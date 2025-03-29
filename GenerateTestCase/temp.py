# import os
# import json
# import streamlit as st
# from langchain.document_loaders import PyPDFLoader
# from langchain.vectorstores import FAISS
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory

# # API Key
# GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"

# # Streamlit configuration
# st.set_page_config(page_title="TestCaseGPT 🧪🤖", page_icon="📜")

# # Sidebar
# with st.sidebar:
#     st.title("📌 TestCaseGPT 🧪🤖")
#     st.markdown("### **🔍 Features**")
#     st.markdown("- Upload **Requirements PDF** 📄 or **Figma JSON** 📝")
#     st.markdown("- Generate & Save **Test Cases** ⚡")
    
#     st.markdown("---")
#     st.subheader("⚙️ **Settings**")
#     dark_mode = st.checkbox("🌙 Enable Dark Mode")
    
#     st.markdown("---")
#     st.info("Developed by **Syntax Error**", icon="💡")
#     st.caption("📌 Version: 1.0.0")

# # Define Data Directory
# DATA_DIR = "data"
# os.makedirs(DATA_DIR, exist_ok=True)

# test_cases_file = os.path.join(DATA_DIR, "test_cases.json")
# if not os.path.exists(test_cases_file):
#     with open(test_cases_file, "w") as f:
#         json.dump([], f)

# # File Upload
# st.title("TestCaseGPT 🧪🤖")
# st.caption("Upload a document to generate test cases automatically!")

# uploaded_file = st.file_uploader("Upload a PDF (requirements) or JSON (Figma data)", type=["pdf", "json"])

# # Load and Process File
# @st.cache_resource(show_spinner=False)
# def load_data(file_path, file_type):
#     try:
#         with st.spinner("Loading and indexing the document..."):
#             if file_type == "pdf":
#                 loader = PyPDFLoader(file_path)
#                 documents = loader.load()
#             else:
#                 with open(file_path, "r") as f:
#                     documents = [{"page_content": json.load(f)}]
            
#             if not documents:
#                 st.error("❌ Could not load the document!")
#                 st.stop()
            
#             st.success(f"✅ Loaded {len(documents)} pages")
#             embeddings = GoogleGenerativeAIEmbeddings(
#                 model="models/embedding-001",
#                 google_api_key=GEMINI_API_KEY,
#             )
#             vector_store = FAISS.from_documents(documents, embeddings)
#             return vector_store
#     except Exception as e:
#         st.error(f"❌ Error: {str(e)}")
#         st.stop()

# # Initialize Chat Model and Memory
# chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GEMINI_API_KEY)
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# def generate_test_cases(vector_store):
#     retrieval_chain = ConversationalRetrievalChain.from_llm(
#         llm=chat_model,
#         retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
#         memory=memory,
#         return_source_documents=False,
#         output_key="answer"
#     )
    
#     prompt = "Generate test cases based on the uploaded document."
#     st.info("Generating test cases...")
    
#     try:
#         response = retrieval_chain.invoke({
#             "question": prompt,
#             "chat_history": []
#         })
        
#         st.info(f"Raw response: {response}")  # Debugging message
        
#         if not response or "answer" not in response:
#             st.error("❌ No response received. Check the document content and API integration.")
#             return

#         answer = response['answer'].strip()
        
#         if not answer:
#             st.error("❌ Empty response received. Ensure the document has meaningful content.")
#             return
        
#         import re

#         def extract_test_cases(answer):
#             lines = [line.strip() for line in answer.split("\n") if line.strip()]
#             test_cases = []
            
#             for line in lines:
#                 # Identify test case lines (lines that start with '* ' or contain 'Verify')
#                 if re.match(r"^\*\s", line) or "Verify" in line:
#                     test_cases.append(line)
            
#             return test_cases
        
#         test_cases = extract_test_cases(answer)
        
#         if not test_cases:
#             st.error("❌ No test cases found in response.")
#             return

#         # Save test cases
#         with open(test_cases_file, "r+") as f:
#             data = json.load(f)
#             data.append({"query": prompt, "test_cases": test_cases})
#             f.seek(0)
#             json.dump(data, f, indent=4)

#         st.success("✅ Test cases generated and saved successfully!")
#         st.write("### Generated Test Cases:")
#         for idx, tc in enumerate(test_cases, start=1):
#             st.write(f"**Test Case {idx}:** {tc}")

#     except Exception as e:
#         st.error(f"Error generating test cases: {str(e)}")
#         st.exception(e)

# # Process the uploaded file
# if uploaded_file:
#     file_path = os.path.join(DATA_DIR, uploaded_file.name)
#     with open(file_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())
    
#     file_type = "pdf" if uploaded_file.name.endswith(".pdf") else "json"
#     vector_store = load_data(file_path, file_type)
    
#     if vector_store:
#         st.success("✅ Document processed successfully!")
#         generate_test_cases(vector_store)