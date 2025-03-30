import os
import json
import requests
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory

# API Key (Replace with your actual Gemini API key)
GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"

# Ensure data directory exists
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
TEST_CASES_FILE = os.path.join(DATA_DIR, "test_cases.json")

# Streamlit UI
st.set_page_config(page_title="Figma TestCaseGPT 🧪", page_icon="📜")

# Sidebar
with st.sidebar:
    st.title("📌 Figma TestCaseGPT 🧪")
    st.markdown("### **🔍 Features**")
    st.markdown("- Fetch **Figma JSON** from API 📝")
    st.markdown("- Generate & Save **Selenium Test Cases** ⚡")
    st.markdown("---")
    st.subheader("⚙️ **Settings**")
    dark_mode = st.checkbox("🌙 Enable Dark Mode")
    st.markdown("---")
    st.info("Developed by **Syntax Error**", icon="💡")
    st.caption("📌 Version: 1.0.0")

# User Inputs
st.title("Figma TestCaseGPT 🧪")
st.caption("Enter a Figma File URL to generate Selenium test cases!")

figma_url = st.text_input("Enter Figma File URL:")
figma_token = st.text_input("Enter Figma API Token:", type="password")

# Function to fetch Figma JSON
def get_figma_json(figma_url, figma_token):
    if "file/" in figma_url:
        file_key = figma_url.split("file/")[1].split("/")[0]
    elif "design/" in figma_url:
        file_key = figma_url.split("design/")[1].split("/")[0]
    else:
        st.error("❌ Invalid Figma URL. Expected 'file/' or 'design/'.")
        return None

    headers = {"X-Figma-Token": figma_token}
    response = requests.get(f"https://api.figma.com/v1/files/{file_key}", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"❌ Error fetching Figma data: {response.status_code} - {response.text}")
        return None

# Extract UI elements from Figma JSON
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

# Initialize AI model
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GEMINI_API_KEY)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Generate Selenium test cases
def generate_test_cases(ui_elements):
    prompt = f"""
    Generate structured Selenium test cases based on the following UI elements:
    {', '.join(ui_elements)}

    Respond **only** with a valid JSON array, formatted like this:

    [
        {{
            "test_name": "Test Case Name",
            "description": "Brief description of the test",
            "steps": [
                {{
                    "action": "click",
                    "target": "CSS selector or XPath",
                    "value": "optional value"
                }}
            ],
            "expected_result": "Expected outcome of the test"
        }}
    ]

    Do not include explanations, markdown formatting, or extra text outside the JSON array.
    """


    st.info("Generating test cases...")

    try:
        response = chat_model.invoke(prompt)
        response_text = response.content.strip() if hasattr(response, "content") else ""

        if not response_text:
            st.error("❌ AI model returned an empty response. Try rephrasing the prompt.")
            return []

        try:
            test_cases = json.loads(response_text)
        except json.JSONDecodeError:
            st.error("❌ AI response is not valid JSON. Try adjusting the prompt.")
            return []

        if not isinstance(test_cases, list):
            st.error("❌ AI response format incorrect. Expected a list of test cases.")
            return []

        return test_cases

    except Exception as e:
        st.error(f"⚠️ Error generating test cases: {str(e)}")
        return []

# Function to save test cases to a file
def save_test_cases(test_cases):
    try:
        with open(TEST_CASES_FILE, "w", encoding="utf-8") as f:
            json.dump(test_cases, f, indent=4)
        return True
    except Exception as e:
        st.error(f"❌ Error saving test cases: {str(e)}")
        return False

# Main Process
if st.button("Generate Test Cases"):
    if figma_url and figma_token:
        figma_data = get_figma_json(figma_url, figma_token)

        if figma_data:
            st.success("✅ Figma JSON fetched successfully!")
            ui_elements = extract_ui_elements(figma_data)
            
            if ui_elements:
                test_cases = generate_test_cases(ui_elements)
                
                if test_cases:
                    # Save test cases to file
                    if save_test_cases(test_cases):
                        st.success(f"✅ Test cases saved in `{TEST_CASES_FILE}`!")

                    # Display test cases
                    st.write("### Generated Selenium Test Cases:")
                    for tc in test_cases:
                        st.write(f"**{tc['test_name']}**")
                        st.write(f"🔹 {tc['description']}")

                    # Download button
                    st.download_button(
                        label="Download Test Cases JSON",
                        data=json.dumps(test_cases, indent=4),
                        file_name="selenium_test_cases.json",
                        mime="application/json"
                    )
    else:
        st.warning("⚠️ Please enter both Figma URL and API Token.")
