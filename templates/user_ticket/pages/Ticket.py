import streamlit as st
import pymongo
from streamlit_extras.switch_page_button import switch_page
import bson

if 'curr_ticket' not in st.session_state:
    st.session_state['curr_ticket']=''


client = pymongo.MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client["support_tickets"]
collection = db["tickets"]

objID = bson.ObjectId(st.session_state['curr_ticket'])

curr_ticket = collection.find_one({'_id': objID})
st.title(curr_ticket["title"])

st.subheader("Status")
if curr_ticket["status"]=="Resolved":
    st.markdown("### :green[%s]" %(curr_ticket["status"]))
elif curr_ticket["status"]=="Pending":
    st.markdown("### :orange[%s]" %(curr_ticket["status"]))
elif curr_ticket["status"]=="Open":
    st.markdown("### :blue[%s]" %(curr_ticket["status"]))
elif curr_ticket["status"]=="N/A":
    st.markdown("### :red[%s]" %(curr_ticket["status"]))

with st.expander("Details"):
    st.write(curr_ticket['details'])

st.subheader("Activity")
st.write()
prompt = st.chat_input("Enter a response to send to the admin")
for speaker in curr_ticket["activity"]:
    if speaker[0]=="user":
        with st.chat_message("user"):
            st.write(speaker[1])
    else:
        with st.chat_message("assistant"):
            st.write(speaker[1])


if prompt:
    with st.chat_message("user"):
            st.write(prompt)
    activity=curr_ticket["activity"]
    activity.append(["user", prompt])
    collection.update_one({'_id': objID}, {"$set": {"activity": activity}})