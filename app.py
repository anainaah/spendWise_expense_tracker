import os
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Expense, User
from smart_categorizer import categorize
from insights import generate_insight

app = Flask(__name__)
CORS(app)

# Secret Key is required to sign session cookies securely
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'spendwise-super-secret-key-123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Helper: Check if a user is logged in
def get_current_user_id():
    return session.get('user_id')

# Route: Serve the Frontend HTML page
@app.route('/')
def home():
    return render_template('index.html')

# ==========================================
# AUTHENTICATION API ROUTES
# ==========================================

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required."}), 400
        
    username = data['username'].strip().lower()
    password = data['password']

    if len(username) < 3 or len(password) < 6:
        return jsonify({"error": "Username must be 3+ chars, password 6+ chars."}), 400

    # Check if user already exists
    existing_user = db.session.execute(db.select(User).where(User.username == username)).scalar()
    if existing_user:
        return jsonify({"error": "Username already taken."}), 400

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    
    # Automatically log them in after registration
    session['user_id'] = new_user.id
    session['username'] = new_user.username
    return jsonify({"message": "User registered successfully.", "username": new_user.username}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required."}), 400
        
    username = data['username'].strip().lower()
    password = data['password']

    user = db.session.execute(db.select(User).where(User.username == username)).scalar()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password."}), 401

    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({"message": "Logged in successfully.", "username": user.username})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."})

@app.route('/check-auth', methods=['GET'])
def check_auth():
    if get_current_user_id():
        return jsonify({"authenticated": True, "username": session.get('username')})
    return jsonify({"authenticated": False})

# ==========================================
# EXPENSES API ROUTES (Scoped to logged-in user)
# ==========================================

@app.route('/expenses', methods=['GET'])
def get_expenses():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized."}), 401
        
    stmt = db.select(Expense).where(Expense.user_id == user_id).order_by(Expense.date.desc())
    expenses = db.session.execute(stmt).scalars().all()
    return jsonify([e.to_dict() for e in expenses])

@app.route('/expenses', methods=['POST'])
def add_expense():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized."}), 401
        
    data = request.json
    if not data or 'amount' not in data or 'note' not in data or 'date' not in data:
        return jsonify({"error": "Missing required fields."}), 400
        
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({"error": "Amount must be positive."}), 400
    except ValueError:
        return jsonify({"error": "Invalid amount."}), 400

    note = str(data['note']).strip()
    if not note:
        return jsonify({"error": "Note cannot be empty."}), 400

    category = categorize(note)
    
    expense = Expense(
        amount=amount,
        note=note,
        category=category,
        date=data['date'],
        user_id=user_id
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify(expense.to_dict()), 201

# PUT route for Editing Expenses
@app.route('/expenses/<int:id>', methods=['PUT'])
def edit_expense(id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized."}), 401
        
    expense = db.session.get(Expense, id)
    if not expense or expense.user_id != user_id:
        return jsonify({"error": "Expense record not found."}), 404

    data = request.json
    if not data or 'amount' not in data or 'note' not in data or 'date' not in data:
        return jsonify({"error": "Missing required fields."}), 400
        
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({"error": "Amount must be positive."}), 400
    except ValueError:
        return jsonify({"error": "Invalid amount."}), 400

    note = str(data['note']).strip()
    if not note:
        return jsonify({"error": "Note cannot be empty."}), 400

    # Re-categorize only if the note text actually changed
    if expense.note != note:
        expense.category = categorize(note)

    expense.amount = amount
    expense.note = note
    expense.date = data['date']
    
    db.session.commit()
    return jsonify(expense.to_dict()), 200

@app.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized."}), 401
        
    expense = db.session.get(Expense, id)
    if not expense or expense.user_id != user_id:
        return jsonify({"error": "Expense record not found."}), 404
        
    db.session.delete(expense)
    db.session.commit()
    return '', 204

@app.route('/summary', methods=['GET'])
def summary():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized."}), 401
        
    stmt = db.select(Expense).where(Expense.user_id == user_id)
    expenses = db.session.execute(stmt).scalars().all()
    
    by_category = {}
    for e in expenses:
        by_category[e.category] = by_category.get(e.category, 0) + e.amount

    return jsonify({
        "by_category": by_category,
        "total": sum(e.amount for e in expenses),
        "insight": generate_insight(expenses)
    })

if __name__ == '__main__':
    app.run(debug=True)