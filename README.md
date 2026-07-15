# SpendWise — AI-Assisted Expense Tracker
SpendWise is a full-stack expense tracker built with Flask, SQLite, and Vanilla JavaScript. It features automated expense categorization, secure user session authentication, RESTful APIs, interactive Chart.js visualizations, and monthly spending insights, showcasing full-stack development, database integration, and clean UI design.
---
## 🚀 Features
- **Multi-User Authentication**: Register/Login system using secure password hashing (`PBKDF2` via `werkzeug.security`) and cookie session persistence.
- **Automated Expense Categorization**: A custom rule-based engine (`smart_categorizer.py`) that checks transaction notes and automatically assigns categories (Food, Transport, Bills, Shopping, Other) upon entry.
- **Transaction Editing**: Edit amounts, notes, and dates dynamically. The categorizer automatically re-analyzes and updates the category if the note changes.
- **Plain-English Spending Insights**: An analysis module (`insights.py`) that calculates month-over-month category aggregates and generates natural-language spending feedback.
- **Interactive Data Visualization**: A dynamic dashboard utilizing **Chart.js** with custom mint/teal themes to display category distributions.
- **Defensive API Architecture**: Clean input validation, sanitization, and error handling, returning appropriate HTTP status codes (e.g., `400 Bad Request`, `201 Created`, `204 No Content`).
- **Automated Testing Suite**: Standardized testing containing unit tests for categorization rules and API integration tests using an isolated, in-memory SQLite database.
---
## 🛠️ Tech Stack
- **Backend**: Python 3, Flask (REST API)
- **Database**: SQLite (local development), SQLAlchemy ORM (environment-variable configuration ready for production PostgreSQL/MySQL)
- **Frontend**: Vanilla HTML5, Custom CSS3 (Responsive Mint/Teal theme), Vanilla ES6 JavaScript (`fetch` API integration)
- **Testing**: Pytest
---
## 📁 Project Structure
```text
spendwise/
├── app.py                  # Main Flask server, configurations, and API routes
├── models.py               # SQLAlchemy Database schemas and models
├── smart_categorizer.py    # Auto-categorization business logic
├── insights.py             # Math logic for generating spending insights
├── test_app.py             # Automated unit and API integration tests
├── templates/
│   └── index.html          # Frontend page structure
├── static/
│   ├── style.css           # Styling sheets (Mint & Teal layout)
│   └── script.js           # Frontend logic & API interaction
├── requirements.txt        # Project dependencies
└── README.md               # Documentation



💻 Installation & Local Setup
Prerequisites
Python 3 installed
Git installed
1. Clone the Repository
bash


git clone https://github.com/anainaah/spendWise_expense_tracker.git
cd spendWise_expense_tracker
2. Set Up a Virtual Environment
bash


# Create environment
python -m venv venv
# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Activate on Mac/Linux
source venv/bin/activate
3. Install Dependencies
bash


pip install -r requirements.txt
4. Run the Server
bash


python app.py
Open your browser and navigate to http://127.0.0.1:5000.

🧪 Running Automated Tests
To execute the test suite (8 unit and integration tests), run:

bash


pytest
☁️ Deployment Guide (Render.com)
This application is ready to deploy on Render.com (Web Service):

Push your latest code to GitHub.
Log in to Render and click New > Web Service.
Connect your GitHub repository.
Configure Environment:
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app (This uses the production-grade Gunicorn WSGI server installed in your requirements).
Environment Variables (Advanced):
To keep database items persistent, click New > PostgreSQL on Render to spin up a free database.
Copy the Internal Database URL and add it to your Web Service env variables as DATABASE_URL. SQLAlchemy will automatically switch to PostgreSQL!
Add a variable SECRET_KEY with a random string to secure session cookies.








