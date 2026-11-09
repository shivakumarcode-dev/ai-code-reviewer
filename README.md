🚀 CodeReview – AI Code Assistant

An AI-powered code review application built using Python, Flask, and Ollama. It helps developers analyze source code, identify potential issues, understand errors, improve code quality, generate corrected code, and convert code between programming languages.

The application uses a locally running AI model through Ollama, eliminating the need for paid cloud API keys.

✨ Features
AI Code Review: Analyze source code and identify potential bugs and issues.
Error Explanation: Understand errors and problematic code in simple language.
Code Suggestions: Get recommendations to improve code quality, readability, and maintainability.
Fix Code: Generate improved and corrected versions of submitted code.
Code Conversion: Convert code from one programming language to another.
User Authentication: Secure user registration and login.
Review History: Access previously submitted code reviews.
Local AI Integration: Run AI models locally using Ollama.
Responsive Interface: Clean and user-friendly web interface.
🛠️ Technologies Used
Technology	Purpose
Python	Backend programming
Flask	Web application framework
HTML5	Page structure
CSS3	User interface design
JavaScript	Frontend interactions
SQLite	Database management
Ollama	Local AI model integration
Qwen2.5-Coder	AI-powered code assistance
Git & GitHub	Version control
📁 Project Structure
text
CodeReview_Ollama/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── templates/
│   ├── auth.html
│   └── index.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        └── app.js

⚙️ Installation and Setup
1. Clone the Repository
bash
git clone YOUR_GITHUB_REPOSITORY_URL


Navigate into the project directory:

bash
cd CodeReview_Ollama

2. Install Ollama

Download and install Ollama:

https://ollama.com/download

3. Download the AI Model

Open your terminal and execute:

bash
ollama pull qwen2.5-coder:1.5b


To test the model:

bash
ollama run qwen2.5-coder:1.5b

4. Create a Virtual Environment
bash
py -m venv venv


Activate the environment in Windows PowerShell:

powershell
.\venv\Scripts\Activate.ps1

5. Install Dependencies
bash
pip install -r requirements.txt

6. Run the Application

Make sure Ollama is running, then execute:

bash
python app.py


Open your browser and visit:

http://127.0.0.1:5000

Register an account and start reviewing your code!

🔄 How It Works
The user registers or logs into the application.
The user selects a programming language and enters source code.
The application sends the submitted code to the locally running Ollama model.
The AI model analyzes the source code.
The application displays code reviews, explanations, and improvement suggestions.
Users can request corrected code or convert code into another programming language.
Previous reviews are stored in the SQLite database.
🔐 Security
User passwords are stored using password hashing.
The application uses a locally running AI model instead of a paid cloud API.
Submitted code is analyzed as text and is not executed by the application.
Sensitive information such as passwords, secret keys, and environment variables should never be committed to GitHub.
Local model execution does not automatically guarantee that submitted code or data is secure.
🚀 Future Improvements
Support for additional programming languages.
More detailed code quality analysis.
Improved bug detection and error explanations.
Download reviewed and corrected code.
Integration of additional AI models.
Advanced code quality scoring.
Improved user dashboard and review history.
👨‍💻 Author

Shivakumar

BCA Graduate |Interested in AI and Software Development

📌 About the Project

CodeReview is a learning and development project created to explore AI integration, Python web development, local large language models, and automated code analysis.

If you find this project useful, consider giving it a ⭐ on GitHub!
