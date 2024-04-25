import streamlit as st

from login import login_page
from signin import signin_page

def main():
    st.sidebar.title("Welcome !")
    selected = st.sidebar.radio(
        "Menu:",
        ("Login", "Create Account"),
        index=0
    )

    if selected == "Login":
        login_page()
                
    elif selected == "Create Account":
        signin_page()

if __name__ == "__main__":
    main()
