import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_community.docstore.document import Document
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.retrievers import TFIDFRetriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from PyPDF2 import PdfReader




def app():

    # Main Title
    st.markdown(
        "<h1 style='text-align: center; color: #4CAF50;'>Chatter AI 🌟</h1>",
        unsafe_allow_html=True,
    )

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []    
    if 'retriever' not in st.session_state:
        st.session_state.retriever = ''     
    if 'processed' not in st.session_state:
        st.session_state.processed = False 


    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key='AIzaSyBT7otzDr-MQ8ZS1JCP4Q0hTxnKHQ2ZDf0')

    st.subheader("📄 **Upload Your PDF Files**")

    if "pdf_files" not in st.session_state:
        st.session_state.pdf_files = ''
    if 'last_pdf' not in st.session_state:
        st.session_state.last_pdf = ''    
    pdf_files = st.file_uploader("Upload Your PDF Files", type='pdf', accept_multiple_files=True)

    if pdf_files and pdf_files != st.session_state.last_pdf:
        st.session_state.chat_history = []
        st.session_state.retriever = ''
        st.session_state.pdf_files = ''
        st.session_state.last_pdf = ''
        st.session_state.processed = False


    # Handle PDF Uploads
    if pdf_files and st.session_state.processed == False:
        pdf_file_names = [file.name for file in pdf_files]
        select_pdf_file = st.sidebar.radio("📂 Select PDF", pdf_file_names)

        selected_file = next(file for file in pdf_files if file.name == select_pdf_file)

        pdf_reader = PdfReader(selected_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        r_splitter = RecursiveCharacterTextSplitter(chunk_size=5000,chunk_overlap=500)
        page = r_splitter.split_text(text)
        st.session_state.retriever = TFIDFRetriever.from_texts(page)
        st.success(f"✅ PDF '{select_pdf_file}' has been processed successfully!")
        st.session_state.last_pdf = pdf_files
        st.session_state.processed = True
    else:
        st.error("⚠️ Please upload at least one PDF to proceed.")

    def chat(user, chat_history):
        template = ChatPromptTemplate.from_messages([
            ("system",
            """You are a helpful  Chat assistant. Follow these rules:
            Give Me The Answer Of My Question From Given Context 
            See All Context And Give Relevant Answer 
            Properly see in which context the answer there and give 

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

    # Chat Section
    st.subheader("💬 **Chat With Your PDF**")
    try:
        for message in st.session_state.chat_history:
            if isinstance(message, HumanMessage):  # Check if the message is from the user
                with st.chat_message("user",avatar='🤖'):
                    st.markdown(message.content)
            else:  
                with st.chat_message("assistant",avatar='🌐'):
                    st.markdown(message.content)
    except:
        pass
    # User input
    user_input = st.chat_input("Enter Your Message:")

    # Update chat history when user inputs a message
    if user_input:
        # Append user message to chat history
        st.session_state.chat_history.append(HumanMessage(user_input))
        with st.chat_message("user",avatar='🤖'):
            st.markdown(user_input)

        # Simulate assistant response
        if st.session_state.get("retriever", None):  # Replace with your condition
            with st.chat_message("assistant",avatar='🌐'):
                with st.spinner("Generation Response ..."):
                    res = chat(user_input, st.session_state.chat_history)
                    st.markdown(res)
            st.session_state.chat_history.append(AIMessage(res))
        else:
            st.error("⚠️ Please upload a valid PDF file to start the chat.")

app()