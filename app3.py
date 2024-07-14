import pyttsx3
import speech_recognition as sr
from openai import AzureOpenAI
import time

# Initialize Azure OpenAI client
API_KEY = "394c57a3-013f-4ba5-a763-de1f0f3f7bd9"
ENDPOINT = "https://polite-ground-030dc3103.4.azurestaticapps.net/api/v1"
API_VERSION = "2024-02-01"
MODEL_NAME = "gpt-35-turbo"

azure_client = AzureOpenAI(
  azure_endpoint=ENDPOINT,
  api_key=API_KEY,
  api_version=API_VERSION,
)

# Initialize TTS engine
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)

# Initialize speech recognizer
r = sr.Recognizer()

# Essential fields for patient information
required_fields = {
  "Full Name": None,
  "Age": None,
  "Gender": None,
  "Primary reason for the visit": None,
  "Duration of the problem": None,
  "Onset of symptoms": None,
  "Characteristics of symptoms": None,
  "Associated symptoms": None,
  "Current medications": None,
  "Known allergies": None,
  "Chronic illnesses": None,
  "General symptoms": None,
  "Cardiovascular symptoms": None,
  "Respiratory symptoms": None,
  "Gastrointestinal symptoms": None,
  "Neurological symptoms": None
}
system_prompt = "You are an intern in a medical school, responsible for taking an initial report from patients before they consult with the main doctor. Your role is to ask the patient for detailed information, including personal details, the primary reason for the visit, medical history, and any current symptoms."

def speak(text):
  """Speaks the provided text using the initialized engine."""
  try:
      engine.say(text)
      engine.runAndWait()
  except RuntimeError as e:
      if "run loop already started" in str(e):
          engine.stop()
          engine.shutdown()
          engine = pyttsx3.init()
          voices = engine.getProperty("voices")
          engine.setProperty("voice", voices[0].id)
          speak(text)
      else:
          raise e

def speech_recog():
  """Converts speech to text using the microphone."""
  try:
      with sr.Microphone() as source:
          print("Listening...")
          audio_text = r.listen(source, timeout=5, phrase_time_limit=10)
          print("Processing audio...")
          try:
              text = r.recognize_google(audio_text).lower()
              print(f"Recognized text: {text}")
              return text
          except sr.UnknownValueError:
              speak("Sorry, I did not understand that. Please repeat.")
          except sr.RequestError as e:
              print(f"Could not request results; {e}")
  except Exception as e:
      print(f"An error occurred: {e}")
  return None

def ask_question(question):
  """Asks a question to the patient and processes the response."""
  speak(question)
  response = speech_recog()
  return response

def generate_response(conversation_history):
  """Generates a response using Azure OpenAI."""
  messages = [{"role": "system", "content": system_prompt}] + conversation_history

  chat_completion = azure_client.chat.completions.create(
      messages=messages,
      model=MODEL_NAME,
      max_tokens=1000,
      temperature=0.3,
  )

  bot_response = chat_completion.choices[0].message.content.strip()
  return bot_response

def check_missing_fields(conversation_history):
  """Checks which required fields are still missing from the conversation."""
  # Generate a summary of the conversation to check for missing fields
  summary_prompt = "Based on the following conversation history, determine which fields are still missing:\n\n"
  for message in conversation_history:
      role = "User" if message["role"] == "user" else "Bot"
      summary_prompt += f"{role}: {message['content']}\n"
  summary_prompt += "\nMissing fields:"

  # Use Azure OpenAI to analyze the summary
  summary_completion = azure_client.chat.completions.create(
      messages=[{"role": "system", "content": summary_prompt}],
      model=MODEL_NAME,
      max_tokens=200,
      temperature=0.5,
  )

  missing_fields_text = summary_completion.choices[0].message.content.strip()
  missing_fields = missing_fields_text.split(", ")
  return missing_fields

def main():
  conversation_history = []
  

  while True:
      missing_fields = check_missing_fields(conversation_history)
      if not missing_fields:
          break

      for field in missing_fields:
          question = f"Please provide your {field}."
          response = ask_question(question)
          if response:
              conversation_history.append({"role": "user", "content": response})
              gpt_response = generate_response(conversation_history)
              required_fields[field] = response if response else None
              speak(gpt_response)

  speak("Thank you for providing all the necessary information. Your session is now complete.")

if __name__ == "_main_":
  main()

