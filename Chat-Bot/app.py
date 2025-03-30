import os
import streamlit as st
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Streamlit configuration
st.set_page_config(page_title="Test Log Analyzer 🧪", page_icon="🐜")

load_dotenv()

# Sidebar UI
with st.sidebar:
    st.title("🛠️ Test Log Analyzer")
    st.markdown("### **🚀 Features**")
    st.markdown("- Upload a **log.txt** 🐜")
    st.markdown("- Get **test failure analysis** ❌💪")
    st.markdown("- Receive **fix recommendations** 🛠️")
    st.markdown("---")
    st.info("Developed by **Dhyan Shah**", icon="💡")
    st.caption("Version: 2.1.0")

# API Key Validation
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("❌ API Key is missing. Set the `GEMINI_API_KEY` environment variable.")
    st.stop()

# Data Directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Upload log.txt File
st.title("Test Log Analyzer 🧪")
st.caption("Upload a log file and get AI-powered insights!")

uploaded_file = st.file_uploader("Upload a log.txt file", type=["txt"])
if uploaded_file:
    log_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(log_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ Uploaded: {uploaded_file.name}")

    # Load log file
    @st.cache_resource(show_spinner=False)
    def load_data(log_path):
        with st.spinner("Processing the log file..."):
            loader = TextLoader(log_path)
            documents = loader.load()
            if not documents:
                st.error("❌ Could not load the log file!")
                st.stop()
            
            # Create embeddings & vector store
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
            vector_store = FAISS.from_documents(documents, embeddings)
            return vector_store
    
    vector_store = load_data(log_path)

    # Conversation Memory
    memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)

    # Chat Model
    chat_model = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=GEMINI_API_KEY,
        temperature=0.5
    )

    # Retrieval Chain
    retrieval_chain = ConversationalRetrievalChain.from_llm(
        llm=chat_model,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True,
        chain_type="stuff",
        verbose=True
    )

    # **Automatic Log Analysis**
    with st.spinner("Analyzing failed test cases..."):
        try:
            response = retrieval_chain({
                "question": "Identify failed test cases and suggest fixes from this log file.",
                "chat_history": []
            })
            
            st.subheader("❌ Failed Test Cases & Fix Recommendations")
            st.write(response['answer'])
            
            if 'source_documents' in response:
                with st.expander("View Log Extracts"):
                    for i, doc in enumerate(response['source_documents']):
                        st.write(f"Source {i+1}:")
                        st.write(doc.page_content)
                        st.write("---")
        except Exception as e:
            st.error(f"Error analyzing logs: {str(e)}")
