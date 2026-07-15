import pytest
from app import app, db
from smart_categorizer import categorize

# ==========================================
# 1. UNIT TESTS (For Auto-Categorization)
# ==========================================

def test_categorize_food():
    assert categorize("zomato dinner") == "Food"
    assert categorize("lunch at cafe") == "Food"
    assert categorize("swiggy order") == "Food"

def test_categorize_transport():
    assert categorize("uber ride home") == "Transport"
    assert categorize("petrol refill") == "Transport"
    assert categorize("bus ticket") == "Transport"

def test_categorize_case_insensitive():
    assert categorize("UBER TRIP") == "Transport"
    assert categorize("SwIgGy Dinner") == "Food"

def test_categorize_fallback():
    assert categorize("random book purchase") == "Other"
    assert categorize("") == "Other"


# ==========================================
# 2. INTEGRATION TESTS (For Flask Scoped Auth & API Edit)
# ==========================================

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

# Helper function to register and log in a user during tests
def auth_user(client, username, password):
    client.post('/register', json={"username": username, "password": password})

def test_auth_blocks_unauthorized(client):
    """Verify backend blocks API endpoints if logged out."""
    res_get = client.get('/expenses')
    assert res_get.status_code == 401
    
    res_post = client.post('/expenses', json={"amount": 100, "note": "lunch", "date": "2026-07-15"})
    assert res_post.status_code == 401

def test_user_registration_and_login(client):
    """Verify standard register and login flow."""
    # Register
    reg_res = client.post('/register', json={"username": "alice", "password": "alicepassword"})
    assert reg_res.status_code == 201
    assert reg_res.json['username'] == "alice"
    
    # Check session authentication state
    auth_check = client.get('/check-auth')
    assert auth_check.json['authenticated'] is True
    assert auth_check.json['username'] == "alice"

def test_scoped_database_isolation(client):
    """Verify User A cannot read or write to User B's account."""
    # 1. Register User A and create an expense
    auth_user(client, "usera", "password123")
    client.post('/expenses', json={"amount": 250.0, "note": "Uber ride", "date": "2026-07-15"})
    
    get_res_a = client.get('/expenses')
    assert len(get_res_a.json) == 1
    
    # Logout User A
    client.post('/logout')
    
    # 2. Register User B and verify they see an empty list
    auth_user(client, "userb", "password123")
    get_res_b = client.get('/expenses')
    assert len(get_res_b.json) == 0  # Isolation check: User B cannot see User A's expense

def test_api_edit_expense(client):
    """Verify editing works and automatically re-categorizes if note changes."""
    auth_user(client, "testuser", "password123")
    
    # 1. Create an expense (Food keyword)
    post_res = client.post('/expenses', json={"amount": 400.0, "note": "zomato food", "date": "2026-07-15"})
    expense_id = post_res.json['id']
    assert post_res.json['category'] == "Food"

    # 2. Edit the expense (change amount and change note to transport keyword)
    edit_payload = {"amount": 120.0, "note": "uber taxi ride", "date": "2026-07-15"}
    put_res = client.put(f'/expenses/{expense_id}', json=edit_payload)
    
    assert put_res.status_code == 200
    assert put_res.json['amount'] == 120.0
    assert put_res.json['note'] == "uber taxi ride"
    # Verification: Smart categorizer should have triggered and updated category to Transport
    assert put_res.json['category'] == "Transport"