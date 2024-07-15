import streamlit as st
import os
import speech_recognition as sr
from openai import AzureOpenAI
from pydub import AudioSegment
import librosa
import io
import pyttsx3
from streamlit_mic_recorder import mic_recorder
import base64


API_KEY=st.secrets["OPENAI_API_KEY"]
ENDPOINT = "https://polite-ground-030dc3103.4.azurestaticapps.net/api/v1"
API_VERSION = "2024-02-01"
MODEL_NAME = "gpt-35-turbo"


azure_client = AzureOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=API_KEY,
    api_version=API_VERSION,
)

# System prompt to set the context
system_prompt = """
You are a mental health counselor. Your role is to engage in a therapeutic session with me, similar to how a psychologist or counselor would. Initiate the conversation and encourage me to express my emotions in detail. Provide solutions to my concerns and, if asked, offer diagnoses and treatment options. This can be a long session, so feel free to delve into greater detail and explore various aspects of my mental health.
"""

# Variable to store conversation history
conversation_history = []

def convert_bytes_to_array(audio_bytes):
    audio_bytes = io.BytesIO(audio_bytes)
    audio, sample_rate = librosa.load(audio_bytes)
    print(sample_rate)
    return audio




def generate_response(user_input):

    if not st.session_state.conversation_history and user_input is None:
        initial_greeting = "Hello, I'm here to help you. How have you been feeling lately?"
        st.session_state.conversation_history.append({
            "role":
            "assistant",
            "content":
            initial_greeting
        })
        

    # Update conversation history with the new user input
    if user_input:
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })

    # Prepare the messages for the API call
    messages = [{
        "role": "system",
        "content": system_prompt
    }] + st.session_state.conversation_history

    # Create a chat completion
    chat_completion = azure_client.chat.completions.create(
        messages=messages,
        model=MODEL_NAME,
        max_tokens=1000,
        temperature=0.3,
    )

    # Extract the bot's response
    bot_response = chat_completion.choices[0].message.content.strip()

    # Update conversation history with the bot's response
    st.session_state.conversation_history.append({
        "role": "assistant",
        "content": bot_response
    })

    

    return bot_response

def play_audio(file_path):
    audio_file = open(file_path, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')



def generate_summary(conversation_history):
    summary_prompt = "Please summarize the following conversation history:\n\n"
    for message in conversation_history:
        role = "User" if message["role"] == "user" else "Bot"
        summary_prompt += f"{role}: {message['content']}\n"
    summary_prompt += "\nSummary:"

    # Use azure_client for generating summary
    summary_completion = azure_client.chat.completions.create(
        messages=[{"role": "system", "content": summary_prompt}],
        model=MODEL_NAME,
        max_tokens=200,
        temperature=0.5,
    )
    summary = summary_completion.choices[0].message['content'].strip()
    return summary

def save_summary(summary):
    with open("conversation_summary.txt", "w") as file:
        file.write(summary)



def speech_recog():
    try:
        with sr.Microphone() as source:
            print("Listening")
            audio_text = r.listen(source, timeout = 3, phrase_time_limit = 5)
            print("Done")
            print(audio_text)
            
            try:
                text = r.recognize_google(audio_text).lower()
                print(text)
                return text
            except sr.UnknownValueError:
                speak("Sorry, I did not understand that" )
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))
    except Exception as e:
        print(f"An error occurred: {e}")



def get_image_as_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

# for voice recognition
r = sr.Recognizer()



def generate_summary(conversation_history):
    summary_prompt = "Please summarize the following conversation history:\n\n"
    for message in conversation_history:
        role = "User" if message["role"] == "user" else "Bot"
        summary_prompt += f"{role}: {message['content']}\n"
    summary_prompt += "\nSummary:"

    # Use azure_client for generating summary
    summary_completion = azure_client.chat.completions.create(
        messages=[{
            "role": "system",
            "content": summary_prompt
        }],
        model=MODEL_NAME,
        max_tokens=200,
        temperature=0.5,
    )
    summary = summary_completion.choices[0].message.content.strip()
    return summary



def save_summary(summary):
    with open("conversation_summary.txt", "w") as file:
        file.write(summary)


