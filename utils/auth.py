import streamlit as st

def login():
    st.title("MTE Calculator Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Invalid credentials")

def check_login():
    if "logged_in" not in st.session_state:
        login()
        st.stop()
