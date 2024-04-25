import streamlit as st
from google.cloud import firestore

# Function to initialize Firestore client
def get_db():
    db = firestore.Client.from_service_account_json('key.json')
    return db

# Function to check uniqueness of email
def unique_email(email):
    db = get_db()
    duser = db.collection('users')
    check = duser.where('email', '==', email).limit(1).get()
    return len(check) == 1

# Function to check uniqueness of username
def unique_username(username):
    db = get_db()
    duser = db.collection('users')
    check = duser.where('username', '==', username).limit(1).get()
    return len(check) == 1
    
# Main Streamlit application
def signin_page():
    st.title("TO-DO List")
    st.header("Create Account:")

    # Create a form for user signup
    with st.form("signup_form"):
        name = st.text_input("Enter your name")
        username = st.text_input("Enter username")
        email = st.text_input("Enter your email")
        password = st.text_input("Enter the password", type='password')
        age = st.number_input("Enter your Age", step=1, format="%d")

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if len(username) <= 6:
                st.warning('Username must have a minimum of 6 characters', icon="⚠")
            elif len(password) <= 6:
                st.warning('Password must have a minimum of 6 characters', icon="⚠")
            elif unique_username(username):
                st.warning('Username already exists', icon="⚠")
            elif unique_email(email):
                st.warning('Email already exists', icon="⚠")
            else:
                # Initialize Firestore client
                db = get_db()

                # Create a dictionary of user data
                user_data = {
                    "name": name,
                    "username": username,
                    "email": email,
                    "password": password,
                    "age": age
                }

                # Add user data to Firestore collection
                users_ref = db.collection('users')
                users_ref.document(username).set(user_data)

                st.success("Account created successfully!")

# Run the main Streamlit application
if __name__ == "__main__":
    signin_page()