import os
from flask import Flask, request, jsonify, render_template
from models import db, Expense
from smart_categorizer import categorize
from insights import generate_insight

app = Flask(__name__)

# Config: Use PostgreSQL/MySQL database URL in production (Render), fallback to local SQLite in development
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create database tables automatically if they don't exist
with app.app_context():
    db.create_all()

# Route: Serve the Frontend HTML page
@app.route('/')
def home():
    return render_template('index.html')

# Route: Fetch all expenses ordered by date descending
@app.route('/expenses', methods=['GET'])
def get_expenses():
    # Modern SQLAlchemy 2.0 selection syntax
    stmt = db.select(Expense).order_by(Expense.date.desc())
    expenses = db.session.execute(stmt).scalars().all()
    return jsonify([e.to_dict() for e in expenses])

# Route: Add a new expense (with automated smart categorization)
@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    
    # 1. Input Validation (Defensive Programming)
    if not data or 'amount' not in data or 'note' not in data or 'date' not in data:
        return jsonify({"error": "Missing required fields: amount, note, and date."}), 400
        
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({"error": "Amount must be a positive number."}), 400
    except ValueError:
        return jsonify({"error": "Amount must be a valid number."}), 400

    note = str(data['note']).strip()
    if not note:
        return jsonify({"error": "Expense description note cannot be empty."}), 400

    # 2. Automated Smart Categorization
    category = categorize(note)
    
    # 3. Save to database
    expense = Expense(
        amount=amount,
        note=note,
        category=category,
        date=data['date']
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify(expense.to_dict()), 201

# Route: Delete an expense by ID
@app.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    # Modern SQLAlchemy 2.0 get syntax
    expense = db.session.get(Expense, id)
    if not expense:
        return jsonify({"error": "Expense record not found."}), 404
        
    db.session.delete(expense)
    db.session.commit()
    return '', 204

# Route: Get aggregate calculations and plain-text insights for the dashboard
@app.route('/summary', methods=['GET'])
def summary():
    stmt = db.select(Expense)
    expenses = db.session.execute(stmt).scalars().all()
    
    # Aggregate spending by category
    by_category = {}
    for e in expenses:
        by_category[e.category] = by_category.get(e.category, 0) + e.amount

    return jsonify({
        "by_category": by_category,
        "total": sum(e.amount for e in expenses),
        "insight": generate_insight(expenses)
    })

if __name__ == '__main__':
    # Run the server on debug mode locally
    app.run(debug=True)