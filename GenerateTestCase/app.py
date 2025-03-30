import os
import json
from dotenv import load_dotenv
import streamlit as st
import random
import string
import subprocess
from datetime import datetime
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import re


load_dotenv()
# API Key
GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"

# GitHub Configuration
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_REPO = os.getenv("GITHUB_REPO")
PAT_TOKEN = os.getenv("PAT_TOKEN")
FILE_PATH_IN_REPO = os.getenv("FILE_PATH_IN_REPO")

# Streamlit configuration
st.set_page_config(page_title="TestCaseGPT 🤪🤖", page_icon="📝")

st.title("TestCaseGPT 🤪🤖")
st.caption("Upload an API documentation PDF to generate structured test cases!")

# Define Data Directory and Test Case File
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
TEST_CASES_FILE = os.path.join(DATA_DIR, "test_cases.json")

# File Upload
uploaded_file = st.file_uploader("Upload a PDF (API Documentation)", type=["pdf"])

def generate_random_email():
    """Generate a unique email to avoid duplicates."""
    return f"user{random.randint(1000, 99999)}@example.com"

def generate_secure_password():
    """Generate a random secure password each time."""
    special_chars = "!@#$%^&*"
    return (
        random.choice(string.ascii_uppercase) +
        random.choice(string.ascii_lowercase) +
        random.choice(string.digits) +
        random.choice(special_chars) +
        "".join(random.choices(string.ascii_letters + string.digits, k=8))
    )

def generate_unique_data():
    """Create unique test data for each test run."""
    return {
        "Email": generate_random_email(),
        "Password": generate_secure_password(),
        "Role": "customer"
    }

def save_test_cases(test_cases):
    """Overwrite JSON file with fresh test cases every time."""
    with open(TEST_CASES_FILE, "w") as f:
        json.dump(test_cases, f, indent=4)

def load_data(file_path):
    """Load PDF and create a new FAISS vector store each run."""
    try:
        with st.spinner("Loading and indexing the document..."):
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            if not documents:
                st.error("❌ Could not load the document!")
                st.stop()
            
            st.success(f"✅ Loaded {len(documents)} pages")
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=GEMINI_API_KEY,
            )
            return FAISS.from_documents(documents, embeddings)
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.stop()

# Initialize AI model with randomness
chat_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=GEMINI_API_KEY,
    temperature=1.0  # Ensures varied outputs
)

def push_to_github():
    """Commits and pushes the test_cases.json file to GitHub."""
    try:
        repo_url = f"https://{GITHUB_USERNAME}:{PAT_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git"
        
        commands = [
            "git config --global user.name 'TestCaseGPT'",
            "git config --global user.email 'testcasegpt@users.noreply.github.com'",
            "git add data/test_cases.json",
            'git commit -m "Updated test cases"',
            f"git push {repo_url} main"
        ]
        
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True)
        
        st.success("✅ Test cases pushed to GitHub successfully!")
    
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Git push failed: {str(e)}")

def generate_test_cases(vector_store):
    """Generate test cases and overwrite the JSON file with new ones each run."""
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)  # Reset memory every time

    retrieval_chain = ConversationalRetrievalChain.from_llm(
        llm=chat_model,
        retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        return_source_documents=False,
        output_key="answer"
    )

    prompt = f"""Generate **5 different API test cases** in JSON format.
    Each test case must have **randomized input data** like email and password:
    [
        {{
            "api_endpoint": "/api/user/signup",
            "method": "POST",
            "payload": {json.dumps(generate_unique_data())},
            "expected_status": 200,
            "expected_response_keys": ["Email", "token"]
        }}
    ]
    Return **only JSON output**.
    """

    st.info("Generating fresh test cases...")

    try:
        response = retrieval_chain.invoke({"question": prompt})

        if not response or "answer" not in response:
            st.error("❌ No response received.")
            return

        raw_json = response["answer"].strip()

        # Extract valid JSON from response
        match = re.search(r"\[.*\]", raw_json, re.DOTALL)
        if match:
            raw_json = match.group(0)
        else:
            st.error("❌ No valid JSON found in response.")
            return

        # Parse JSON
        new_test_cases = json.loads(raw_json)

        # Inject unique values to ensure freshness
        for test in new_test_cases:
            test["payload"] = generate_unique_data()  # Ensure every test has unique data

        # Ensure metrics API test case is correctly structured
        new_test_cases.append({
            "api_endpoint": "/metrics",
            "method": "GET",
            "payload": {},
            "expected_status": 200,
            "expected_response_keys": []
        })

        # Overwrite the JSON file with fresh test cases
        save_test_cases(new_test_cases)

        st.success(f"✅ Fresh Test Cases Generated & Saved as `{TEST_CASES_FILE}`")
        st.json(new_test_cases)

        # Push the generated file to GitHub
        push_to_github()

    except json.JSONDecodeError as e:
        st.error(f"❌ JSON decoding error: {str(e)}")
        st.text_area("Raw response causing error:", raw_json)
    except Exception as e:
        st.error(f"Error generating test cases: {str(e)}")
        st.exception(e)


# Run process on file upload
if uploaded_file:
    file_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    vector_store = load_data(file_path)

    if vector_store:
        st.success("✅ Document processed successfully!")
        generate_test_cases(vector_store)