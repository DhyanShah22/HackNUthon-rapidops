import os
import json
import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# API Key
GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"

# Streamlit configuration
st.set_page_config(page_title="TestCaseGPT 🧪🤖", page_icon="📜")

st.title("TestCaseGPT 🧪🤖")
st.caption("Upload an API documentation PDF to generate structured test cases!")

# Define Data Directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

test_cases_file = os.path.join(DATA_DIR, "test_cases.json")
if not os.path.exists(test_cases_file):
    with open(test_cases_file, "w") as f:
        json.dump([], f)

# File Upload
uploaded_file = st.file_uploader("Upload a PDF (API Documentation)", type=["pdf"])

@st.cache_resource(show_spinner=False)
def load_data(file_path):
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
            vector_store = FAISS.from_documents(documents, embeddings)
            return vector_store
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.stop()

chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GEMINI_API_KEY)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

import re

def generate_test_cases(vector_store):
    retrieval_chain = ConversationalRetrievalChain.from_llm(
        llm=chat_model,
        retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        return_source_documents=False,
        output_key="answer"
    )
    
    prompt = """Generate structured API test cases in the following JSON format:
    [
        {
            "api_endpoint": "<endpoint>",
            "method": "<HTTP_METHOD>",
            "payload": { <request_payload> },
            "expected_status": <STATUS_CODE>,
            "expected_response_keys": [<response_keys>]
        }
    ]
    """
    st.info("Generating test cases...")

    
    try:
        response = retrieval_chain.invoke({"question": prompt, "chat_history": []})
        
        if not response or "answer" not in response:
            st.error("❌ No response received.")
            return

        # Remove markdown code block formatting if present
        raw_json = response['answer'].strip()
        raw_json = re.sub(r"^```json\s*", "", raw_json)  # Remove opening ```
        raw_json = re.sub(r"\s*```$", "", raw_json)  # Remove closing ```

        # Parse JSON
        test_cases = json.loads(raw_json)
        
        with open(test_cases_file, "w") as f:
            json.dump(test_cases, f, indent=4)

        st.success("✅ Test cases generated and saved successfully!")
        st.json(test_cases)

    except json.JSONDecodeError as e:
        st.error(f"❌ JSON decoding error: {str(e)}")
        st.text_area("Raw response:", raw_json)
    except Exception as e:
        st.error(f"Error generating test cases: {str(e)}")
        st.exception(e)


if uploaded_file:
    file_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    vector_store = load_data(file_path)
    
    if vector_store:
        st.success("✅ Document processed successfully!")
        generate_test_cases(vector_store)
