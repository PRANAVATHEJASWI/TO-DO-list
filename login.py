import streamlit as st
from google.cloud import firestore
from datetime import datetime

# Function to initialize Firestore client
def get_db():
    db = firestore.Client.from_service_account_json('key.json')
    return db

def authenticate(username, password):
    db = get_db()
    auser = db.collection('users')
    query = auser.where('username', '==', username).limit(1).get()
    if len(query) == 0:
        return False
    user_doc = query[0]
    user_data = user_doc.to_dict()
    return user_data.get('password') == password

def add_task(username, new_task, task_date, task_time):
    # Initialize Firestore client
    db = get_db()

    # Get reference to the user's document
    user_ref = db.collection('Task').document(username)

    # Retrieve the user's document
    user_doc = user_ref.get()

    if user_doc.exists:
        # If user document exists, retrieve current tasks array or initialize an empty array
        current_tasks = user_doc.to_dict().get('tasks', [])
    else:
        # If user document does not exist, initialize an empty tasks array
        current_tasks = []

    # Combine date and time to create datetime object for the new task
    task_datetime = datetime.combine(task_date, task_time)

    # Prepare new task data dictionary
    new_task_data = {
        'task_description': new_task,
        'datetime': task_datetime
    }

    # Append the new task data to the tasks array
    current_tasks.append(new_task_data)

    # Update the user's document with the updated tasks array and username
    user_ref.set({'tasks': current_tasks, 'username': username})

    st.success("Task added successfully!")

def delete_task(username, task_description):
    # Initialize Firestore client
    db = get_db()

    # Get reference to the user's document
    user_ref = db.collection('Task').document(username)

    # Retrieve the user's document
    user_doc = user_ref.get()

    if user_doc.exists:
        # If user document exists, retrieve current tasks array
        current_tasks = user_doc.to_dict().get('tasks', [])

        # Filter out the task to be deleted
        updated_tasks = [task for task in current_tasks if task['task_description'] != task_description]

        # Update the user's document with the updated tasks array
        user_ref.update({'tasks': updated_tasks})

        st.success("Task deleted successfully!")

import streamlit as st
from google.cloud import firestore
from datetime import datetime

# Function to initialize Firestore client
def get_db():
    db = firestore.Client.from_service_account_json('key.json')
    return db

def modify_task(username, task_description, new_description, new_datetime):
    # Initialize Firestore client
    db = get_db()

    # Get reference to the user's document
    user_ref = db.collection('Task').document(username)

    # Retrieve the user's document
    user_doc = user_ref.get()

    if user_doc.exists:
        # If user document exists, retrieve current tasks array
        current_tasks = user_doc.to_dict().get('tasks', [])

        # Flag to track if the task was found and modified
        task_found = False

        # Find the task to be modified
        for task in current_tasks:
            if task['task_description'] == task_description:
                # Update task description
                task['task_description'] = new_description

                # Check if new_datetime is provided and update task datetime
                if new_datetime:
                    # Convert new_datetime to datetime object
                    new_datetime = datetime.combine(new_datetime, datetime.min.time())
                    task['datetime'] = new_datetime

                # Task found and modified
                task_found = True
                break

        if task_found:
            # Update the user's document with the modified tasks array
            user_ref.update({'tasks': current_tasks})
            st.success("Task modified successfully!")
        else:
            st.warning(f"Task '{task_description}' not found for user '{username}'.")
    
def display_tasks(username):
    # Initialize Firestore client
    db = get_db()

    # Get reference to the user's document
    user_ref = db.collection('Task').document(username)

    # Retrieve the user's document
    user_doc = user_ref.get()

    if user_doc.exists:
        # If user document exists, retrieve tasks array and display tasks
        tasks = user_doc.to_dict().get('tasks', [])
        st.header(f"Tasks for {username}")
        if tasks:
            for task in tasks:
                # Display task description and input fields for modifying the task
                task_description = task['task_description']
                task_datetime = task['datetime']

                st.write(f"- {task_description} (Due: {task_datetime})")

                # Use columns to display buttons side by side
                col1, col2 = st.columns([1, 1])

                # Modify button
                if col1.button(f"✏ Modify '{task_description}'"):
                    new_description = st.text_input("New description", value=task_description)
                    new_datetime = st.date_input("New due date", value=task_datetime)
                    if st.button("✓"):
                        modify_task(username, task_description, new_description, new_datetime)

                # Delete button
                if col2.button(f"🗑 Delete '{task_description}'"):
                    delete_task(username, task_description)
                    # Refresh the task list after deletion
                    st.experimental_rerun()

                st.write("")  # Empty line for spacing
        else:
            st.write("No tasks found.")


def login_page():
    # Check if the user is already logged in
    if st.session_state.get('logged_in', False):
        username = st.session_state.username
        st.write(f"Welcome, {username}!")
        st.header("Add a Task")
        new_task = st.text_input("Enter a new task")
        task_date = st.date_input("Select task date", min_value=datetime.today())
        task_time = st.time_input("Select task time")
        
        if st.button("Add Task"):
            if new_task:
                add_task(username, new_task, task_date, task_time)
            else:
                st.warning("Task description cannot be empty.")
        
        display_tasks(username)
        return
    
    # Display login form if user is not logged in
    st.title("TO-DO List")
    st.header("Login")

    with st.form("login_form"):
        username = st.text_input("Enter your username")
        password = st.text_input("Enter the password", type='password')

        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if authenticate(username, password):
                # Store logged-in user's information in session state
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
            else:
                st.warning("Incorrect username or password")

if __name__ == "__main__":
    login_page()
