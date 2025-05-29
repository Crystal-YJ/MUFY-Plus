import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyAIsjhTE7qGmijcsPEwUw1IY-MSX7Wj8ro"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"
    if "user_name" not in st.session_state:
        st.session_state.user_name = "User"
    if "custom_color" not in st.session_state:
        st.session_state.custom_color = "#ffffff"

initialize_session_state()

# Sidebar for customization
st.sidebar.title("Settings")

# Theme selection
theme_options = ["Light", "Dark", "Custom"]
selected_theme = st.sidebar.selectbox("Choose Theme", theme_options, index=theme_options.index(st.session_state.theme))
st.session_state.theme = selected_theme

# Apply selected theme
if selected_theme == "Dark":
    st.markdown("<style>body { background-color: #1e1e1e; color: white; }</style>", unsafe_allow_html=True)
elif selected_theme == "Custom":
    custom_color = st.sidebar.color_picker("Pick a background color", st.session_state.custom_color)
    st.session_state.custom_color = custom_color
    st.markdown(f"<style>body {{ background-color: {custom_color}; }}</style>", unsafe_allow_html=True)

# User name input
st.session_state.user_name = st.sidebar.text_input("Enter your name", st.session_state.user_name)

# Main Chatbot UI
st.title(f"Gemini AI Chatbot - Welcome, {st.session_state.user_name}!")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(f"{message['content']}  \n*({message['timestamp']})*")

# Chat input
if prompt := st.chat_input(f"Chat with Gemini"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Display user message
    with st.chat_message("user"):
        st.write(f"{prompt}  \n*({timestamp})*")

    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp})

    # Get Gemini response
    response = model.generate_content(prompt).text.strip("```")  # Strip accidental code block formatting

    # Display assistant response properly
    with st.chat_message("assistant"):
        st.markdown(response)  # Ensures proper text formatting

    # Add assistant response to history
    timestamp_response = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp_response})