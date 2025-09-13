import http
from youtube_transcript_api import YouTubeTranscriptApi 
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.docstore.document import Document
from langchain_community.retrievers import TFIDFRetriever
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import main
from urllib.parse import urlparse, parse_qs



def apps():
    # Initialize Langchain LLM
    llm = main.llm

    # Initialize session state variables
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'transcript' not in st.session_state:
        st.session_state.transcript = []
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

    def extract_youtube_id(url: str) -> str | None:
        """
        Extract the YouTube video ID from a given URL.
        Returns None if no valid video ID is found.
        """
        parsed = urlparse(url)
        
        # Case 1: youtu.be/<id>
        if parsed.netloc in ("youtu.be", "www.youtu.be"):
            return parsed.path.lstrip("/")
        
        # Case 2: youtube.com/watch?v=<id>
        if parsed.netloc in ("youtube.com", "www.youtube.com", "m.youtube.com"):
            if parsed.path == "/watch":
                query = parse_qs(parsed.query)
                return query.get("v", [None])[0]
            
            # Case 3: youtube.com/embed/<id> or /v/<id>
            if parsed.path.startswith(("/embed/", "/v/")):
                return parsed.path.split("/")[2]
        
        return None     


    # Function to fetch transcript directly (no backend)
    def fetch_transcript(video_id):
        try:
            import http.client

            conn = http.client.HTTPSConnection("youtube-transcript3.p.rapidapi.com")

            headers = {
                'x-rapidapi-key': "e46295bd9fmsh010d3937189881dp130561jsn30c7d5cfe573",
                'x-rapidapi-host': "youtube-transcript3.p.rapidapi.com"
            }

            conn.request("GET", f"/api/transcript?videoId={video_id}", headers=headers)

            res = conn.getresponse()
            data = res.read()

            st.session_state.transcript = data.decode("utf-8")
            return st.session_state.transcript
        except Exception as e:          
            st.error(f"Error fetching transcript: {e}")
            return None
    # Streamlit app
    st.title("YouTube Video Chatter")

    # Input for YouTube video URL
    full_video_url = st.text_input("Enter Your YouTube Video URL")

    if full_video_url and full_video_url != st.session_state.last_url:
        st.session_state.video_url = full_video_url
        st.session_state.last_url = ''
        st.session_state.chat_history = []
        st.session_state.transcript = []
        st.session_state.retriever = ''
        st.session_state.summary_generated = False
        st.session_state.processed = False

    if full_video_url:
        # Extract video ID using LLM
        video_id  = extract_youtube_id(full_video_url)
         # Extract video ID using LLM
        st.success("Video URL is correct. Please wait..")
        st.session_state.video_id = video_id

        if video_id:
            # Fetch transcript directly
            transcript = fetch_transcript(video_id)
            if transcript:
                st.session_state.transcript = transcript
                st.session_state.last_url = full_video_url

                # Process transcript
                context = st.session_state.transcript
                
                doc_store = [Document(page_content=context)]
                r_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=800)
                page = r_splitter.split_documents(doc_store)
                st.session_state.retriever = TFIDFRetriever.from_documents(page)
                st.session_state.processed = True
            else:
                st.error("Failed to fetch transcript.")

    if not st.session_state.summary_generated and st.session_state.processed:
        if st.button("Summary"):
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

    # Display chat history
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

if __name__ == "__main__":
    apps()
