from streamlit_option_menu import option_menu
import streamlit as st
import Pdf_With_Page_Number, check, Website_Chatter

def main():

    # Create sidebar with option menu and store selection in a local variable.
    with st.sidebar:
        selected_app = option_menu(
            'Simple Chat',
            options=["Youtube Video Chatter", "Chats With URL's", "Chats With Pdf"],
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "white"},
                "icon": {"color": "white", "font-size": "25px", "font-weight": "200"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#02ab21"},
            }
            
        )
        
    
    if selected_app == "Youtube Video Chatter":
        check.apps()
    elif selected_app == "Chats With URL's":
        Website_Chatter.app()
    elif selected_app == "Chats With Pdf":
        Pdf_With_Page_Number.app()
    else:
        st.write("Please select an app.")

if __name__ == '__main__':
    main()
