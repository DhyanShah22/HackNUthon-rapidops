import os
import json
import streamlit as st
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# API Key
GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"

# Streamlit configuration
st.set_page_config(page_title="Figma TestCaseGPT 🧪", page_icon="📜")

# Sidebar
with st.sidebar:
    st.title("📌 Figma TestCaseGPT 🧪")
    st.markdown("### **🔍 Features**")
    st.markdown("- Upload **Figma JSON** 📝")
    st.markdown("- Generate & Save **Selenium Test Cases** ⚡")
    st.markdown("---")
    st.subheader("⚙️ **Settings**")
    dark_mode = st.checkbox("🌙 Enable Dark Mode")
    st.markdown("---")
    st.info("Developed by **Syntax Error**", icon="💡")
    st.caption("📌 Version: 1.0.0")

# Define Data Directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# File Upload
st.title("Figma TestCaseGPT 🧪")
st.caption("Upload a Figma JSON file to generate Selenium test cases!")

uploaded_file = st.file_uploader("Upload a JSON (Figma data)", type=["json"])

# Load and Process File
@st.cache_resource(show_spinner=False)
def load_figma_json(file_path):
    try:
        with open(file_path, "r") as f:
            figma_data = json.load(f)
        return figma_data
    except Exception as e:
        st.error(f"❌ Error loading JSON: {str(e)}")
        return None

# Initialize Chat Model and Memory
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GEMINI_API_KEY)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def extract_ui_elements(figma_data):
    elements = []
    
    def traverse(node):
        if isinstance(node, dict):
            if 'type' in node and 'name' in node:
                elements.append(f"{node['type']} - {node['name']}")
            for key in node:
                traverse(node[key])
        elif isinstance(node, list):
            for item in node:
                traverse(item)
    
    traverse(figma_data)
    return elements

# Generate test cases function
def generate_test_cases(ui_elements):
    prompt = f"""
    Generate Selenium test cases for the following UI elements:
    {', '.join(ui_elements)}

    Format the response as a JSON array where each test case has:
    - 'test_name': (string) The name of the test case
    - 'description': (string) A brief explanation of the test
    - 'steps': (list of strings) Step-by-step test actions
    - 'expected_result': (string) The expected outcome of the test

    Ensure the response is a valid JSON array and nothing else.
    """

    st.info("Generating test cases...")

    try:
        # Call the AI model
        response = chat_model.invoke(prompt)

        # Debugging: Show the raw response before parsing
        st.write("🔹 Raw Response from AI Model:", response.content)

        # Extract content from AIMessage
        response_text = response.content.strip() if hasattr(response, "content") else ""

        # Ensure response is not empty
        if not response_text:
            st.error("❌ AI model returned an empty response. Try rephrasing the prompt.")
            return []

        # Attempt to parse JSON safely
        try:
            test_cases = json.loads(response_text)
        except json.JSONDecodeError:
            st.error("❌ AI response is not valid JSON. Try adjusting the prompt.")
            return []

        # Ensure test cases are in expected format
        if not isinstance(test_cases, list):
            st.error("❌ AI response format incorrect. Expected a list of test cases.")
            return []

        return test_cases

    except Exception as e:
        st.error(f"⚠️ Error generating test cases: {str(e)}")
        return []


if uploaded_file:
    file_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    figma_data = load_figma_json(file_path)
    
    if figma_data:
        st.success("✅ Figma JSON loaded successfully!")
        ui_elements = extract_ui_elements(figma_data)
        
        if ui_elements:
            test_cases = generate_test_cases(ui_elements)
            
            if test_cases:
                test_cases_file = os.path.join(DATA_DIR, "selenium_test_cases.json")
                with open(test_cases_file, "w") as f:
                    json.dump(test_cases, f, indent=4)
                
                st.success("✅ Test cases generated and saved successfully!")
                st.write("### Generated Selenium Test Cases:")
                for tc in test_cases:
                    st.write(f"**{tc['test_name']}**")
                    st.write(f"🔹 {tc['description']}")
