import streamlit as st
import openai
from openai import AzureOpenAI

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter

import tempfile

API_KEY=st.secrets["OPENAI_API_KEY"]
ENDPOINT = "https://polite-ground-030dc3103.4.azurestaticapps.net/api/v1"
API_VERSION = "2024-02-01"
MODEL_NAME = "gpt-35-turbo"

# Initialize the Azure OpenAI client
azure_client = AzureOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=API_KEY,
    api_version=API_VERSION,
)

# Function to summarize the medical report
def summarize_report(text):
    summary_prompt = "Please summarize the following medical report:\n\n" + text
    summary_completion = azure_client.chat.completions.create(
        messages=[{"role": "system", "content": summary_prompt}],
        model=MODEL_NAME,
        max_tokens=300,
        temperature=0.3,
    )
    summary = summary_completion.choices[0].message.content.strip()
    return summary



def get_answer(context, query):
    prompt = f"Based on the following medical report, answer the question:\n\nContext:\n{context}\n\nQuestion:\n{query}\n\nAnswer:"
    
    # Call the Azure OpenAI API to get the answer
    response = azure_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on medical report context."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.3,
    )
    
    # Extract the answer from the response
    answer = response.choices[0].message.content.strip()
    return answer

def main():
    # Title of the Streamlit app
    st.title("Medical Report Summarizer and Q&A")

    # File uploader for the medical report
    uploaded_file = st.file_uploader("Choose a medical report file", type=["txt", "pdf"])

    if uploaded_file is not None:
        # Create a temporary file to store the uploaded PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(uploaded_file.read())
        
        document_path = temp_file.name  # Use the temp file path
        
        # Load and split the PDF document
        loader = PyPDFLoader(document_path)
        documents = loader.load_and_split()

        # Split the text into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1200, chunk_overlap=25)
        docs = text_splitter.split_documents(documents)
        combined_text = "\n".join([doc.page_content for doc in docs])
        # st.write(combined_text)
        # Summarize the report
        summary = summarize_report(combined_text)
        st.subheader("Summary")
        st.write(summary)
        
        
        
        # User input for asking questions
        question = st.text_input("Ask a question about the medical report:")
        
        # Create a clear button to reset the question input and remove the answer
        if st.button("Clear"):
            question = ""  # Reset the question input
            st.text_input("Ask a question about the medical report:", value=question, key="question_input")
        
        if question:
            # Get the answer to the question
            answer = get_answer(combined_text, question)
            st.subheader("Answer")
            st.write(answer)
        else:
            st.write("Please enter a question to get an answer.")

if __name__ == '__main__':
    main()

          
