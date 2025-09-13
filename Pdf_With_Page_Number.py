import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.docstore.document import Document
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.retrievers import TFIDFRetriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
# from PyPDF2 import PdfReader
from langchain.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq 
import main

def app():
    # Custom CSS for better UI
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
            border-radius: 10px;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border-radius: 20px;
            padding: 0.5rem 2rem;
            border: none;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .upload-section {
            border: 2px dashed #4CAF50;
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem 0;
            background: rgba(74, 175, 80, 0.1);
        }
        .chat-message {
            padding: 1rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stTextInput input {
            border-radius: 20px;
            border: 2px solid #4CAF50;
            padding: 0.5rem 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Enhanced Main Title with Gradient and Multiple Color Layers
    st.markdown(
        """
        <div style='
            text-align: center; 
            padding: 2.5rem;
            background: linear-gradient(135deg, rgba(74, 175, 80, 0.1), rgba(33, 150, 243, 0.1), rgba(156, 39, 176, 0.1));
            border-radius: 15px;
            border: 2px solid rgba(74, 175, 80, 0.3);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
            position: relative;
            overflow: hidden;
        '>
            <div style='
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #4CAF50, #2196F3, #9C27B0);
            '></div>
            <h1 style='
                color: #4CAF50; 
                margin-bottom: 0.5rem;
                font-size: 2.5rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
                background: -webkit-linear-gradient(45deg, #4CAF50, #45a049);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            '>✅ CHAT WITH DOC GPT OSS 20B OFFLINE 📕🌟</h1>
            <div style='
                width: 150px;
                height: 3px;
                background: linear-gradient(90deg, #4CAF50, #2196F3, #9C27B0);
                margin: 1rem auto 0 auto;
                border-radius: 3px;
            '></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []    
    if 'retriever' not in st.session_state:
        st.session_state.retriever = ''     
    if 'processed' not in st.session_state:
        st.session_state.processed = False 
    if 'doc_list' not in st.session_state:
        st.session_state.doc_list = []


    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key='AIzaSyAqw9OFBpgtK0f4EHf3cUtZIk2vGeG4HV4')
    # To open GitHub Copilot Chat:
    # Windows/Linux: Ctrl + Shift + I
    # Mac: Cmd + Shift + I
    llm = main.llm

    # Enhanced Upload Section
    st.markdown("""
        <div class='upload-section'>
            <h2 style='color: #4CAF50; text-align: center;'>📄 Upload Your PDF Files</h2>
        </div>
    """, unsafe_allow_html=True)

    if "pdf_files" not in st.session_state:
        st.session_state.pdf_files = ''
    if 'last_pdf' not in st.session_state:
        st.session_state.last_pdf = ''    

    # Enhanced file uploader
    with st.container():
        pdf_files = st.file_uploader("Drop your PDFs here ✨", type='pdf', accept_multiple_files=True)

    # Processing indicator
    if pdf_files and st.session_state.processed == False:
        with st.spinner('🔄 Processing your PDF... Please wait...'):
            # Handle PDF Uploads
            if pdf_files and st.session_state.processed == False:
                pdf_file_names = [file.name for file in pdf_files]
                select_pdf_file = st.sidebar.radio("📂 Select PDF", pdf_file_names)
                r_splitter = RecursiveCharacterTextSplitter(chunk_size=5000,chunk_overlap=500)

                selected_file = next(file for file in pdf_files if file.name == select_pdf_file)
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(selected_file.read())
                    tmp_path = tmp_file.name
        
        # Use PyPDFLoader instead of PdfReader
                loader = PyPDFLoader(tmp_path)
                pages = loader.load()
        
                for page in pages:
                    page_split = r_splitter.split_text(page.page_content)
                    for sub_split in page_split:
                        metadata = {
                        "source": selected_file.name,
                        "page_number": page.metadata['page']  # This gives you the page number
                    }
                        st.session_state.doc_list.append(Document(
                        page_content=sub_split,
                        metadata=metadata
                    ))
        
        # Clean up temp file
                os.unlink(tmp_path)


                # pdf_reader = PdfReader(selected_file)
                # text = ""
                # for page in pdf_reader.pages:
                #     text += page.extract_text() 

                # page = r_splitter.split_text(text)

                st.session_state.retriever = TFIDFRetriever.from_documents(st.session_state.doc_list)
                st.success(f"✅ PDF '{select_pdf_file}' has been processed successfully!")
                st.session_state.last_pdf = pdf_files
                st.session_state.processed = True
            else:
                st.error("⚠️ Please upload at least one PDF to proceed.")

    def chat(user, chat_history):
        template = ChatPromptTemplate.from_messages([
    ("system",
    """You are an intelligent and helpful AI assistant 🤖. Follow these guidelines carefully:

    1. Answer Generation 📝:
       - Provide detailed, accurate answers from the given context
       - Maintain natural conversation flow using chat history
       - Structure responses with clear paragraphs and bullet points where appropriate
       - Use relevant emojis to make responses engaging
    
    2. Context Analysis 🔍:
       - Thoroughly analyze all provided context
       - Ensure answers are directly relevant to the user's question
       - Include specific details and examples when available
       - If multiple relevant sections exist, combine them coherently
    
    3. Response Format 📋:
       - Start with a clear, direct answer
       - Provide supporting details and explanations
       - Use bullet points for multiple items
       - Keep responses informative but concise
    
    4. Source Citation 📚:
       - At the end of each response, always include:
         "📄 Source: [Document Name]
          📎 Page Number: [Page Number from metadata]"
    
    Current Chat History: {chat_history}
    Document Context: {context}
    """),
    
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

    # Enhanced Chat Section
    st.markdown("""
        <div style='margin-top: 2rem;'>
            <h2 style='color: #4CAF50; text-align: center; padding: 1rem;'>💬 Chat With Your PDF</h2>
            <div style='width: 50px; height: 3px; background: #4CAF50; margin: 0 auto 2rem auto;'></div>
        </div>
    """, unsafe_allow_html=True)

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
    user_input = st.chat_input("💭 Ask anything about your document...")

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

    # Add this right after the initial CSS
    # Sidebar styling
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
            padding: 2rem 1rem;
            border-right: 2px solid #4CAF50;
        }
        .sidebar-title {
            text-align: center;
            color: #4CAF50;
            padding-bottom: 1rem;
            border-bottom: 2px solid #4CAF50;
            margin-bottom: 2rem;
        }
        .model-select {
            margin: 1rem 0;
            padding: 0.5rem;
            border-radius: 10px;
            border: 1px solid #4CAF50;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar Content
    with st.sidebar:
        st.markdown("<div class='sidebar-title'><h2>🤖 Model Settings</h2></div>", unsafe_allow_html=True)
        
        # Model Selection
        st.markdown("### 🔄 Select Model")
        model_option = st.selectbox(
            "",
            ["GPT-OSS-20B (Default)", "Claude 3", "GPT-4", "Gemini Pro", "Llama-2"],
            index=0,
        )

        # Decorative divider
        st.markdown("<hr style='border: 1px solid #4CAF50; margin: 2rem 0;'>", unsafe_allow_html=True)

        # Temperature Control (for display only)
        st.markdown("### 🌡️ Temperature")
        st.slider("", 0.0, 1.0, 0.7, disabled=True)

        # Context Length (for display only)
        st.markdown("### 📏 Context Length")
        st.select_slider(
            "",
            options=["2K", "4K", "8K", "16K", "32K"],
            value="8K",
            disabled=True
        )

        # Action Buttons
        st.markdown("<hr style='border: 1px solid #4CAF50; margin: 2rem 0;'>", unsafe_allow_html=True)
        st.markdown("### 🛠️ Chat Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("🔄 New Chat", disabled=True)
        with col2:
            st.button("🗑️ Clear All", disabled=True)

        # PDF Selection (keep your existing PDF selection code here)
        if pdf_files and st.session_state.processed == False:
            st.markdown("<hr style='border: 1px solid #4CAF50; margin: 2rem 0;'>", unsafe_allow_html=True)
            st.markdown("### 📚 Selected PDFs")
            pdf_file_names = [file.name for file in pdf_files]
            select_pdf_file = st.radio("", pdf_file_names)

if __name__ == "__main__":
    app()