def main():

        
    def speak(text):
        """Speaks the provided text using the initialized engine."""

        engine = pyttsx3.init(driverName='sapi5')  # Specify the driver name explicitly
        voices = engine.getProperty("voices")
        engine.setProperty("voice", voices[0].id)
        try:
            engine.say(text)
            engine.runAndWait()
        except RuntimeError as e:
            if "run loop already started" in str(e):
            # Handle potential engine restart if needed
                    print("Engine restart required due to loop error.")
                    engine.stop()
                    engine.shutdown()
                    engine = pyttsx3.init()
                    voices = engine.getProperty("voices")
                    engine.setProperty("voice", voices[0].id)
                    speak(text)  # Retry speaking the text
            else:
                    raise e  # Raise other RuntimeError exceptions


    st.markdown("<h1 style='text-align: center;'>Mental Health Chatbot</h1>", unsafe_allow_html=True)
    # intro_message = "I am Ai heath chatBot train to solve issue releated to heath"
    # speak(intro_message)

    # Streamlit app
    if 'record' not in st.session_state:
        st.session_state.record = False

    if 'session' not in st.session_state:
        st.session_state.session = False

    if 'session_end' not in st.session_state:
        st.session_state.session_end = False

    if 'session_start' not in st.session_state:
        st.session_state.session_start = True
    # Initialize session state variables
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []  
    if "audio_counter" not in st.session_state:
        st.session_state.audio_counter = 0    


    intro_message = "Remember to tap spacebar before you say any voice commands. To upload a file say UPLOAD, to start say START, to translate to a different language say TRANSLATE, to summarize say SUMMARISE, to ask questions say QUESTION, to quiz yourself say QUIZ, to change the playback speed say FAST, MEDIUM, or SLOW. "
    # speak(intro_message,engine)

    st.markdown("""
        <style>
            .stApp {
                background-color: rgba(33,33,33,255);
            }
            .user-message, .bot-message {
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 10px;
                color:white
            }
            .user-message {
                background-color: #0d0d0d;
                text-align: left;
            }
            .bot-message {
                background-color: #2f2f2f;
                text-align: left;
            }
            .message-container {
                display: flex;
                align-items: flex-start;
                margin-bottom: 10px;
            }
            .message-icon {
                width: 40px;
                height: 40px;
                margin-right: 10px;
            }
            .stButton {
                color: white;
                border: none;
                border-radius: 4px;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                cursor: pointer;
            }


                    .stApp {
                        background-color: rgba(33,33,33,255);
                        border: 2px solid #555;
                        border-radius: 10px;
                        padding: 20px;
                        width: 80vw;
                        margin: 20px auto; /* Center align and add space around */   
                        margin-top:4rem;
                    }
                    .stButton {
                        color: white;
                        border: none;
                        border-radius: 4px;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        cursor: pointer;
                        margin-top: 10px; /* Increase vertical gap */
                        margin-bottom: 10px; /* Increase vertical gap */
                    }

                    .navbar {
                        background-color: #333;
                        padding: 10px 0;
                        text-align: center;
                        margin-bottom: 20px;
                        border-bottom: 2px solid #555;
                    }
                    .navbar-title {
                        color: white;
                        font-size: 24px;
                        font-weight: bold;
                    }

            .scrollable-conversation {
                max-height: 400px;
                overflow-y: auto;
                padding-right: 20px; /* Add padding to keep scrollbar visible */
            }

        </style>
    """,
                unsafe_allow_html=True)

    st.markdown("""
            <style>
                .record-button {
                    background-color: #4CAF50; /* Green */
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 10px;
                }
                .record-button:hover {
                    background-color: #45a049;
                }
            </style>
        """,
                    unsafe_allow_html=True)

    if st.session_state.session_start:
            if st.button("🎙️Ask question"):
            # if st.markdown("<div style='text-align: center;'><button style='background-color: #0e1117; color: white; border: none; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;' onclick='window.location.reload();'> 🎙️Ask question</button></div>", unsafe_allow_html=True):
                question = speech_recog()
                response = generate_response(question)
                speak(response)
                st.write(response)

            if "conversation_history" in st.session_state and st.session_state.conversation_history:

                if st.button("End Conversation"):
                    st.session_state.session_end = True
                    st.session_state.session = False
                    st.session_state.session_start = False
                    st.experimental_rerun()  
                

                st.subheader("Conversation History")

                user_icon_b64 = get_image_as_base64("image/user-icon.png")
                bot_icon_b64 = get_image_as_base64("image/bot-icon.png")

                st.markdown('<div class="scrollable-conversation">', unsafe_allow_html=True)

                for message in st.session_state.conversation_history:
                    role = "User" if message["role"] == "user" else "Bot"
                    icon = user_icon_b64 if role == "User" else bot_icon_b64
                    message_class = "user-message" if role == "User" else "bot-message"
                    st.markdown(f"""
                        <div class="message-container">
                            <img src="data:image/png;base64,{icon}" class="message-icon">
                            <div class="{message_class}">
                                <strong>{role}:</strong> {message['content']}
                            </div>
                        </div>
                    """,
                                unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True) 


    if st.session_state.session_end:
        summary = generate_summary(st.session_state.conversation_history)
        st.write("Summary:")
        st.write(summary)
        save_summary(summary)
        st.write("Conversation ended. Thank you!")        
                

if __name__ == '__main__':
    main()

