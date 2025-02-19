
import streamlit as st
from streamlit_option_menu import option_menu
import check
import Website_Chatter
import Pdf_With_Page_Number
import time


class Main():
    def run():
        with st.sidebar:
            app = option_menu(
                'Simple Chat',
                options=('Youtube Video Chatter', "Chats With URL's", "Chats With Pdf"),
                styles={
                    "container": {"padding": "5!important", "background-color": "white"},
                    "icon": {"color": "white", "font-size": "25px",'font-Weight':'200'}, 
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )

        try:
            time.sleep(5)

            if  app == "Youtube Video Chatter":
                check.app()
            elif  app == "Chats With URL's":
                Website_Chatter.app()
            elif  app == "Chats With Pdf":
                Pdf_With_Page_Number.app()
            else:
                st.write("Please Select System")   
        except Exception as e:
               st.write(e)

    run()         