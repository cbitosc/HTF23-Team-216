import streamlit as st
import pymongo
from streamlit_extras.switch_page_button import switch_page
st.title("All tickets")
client = pymongo.MongoClient(st.secrets['mongo'])  # Replace with your MongoDB connection string
db = client["support_tickets"]
collection = db["tickets"]

if 'user_id' not in st.session_state:
    st.session_state['user_id']=''
    
if "curr_ticket" not in st.session_state:
    st.session_state['curr_ticket']=''

tickets = collection.find({})

if not tickets:
    st.write("No tickets available currently")
else:
    count=1
    grid = st.columns([2,4,3,2])
    with grid[0]:
        st.subheader("S No.")
    with grid[1]:
        st.subheader("Title")
    with grid[2]:
        st.subheader("Status")
    with grid[3]:
        st.subheader("Action")
    for ticket in tickets:
        grid = st.columns([2,4,3,2])
        with grid[0]:
            st.subheader(count)
            count+=1
        with grid[1]:
            st.subheader(ticket["title"])
        with grid[2]:
            if ticket["status"]=="Resolved":
                st.markdown("### :green[%s]" %(ticket["status"]))
            elif ticket["status"]=="Pending":
                st.markdown("### :orange[%s]" %(ticket["status"]))
            elif ticket["status"]=="Open":
                st.markdown("### :blue[%s]" %(ticket["status"]))
            elif ticket["status"]=="N/A":
                st.markdown("### :red[%s]" %(ticket["status"]))
        with grid[3]:
            view_button = st.button("View ticket", key=f"view{count}")
            if view_button:
                st.session_state['curr_ticket'] =str(ticket['_id'])
                switch_page("admin_ticket")
