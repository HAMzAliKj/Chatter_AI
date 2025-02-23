from youtube_transcript_api import YouTubeTranscriptApi as yt
from youtube_transcript_api._errors import NoTranscriptFound
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.docstore.document import Document
from langchain_community.retrievers import TFIDFRetriever
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import requests


def apps():
    # Backend URL (replace with your Render backend URL)
    BACKEND_URL = "https://web-production-4212.up.railway.app/transcript"

    def fetch_transcript(video_id):
        try:
            # Call the backend to fetch the transcript
            response = requests.get(BACKEND_URL, params={"video_id": video_id})
            if response.status_code == 200:
                return response.json()  # Return the transcript
            else:
                st.error(f"Failed to fetch transcript: {response.json().get('error')}")
                return None
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")
            return None

    # Initialize Langchain LLM with API key
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key='AIzaSyBT7otzDr-MQ8ZS1JCP4Q0hTxnKHQ2ZDf0')

    # Initialize session state variables
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'transcript' not in st.session_state:
        st.session_state.transcript = ''
    if "video_url" not in st.session_state:
        st.session_state.video_url = ''
    if "last_url" not in st.session_state:
        st.session_state.last_url = ''
    if "summary_generated" not in st.session_state:
        st.session_state.summary_generated = False     
    if 'retriever' not in st.session_state:
        st.session_state.retriever = ''     
    if 'processed' not in st.session_state:
        st.session_state.processed = False    

    # Function to convert seconds to [HH:MM:SS] format
    def seconds_to_timestamp(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"[{hours:02}:{minutes:02}:{secs:02}]"

    # Streamlit app
    st.title("YouTube Video Chatter")

    # Input for YouTube video URL
    full_video_url = st.text_input("Enter Your YouTube Video URL")

    if full_video_url and full_video_url != st.session_state.last_url:
        st.session_state.video_url = full_video_url
        st.session_state.last_url = ''
        st.session_state.chat_history = []
        st.session_state.transcript = ''
        st.session_state.retriever = ''
        st.session_state.summary_generated = False
        st.session_state.processed = False

    if full_video_url:
        # Extract video ID using LLM
        video_id = llm.invoke(f"Give me the ID of this URL, just the ID and nothing else: {full_video_url}").content
        st.success("Video URL is correct. Please wait..")
        st.session_state.video_id = video_id

        if video_id:
            # Fetch transcript from the backend
            transcript = fetch_transcript(video_id)
            if transcript:
                st.session_state.transcript = transcript
                st.session_state.last_url = full_video_url

                # Process transcript
                context = ''
                for con in st.session_state.transcript:
                    text = con['text']
                    start = con['start']
                    context += text + seconds_to_timestamp(start)

                doc_store = [Document(page_content=context)]
                r_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=800)
                page = r_splitter.split_documents(doc_store)
                st.session_state.retriever = TFIDFRetriever.from_documents(page)
                st.session_state.processed = True
            else:
                st.error("Failed to fetch transcript.")

    if not st.session_state.summary_generated:
        button = st.button("Summary")
        if button:
            summary = llm.invoke(f"Generate a summary of this video context, add emojis, and write in bullet points: {context}").content
            st.write(summary)
            st.session_state.summary_generated = True

    # Chat function
    def chat(user, chat_history):
        template = ChatPromptTemplate.from_messages([
            ("system",
            """You are a helpful YouTube video assistant. Follow these rules:
            1. FIRST check chat history for answers to non-video questions
            2. Use video context ONLY when explicitly asked about content
            3. For rewrite/simplify requests, use previous answers from history
            4. Maintain natural conversation flow
            5. Always include relevant timestamps in [HH:MM:SS] format

            Current Chat History: {chat_history}
            Video Context: {context}"""),

            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        retriever_prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            ("human", "Given the above conversation, generate the search query to get relevant information.")
        ])

        history_aware = create_history_aware_retriever(
            llm=llm,
            prompt=retriever_prompt,
            retriever=st.session_state.retriever
        )

        chain = create_stuff_documents_chain(llm, template)
        result = create_retrieval_chain(history_aware, chain)
        answerb = result.invoke({"input": user, "chat_history": chat_history})
        return answerb['answer']

    try:
        for message in st.session_state.chat_history:
            if isinstance(message, HumanMessage):
                with st.chat_message('user'):
                    st.markdown(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message('assistant'):
                    st.markdown(message.content)

        # User input
        user = st.chat_input("How can I help you?")
        if user:
            st.session_state.chat_history.append(HumanMessage(user))
            with st.chat_message('user'):
                st.markdown(user)
            with st.chat_message('assistant'):
                try:
                    res = chat(user, st.session_state.chat_history)
                    st.markdown(res)
                    st.session_state.chat_history.append(AIMessage(res))
                except Exception as e:
                    st.error(f"Error generating response: {e}")

    except Exception as e:
        st.write(f"Error: {e}")

if __name__ == "__main__":
    apps()
