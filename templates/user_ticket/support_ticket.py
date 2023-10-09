import streamlit as st 
import pymongo
from streamlit_extras.switch_page_button import switch_page
st.set_page_config('wide')
st.title("Create a ticket")
client = pymongo.MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client["support_tickets"]
collection = db["tickets"]


if "user_id" not in st.session_state:
    st.session_state['user_id']=''

title = st.text_input("Enter the ticket title")
user_id = "123" #can be taken after login
categories = ["Query", "Complaint", "Suggestion", "Other"]
category = st.selectbox("Select the type of ticket", options=categories)
details = st.text_area("Enter the details below")
submit_button = st.button("Submit your ticket")

if submit_button:
    ticket = {"uid": user_id, "title": title, "category": category, "details": details, "status": "Open", "activity": [["assistant", "Hi! Your ticket has been received and we are working on it"]]}
    st.session_state['user_id']=user_id
    collection.insert_one(ticket)
    st.success('''Ticket submitted successfully. An admin will contact you soon.
               View your tickets by clicking on "My Tickets" in the sidebar''')
    
    
    
