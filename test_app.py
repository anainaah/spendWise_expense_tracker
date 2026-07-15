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
# 2. INTEGRATION TESTS (For Flask API Routes)
# ==========================================

# A Pytest fixture that sets up a clean, isolated in-memory test database 
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Build temporary tables in memory
        yield client         # Return test client to execute route requests
        with app.app_context():
            db.drop_all()    # Clean up after tests run

def test_home_route(client):
    """Verify that the landing page renders successfully."""
    response = client.get('/')
    assert response.status_code == 200

def test_api_get_expenses_empty(client):
    """Verify that a clean database returns an empty list."""
    response = client.get('/expenses')
    assert response.status_code == 200
    assert response.json == []

def test_api_add_expense_validation(client):
    """Verify API rejects bad inputs with 400 Bad Request."""
    bad_payload = {"amount": -10.0, "note": "Valid note", "date": "2026-07-15"}
    response = client.post('/expenses', json=bad_payload)
    assert response.status_code == 400
    
    empty_note_payload = {"amount": 500, "note": "", "date": "2026-07-15"}
    response = client.post('/expenses', json=empty_note_payload)
    assert response.status_code == 400

def test_api_add_and_delete_expense(client):
    """Verify successful POST and DELETE cycles."""
    # 1. Add record
    payload = {"amount": 250.0, "note": "Swiggy burger", "date": "2026-07-15"}
    post_res = client.post('/expenses', json=payload)
    assert post_res.status_code == 201
    expense_id = post_res.json['id']
    assert post_res.json['category'] == "Food"  # Check auto-categorization works on API request
    
    # 2. Fetch list to verify it exists
    get_res = client.get('/expenses')
    assert len(get_res.json) == 1
    
    # 3. Delete record
    delete_res = client.delete(f'/expenses/{expense_id}')
    assert delete_res.status_code == 204
    
    # 4. Fetch list again to verify it is gone
    get_res_after = client.get('/expenses')
    assert len(get_res_after.json) == 0