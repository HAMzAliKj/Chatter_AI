from streamlit_option_menu import option_menu
import streamlit as st
import Pdf_With_Page_Number, check, Website_Chatter
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

api_key = os.getenv("geminiapi")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=api_key)

def main():
    # Page config
    st.set_page_config(page_title="Chatter AI", page_icon="💬", layout="wide")

    # Sidebar with option menu
    with st.sidebar:
        st.markdown(
            """
            <style>
            .sidebar-title {
                text-align: center;
                font-size: 22px;
                font-weight: bold;
                padding: 10px;
                background: rgba(0, 150, 136, 0.3);
                border-radius: 8px;
                margin-bottom: 15px;
                color: black;
            }
            </style>
            <div class="sidebar-title">⚙️ Navigation</div>
            """,
            unsafe_allow_html=True
        )
        selected_app = option_menu(
            'Simple Chat',
            options=[" ", "Youtube Video Chatter", "Chats With URL's", "Chats With Pdf"],
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "white"},
                "icon": {"color": "#02ab21", "font-size": "25px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#02ab21", "color": "white"},
            }
        )

    # Main page styling when no app is selected
    if selected_app == " ":
        st.markdown(
            """
            <style>
            .center-box {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 80vh;
                background: linear-gradient(135deg, rgba(0, 119, 182, 0.8), rgba(2, 170, 176, 0.8));
                border-radius: 25px;
                padding: 50px;
                box-shadow: 0 0 30px rgba(0,0,0,0.4);
            }
            .main-title {
                font-size: 56px;
                font-weight: bold;
                color: white;
                background: rgba(0,0,0,0.3);
                padding: 20px 50px;
                border-radius: 15px;
                margin-bottom: 40px;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
                box-shadow: 0 0 15px rgba(255,255,255,0.2);
            }
            .feature {
                font-size: 22px;
                margin: 12px 0;
                background: rgba(255, 255, 255, 0.9);
                padding: 12px 25px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .feature:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 16px rgba(0,0,0,0.25);
            }
            </style>
            <div class="center-box">
                <div class="main-title">🤖 Chatter AI</div>
                <div class="feature">🎥 Chat with YouTube</div>
                <div class="feature">📄 Chat with PDF</div>
                <div class="feature">🌐 Chat with Website</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif selected_app == "Youtube Video Chatter":
        check.apps()
    elif selected_app == "Chats With URL's":
        Website_Chatter.app()
    elif selected_app == "Chats With Pdf":
        Pdf_With_Page_Number.app()
    else:
        st.write("Please select an app.")

if __name__ == '__main__':
    main()
