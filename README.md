# ai-code-reviewer
CodeReview – AI Code Assistant

An AI-powered code review application built using Python, Flask, and Ollama. It helps developers understand their code, identify potential issues, get suggestions, fix errors, and convert code between programming languages.

The application uses a locally running AI model through Ollama, so no paid cloud API key is required.

Features

- AI Code Review: Analyze code and identify potential issues.
- Error Explanation: Understand errors and problematic code in simple language.
- Code Suggestions: Get recommendations to improve code quality and readability.
- Fix Code: Generate an improved version of submitted code.
- Code Conversion: Convert code from one programming language to another.
- User Authentication: Register and log in securely.
- Review History: Access previously submitted code reviews.
- Local AI Integration: Use Ollama to run the AI model locally.
- Responsive Interface: Clean and user-friendly web interface.

Technologies Used

Technology| Purpose
Python| Backend programming
Flask| Web application framework
HTML| Page structure
CSS| User interface design
JavaScript| Frontend interactions
SQLite| Database
Ollama| Local AI model integration
Qwen2.5-Coder| AI-powered code assistance
Git & GitHub| Version control

Project Structure

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

Installation and Setup

1. Clone the Repository

git clone YOUR_GITHUB_REPOSITORY_URL

Navigate into the project:

cd CodeReview_Ollama

2. Install Ollama

Download and install Ollama:

https://ollama.com/download/windows

3. Download the AI Model

Open your terminal and run:

ollama pull qwen2.5-coder:1.5b

To test the model:

ollama run qwen2.5-coder:1.5b

4. Create a Virtual Environment

py -m venv venv

Activate it in Windows PowerShell:

.\venv\Scripts\Activate.ps1

5. Install Dependencies

pip install -r requirements.txt

6. Run the Application

Make sure Ollama is running, then execute:

python app.py

Open your browser and visit:

http://127.0.0.1:5000

Create an account and start reviewing your code.

How It Works

1. The user registers or logs into the application.
2. The user selects a programming language and enters code.
3. The application sends the code to the local Ollama model.
4. The AI analyzes the submitted code.
5. The application displays the review, explanations, and suggestions.
6. Users can request code fixes or language conversion.
7. Review history is stored in the SQLite database.

Security Notes

- User passwords are stored using password hashing.
- The application uses a local AI model instead of a paid cloud API.
- Submitted code is analyzed as text and is not executed by the application.
- Never commit passwords, API keys, or other sensitive information to GitHub.

Future Improvements

- Support for additional programming languages.
- More detailed code quality analysis.
- Improved error detection and explanations.
- Download reviewed and corrected code.
- Additional AI models and customization options.

Author
Shivakumar

---

CodeReview is a learning and development project created to explore AI integration, Python web development, and automated code analysis.
