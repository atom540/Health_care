# app.py

import streamlit as st
from app import main as voice_chat
from app2 import main as report_evalution

# Set page title
# st.title('Mental Health Support Chatbot')

# Create left sidebar navigation with a list
option = st.sidebar.radio(
    'Navigation',
    ['User Inputs', 'Lab Report']
)   

# Render selected page based on user's choice
if option == 'User Inputs':
    voice_chat()
elif option == 'Lab Report':
    report_evalution()