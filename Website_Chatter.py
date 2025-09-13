import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import TFIDFRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from operator import itemgetter
from firecrawl import FirecrawlApp
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import main

load_dotenv()
import os


firecrawlapi = os.getenv("firecrawl")
groqapi = os.getenv("groqapi")

def app():
    st.title("Chat With Website URLs")

    if "last_processed_url" not in st.session_state:
        st.session_state.last_processed_url = None
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if 'summary' not in st.session_state:
        st.session_state.summary = False
    if "processed" not in st.session_state:
        st.session_state.processed = False   

    url = st.text_input("Enter Website Url To Chat")


    llm = main.llm

    if url and url != st.session_state.last_processed_url:
        st.session_state.retriever = ""
        st.session_state.chat_history = []
        st.session_state.summary = False
        st.session_state.processed = False

    if url and st.session_state.processed == False:
        st.write("LLM Initialized")
        website_url = url
        st.session_state.appi_key = firecrawlapi
        st.session_state.app = FirecrawlApp(api_key=st.session_state.appi_key)

        try:
            scrape_status = st.session_state.app.scrape_url(website_url)
            st.session_state.context = ""
            st.session_state.context = scrape_status.markdown

            r_splitter = RecursiveCharacterTextSplitter(chunk_size=50000, chunk_overlap=1500)
            pages = r_splitter.split_text(st.session_state.context)
            st.session_state.retriever = TFIDFRetriever.from_texts(pages)
            st.session_state.last_processed_url = url
            st.session_state.processed = True
            st.success("Website processed successfully. Start chatting!")
        except Exception as e:
            st.error(f"Error processing URL: {e}")
    else:
        pass

    # Function to generate a response
    def response(query, chat_history):
        template = ChatPromptTemplate.from_messages([
            ('system', """You Are Helpful Assistant Give Answer Of My Question From Given Context Give Accurate Answer And Also Use Previous Chat History To Maintain Natural Conversation Between User And You 
            Context : {context}
            chat_history : {chat_history}"""),
            (MessagesPlaceholder(variable_name='chat_history')),
            ('human', '{input}')
        ])
        
        retriever_prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name='chat_history'),
            ('human', '{input}'),
            ('human', 'Given The Above Conversation Generate Search Query To Look In Order To Get Relevant Information to conversation')
        ])

        st.session_state.history_aware = create_history_aware_retriever(
            llm,
            retriever=st.session_state.retriever,
            prompt=retriever_prompt
        )

        chains = create_stuff_documents_chain(llm, template)
        result = create_retrieval_chain(
            st.session_state.history_aware,
            chains
        )
        answerb = result.invoke({"input": query, "chat_history": chat_history})
        return answerb['answer']

    # Display chat history without altering its format
    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message('user'):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message('assistant'):
                st.markdown(message.content)

    if st.session_state.summary == False:
        try:
            button = st.button("Summary")
            if button:
                response = llm.invoke(f"Generate Summary of This long of all and write in beautiful way like include emoji not to long and not too short just normal and also some in points and good and easy to understand  {st.session_state.context}")
                st.success("Summary generation completed!")
                st.markdown(response.content)
                st.session_state.summary = True
        except Exception as e:
            st.markdown(f"Error: {e}")

    user_input = st.chat_input("Enter Your Message")

    if user_input:
        st.session_state.chat_history.append(HumanMessage(user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            try:
                res = response(user_input, st.session_state.chat_history)
                st.markdown(res)
                st.session_state.chat_history.append(AIMessage(res))
            except Exception as e:
                st.error(f"Error generating response: {e}")

if __name__ == "__main__":
    app()
