# SpendWise — AI-Assisted Expense Tracker

SpendWise is a full-stack expense tracker built with Flask, SQLite, and Vanilla JavaScript. It features automated expense categorization, RESTful APIs, interactive Chart.js visualizations, and monthly spending insights, showcasing full-stack development, database integration, and clean UI design.

## 🚀 Features

- **Automated Expense Categorization**: A custom rule-based engine (`smart_categorizer.py`) that checks transaction notes and automatically assigns categories (Food, Transport, Bills, Shopping, Other) upon entry.
- **Plain-English Spending Insights**: An analysis module (`insights.py`) that calculates month-over-month category aggregates and generates natural-language spending feedback (e.g., *"You spent 15% more on Food this month than last month"*).
- **Interactive Data Visualization**: A dynamic dashboard utilizing **Chart.js** to display category distributions that updates in real-time without reloading the page.
- **Defensive API Architecture**: Clean input validation, sanitization, and error handling, returning appropriate HTTP status codes (e.g., `400 Bad Request`, `201 Created`, `204 No Content`).
- **Automated Testing Suite**: Standardized testing containing unit tests for categorization rules and API integration tests using an isolated, in-memory SQLite database.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask (REST API)
- **Database**: SQLite (local development), SQLAlchemy ORM (Twelve-Factor environment-variable configuration ready for production PostgreSQL/MySQL)
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


Installation & Setup
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
To execute the test suite (unit and integration tests), run:
bash


pytest
🔮 Future Roadmap
Machine Learning Upgrade: Replace the rule-based keyword categorizer with a trained Naive Bayes text classifier using scikit-learn once the transaction dataset reaches a sufficient size.
Database Migrations: Integrate Flask-Migrate (Alembic) to handle safe database schema updates in production.
Multi-user Authentication: Implement JWT (JSON Web Tokens) or session-based cookies to allow multiple users to securely track expenses in isolated accounts.




