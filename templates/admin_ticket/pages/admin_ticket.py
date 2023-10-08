import streamlit as st
import pymongo
from streamlit_extras.switch_page_button import switch_page
import bson

if 'curr_ticket' not in st.session_state:
    st.session_state['curr_ticket']=''


client = pymongo.MongoClient(st.secrets['mongo'])  # Replace with your MongoDB connection string
db = client["support_tickets"]
collection = db["tickets"]

objID = bson.ObjectId(st.session_state['curr_ticket'])

curr_ticket = collection.find_one({'_id': objID})
st.title(curr_ticket["title"])

st.subheader("Status")
statuses = ['Open','Resolved','Pending','N/A']
statuses.remove(curr_ticket['status'])
statuses.insert(0, curr_ticket['status'])
new_status = st.selectbox('Change status', statuses)

    
with st.expander("Details"):
    st.write(curr_ticket['details'])

st.subheader("Activity")
st.write()
prompt = st.chat_input("Enter a response to send to the user")
for speaker in curr_ticket["activity"]:
    if speaker[0]=="user":
        with st.chat_message("user"):
            st.write(speaker[1])
    elif speaker[0]=='assistant':
        with st.chat_message("assistant"):
            st.write(speaker[1])
    else:
        with st.chat_message("admin", avatar='🧑‍💻'):
            st.write(speaker[1])

if new_status!=curr_ticket['status']:
    with st.chat_message("assistant"):
        st.write("Status changed: " + curr_ticket['status'] + ' --> ' + new_status)
    collection.update_one({'_id': objID}, {"$set": {"status": new_status}})
    activity=curr_ticket["activity"]
    activity.append(["assistant", "Status changed: " + curr_ticket['status'] + ' --> ' + new_status])
    collection.update_one({'_id': objID}, {"$set": {"activity": activity}})

if prompt:
    with st.chat_message("admin", avatar='🧑‍💻'):
            st.write(prompt)
    activity=curr_ticket["activity"]
    activity.append(["admin", prompt])
    collection.update_one({'_id': objID}, {"$set": {"activity": activity}})
