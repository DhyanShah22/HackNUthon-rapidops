# 🚀 InspectRa: AI-Powered Test Automation Platform

**InspectRa** is an intelligent automation framework that generates, executes, and analyzes test cases from API documentation and UI designs using AI. It leverages CI/CD pipelines to automate the entire testing lifecycle — from requirement understanding to intelligent failure diagnosis — reducing manual testing efforts by over 50%.

## ✨ Features

- 📄 Upload API docs or connect Figma designs
- 🧠 Auto-generate test cases using Google Gemini & LangChain
- ⚙️ Execute tests with Pytest (API) and Selenium (UI)
- 📊 Analyze and log failed test cases automatically
- 💡 AI-powered suggestions and fix recommendations
- 🔁 End-to-end CI/CD integration with GitHub Actions

---

## 📸 Screenshots

<p float="left">
  <img src="screenshots/architecture.png" width="400"/>
  <img src="screenshots/inspectra-ui.png" width="400"/>
</p>

---

## 🧩 Tech Stack

**Backend**: FastAPI, LangChain, Google Gemini, FAISS, Redis  
**Frontend**: Streamlit, React.js, Tailwind CSS  
**Testing**: Selenium, Pytest  
**CI/CD & DevOps**: GitHub Actions, Docker  
**Database**: FAISS for vector store, Redis for caching

---

## 🛠️ How It Works

### 1. Requirement Ingestion
- Upload API documentation (PDF) or Figma file link
- Requirements are parsed and embedded using LangChain + Gemini

### 2. Test Case Generation
- AI generates structured JSON test cases (both API & UI)
- Stored and committed to GitHub

### 3. Automated Testing & CI/CD
- GitHub Actions trigger test runs via Pytest and Selenium
- Test reports and `log.txt` are generated and stored

### 4. Log Analysis & Recommendations
- AI analyzes failed logs and suggests actionable fixes
- Devs can upload logs and get smart feedback from the Streamlit-based analyzer

---

## 📂 Folder Structure

├── GenerateTestCase/ │ ├── app.py (API TestCase Generator) │ └── data/test_cases.json ├── FigmaTestCase/ │ ├── app.py (Figma-based TestCase Generator) │ └── data/test_cases.json ├── Selenium-test/ │ └── app.py (Frontend tests using Selenium) ├── Py-test/ │ └── test_api.py (Backend tests using Pytest) ├── logAnalyzer/ │ └── analyzer_app.py (Log analyzer Streamlit App) ├── test_reports/ ├── logs/ ├── .github/workflows/ │ └── test_pipeline.yml └── README.md

yaml
Copy
Edit

---

## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/<your-username>/InspectRa.git && cd InspectRa

# Install dependencies
pip install -r requirements.txt

# Start the TestCase Generator
streamlit run GenerateTestCase/app.py

# Run the analyzer
streamlit run logAnalyzer/analyzer_app.py
📈 CI/CD Pipeline
✅ GenerateTestCase/test_cases.json triggers API test job

✅ FigmaTestCase/test_cases.json triggers UI test job

✅ Both jobs log results to /logs and commit back to repo

🤖 Innovation
Combines RAG (Retrieval-Augmented Generation) with embeddings & vector DB (FAISS)

Uses cosine similarity to understand and cluster test requirements

Reduces dev/test workload and provides actionable logs using AI reasoning

👨‍💻 Contributors
Dhyan Shah (Team Lead, Backend & AI)

[Your Teammate 1] (Frontend & UI/UX)

[Your Teammate 2] (DevOps & CI/CD)

[Your Teammate 3] (Testing & Integration)

📄 License
This project is licensed under the MIT License.

🌟 Show some ❤️ by starring this repo!
python
Copy
Edit

Let me know if you'd like a version with badges, links, or if you'd like the README written in a different style!
