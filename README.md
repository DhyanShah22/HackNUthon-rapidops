TestCaseGPT 🤪🤖

TestCaseGPT is an AI-powered tool that generates structured test cases from API documentation PDFs. It uses Google Gemini AI for intelligent test case generation and supports automated GitHub integration for seamless test case management.

🚀 Features

PDF Parsing & Vector Storage: Uses FAISS for efficient document retrieval.

AI-powered Test Case Generation: Generates structured test cases dynamically.

Automated Unique Test Data: Ensures every test case has unique randomized inputs.

GitHub Integration: Pushes generated test cases to a GitHub repository automatically.

CI/CD Pipeline: Automates deployment and test case updates.

Figma Integration: Synchronizes UI/UX designs with test case generation.

📥 Installation & Setup

Prerequisites

Python 3.8+

Streamlit

GitHub Personal Access Token (PAT)

Google Gemini API Key

Figma API Token

1️⃣ Clone the Repository

git clone https://github.com/YOUR_USERNAME/TestCaseGPT.git
cd TestCaseGPT

2️⃣ Install Dependencies

pip install -r requirements.txt

3️⃣ Set Up Environment Variables

Create a .env file and add:

GEMINI_API_KEY=your_google_api_key
GITHUB_USERNAME=your_github_username
GITHUB_REPO=your_github_repo
PAT_TOKEN=your_github_pat
FILE_PATH_IN_REPO=data/test_cases.json
FIGMA_API_KEY=your_figma_api_key
FIGMA_FILE_ID=your_figma_file_id

4️⃣ Run the Application

streamlit run app.py

📝 How It Works

Upload an API documentation PDF.

AI processes and extracts test scenarios.

Unique test data (email/password) is generated dynamically.

Test cases are saved and pushed to GitHub.

CI/CD pipeline triggers automated testing.

UI changes in Figma trigger test case updates.

🖼️ Figma Integration

Syncs UI/UX components with test case definitions.

Uses Figma API to extract form fields and expected API behaviors.

Automated mapping of UI fields to API payloads.

🔄 Fetching UI Elements from Figma

import requests
headers = {"Authorization": f"Bearer {FIGMA_API_KEY}"}
figma_url = f"https://api.figma.com/v1/files/{FIGMA_FILE_ID}"
data = requests.get(figma_url, headers=headers).json()
print(data)

🔄 CI/CD Automation

🔹 GitHub Actions Workflow

Automates test case updates and deployments.

.github/workflows/deploy.yml

name: CI/CD Pipeline
on:
  push:
    branches:
      - main
  schedule:
    - cron: '0 0 * * *'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v2
      - name: Install Dependencies
        run: pip install -r requirements.txt
      - name: Run Test Case Generation
        run: python app.py
      - name: Commit and Push Changes
        run: |
          git config --global user.email "ci@github.com"
          git config --global user.name "GitHub Actions"
          git add data/test_cases.json
          git commit -m "Automated test case update"
          git push origin main

📌 Project Structure

📂 TestCaseGPT
├── 📂 data               # Stores test_cases.json
├── 📂 src                # Core logic and utility functions
├── 📂 .github/workflows  # CI/CD pipeline
├── app.py                # Streamlit application
├── requirements.txt      # Dependencies
├── README.md             # Documentation

📊 Example Test Case Output

[
  {
    "api_endpoint": "/api/user/signup",
    "method": "POST",
    "payload": {
      "Email": "user1234@example.com",
      "Password": "Secure@1234",
      "Role": "customer"
    },
    "expected_status": 200,
    "expected_response_keys": ["Email", "token"]
  }
]

🤝 Contributions

Feel free to fork, submit issues, or contribute enhancements!

🛠️ Future Enhancements

Integrate OpenAPI spec parsing.

Add more test scenarios dynamically.

Enhance CI/CD to deploy test cases to cloud environments.

📄 License

MIT License. See LICENSE for details.

🚀 Test smarter, deploy faster! 🚀

