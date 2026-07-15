// DOM Elements
const authOverlay = document.getElementById('auth-overlay');
const appContainer = document.getElementById('app-container');
const authForm = document.getElementById('auth-form');
const authUsernameInput = document.getElementById('auth-username');
const authPasswordInput = document.getElementById('auth-password');
const authTitle = document.getElementById('auth-title');
const authBtn = document.getElementById('auth-btn');
const toggleAuthModeBtn = document.getElementById('toggle-auth-mode');
const toggleText = document.getElementById('toggle-text');

const userDisplay = document.getElementById('user-display');
const logoutBtn = document.getElementById('logout-btn');

const expenseForm = document.getElementById('expense-form');
const tbody = document.getElementById('expense-body');
const insightEl = document.getElementById('insight');
const formTitle = document.getElementById('form-title');
const submitBtn = document.getElementById('submit-btn');
const cancelEditBtn = document.getElementById('cancel-edit-btn');

let categoryChart; 
let isLoginMode = true; // Tracks register vs. login screen state
let editingId = null;   // Tracks the ID of the expense currently being edited

// Check if user is already authenticated on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Set default date to today
    document.getElementById('date').value = new Date().toISOString().split('T')[0];
    
    await checkAuthentication();
});

// Authenticate checks
async function checkAuthentication() {
    try {
        const res = await fetch('/check-auth');
        const data = await res.json();
        if (data.authenticated) {
            showDashboard(data.username);
        } else {
            showAuthScreen();
        }
    } catch (e) {
        console.error("Auth check failed:", e);
        showAuthScreen();
    }
}

// Switch UI view to Dashboard
function showDashboard(username) {
    authOverlay.classList.add('hidden');
    appContainer.classList.remove('hidden');
    userDisplay.innerText = `👤 ${username}`;
    loadExpenses();
    loadSummary();
}

// Switch UI view to Auth Overlay
function showAuthScreen() {
    authOverlay.classList.remove('hidden');
    appContainer.classList.add('hidden');
    // Clear forms
    authForm.reset();
    expenseForm.reset();
    clearEditState();
}

// Handle Register / Login Form submission
authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = authUsernameInput.value.trim();
    const password = authPasswordInput.value;
    
    const endpoint = isLoginMode ? '/login' : '/register';
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        if (response.ok) {
            showDashboard(data.username);
        } else {
            alert(data.error || "Authentication failed.");
        }
    } catch (err) {
        console.error("Auth API error:", err);
    }
});

// Toggle Auth mode (Login vs Register)
toggleAuthModeBtn.addEventListener('click', () => {
    isLoginMode = !isLoginMode;
    if (isLoginMode) {
        authTitle.innerText = "Welcome to SpendWise";
        authBtn.innerText = "Log In";
        toggleText.innerText = "Don't have an account?";
        toggleAuthModeBtn.innerText = "Sign Up";
    } else {
        authTitle.innerText = "Create Account";
        authBtn.innerText = "Register";
        toggleText.innerText = "Already have an account?";
        toggleAuthModeBtn.innerText = "Log In";
    }
});

// Handle Logout
logoutBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/logout', { method: 'POST' });
        if (response.ok) {
            showAuthScreen();
        }
    } catch (e) {
        console.error("Logout failed:", e);
    }
});

// ==========================================
// CORE APP HANDLERS
// ==========================================

// Fetch and display transactions
async function loadExpenses() {
    try {
        const response = await fetch('/expenses');
        if (response.status === 401) {
            showAuthScreen();
            return;
        }
        const expenses = await response.json();
        
        tbody.innerHTML = '';
        
        if (expenses.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 24px;">No transactions recorded yet.</td></tr>`;
            return;
        }

        expenses.forEach(e => {
            tbody.innerHTML += `
                <tr>
                    <td>${formatDate(e.date)}</td>
                    <td style="font-weight: 500;">${e.note}</td>
                    <td><span class="category-pill">${e.category}</span></td>
                    <td style="font-weight: 600;">₹${parseFloat(e.amount).toFixed(2)}</td>
                    <td>
                        <div class="table-actions">
                            <button class="btn-edit" onclick="startEditExpense(${e.id}, ${e.amount}, '${e.note}', '${e.date}')">Edit</button>
                            <button class="btn-delete" onclick="deleteExpense(${e.id})">Delete</button>
                        </div>
                    </td>
                </tr>
            `;
        });
    } catch (error) {
        console.error("Error loading expenses:", error);
    }
}

// Fetch summaries and draw chart
async function loadSummary() {
    try {
        const response = await fetch('/summary');
        if (response.status === 401) return;
        const data = await response.json();
        
        insightEl.innerText = data.insight;

        const labels = Object.keys(data.by_category);
        const values = Object.values(data.by_category);

        if (categoryChart) {
            categoryChart.destroy();
        }

        if (labels.length > 0) {
            categoryChart = new Chart(document.getElementById('categoryChart'), {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: ['#0d9488', '#2dd4bf', '#14b8a6', '#059669', '#94a3b8', '#64748b'],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                font: { family: 'Inter', size: 12 },
                                boxWidth: 12
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error("Error loading summary:", error);
    }
}

// Trigger edit mode for a transaction
function startEditExpense(id, amount, note, date) {
    editingId = id;
    
    // Fill the inputs with current transaction values
    document.getElementById('amount').value = amount;
    document.getElementById('note').value = note;
    document.getElementById('date').value = date;
    
    // Modify form titles and buttons
    formTitle.innerText = "Edit Transaction";
    submitBtn.innerText = "Update Expense";
    cancelEditBtn.classList.remove('hidden');
    
    // Smooth scroll back to form (for mobile UX)
    document.querySelector('.form-card').scrollIntoView({ behavior: 'smooth' });
}

// Cancel current editing state
cancelEditBtn.addEventListener('click', clearEditState);

function clearEditState() {
    editingId = null;
    expenseForm.reset();
    document.getElementById('date').value = new Date().toISOString().split('T')[0];
    
    formTitle.innerText = "Add Transaction";
    submitBtn.innerText = "Log Expense";
    cancelEditBtn.classList.add('hidden');
}

// Handle Add/Edit Expense Form submit
expenseForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const amountVal = parseFloat(document.getElementById('amount').value);
    const noteVal = document.getElementById('note').value;
    const dateVal = document.getElementById('date').value;

    const payload = {
        amount: amountVal,
        note: noteVal,
        date: dateVal
    };

    // Determine if we are updating (PUT) or creating (POST)
    const url = editingId ? `/expenses/${editingId}` : '/expenses';
    const method = editingId ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            clearEditState();
            await loadExpenses();
            await loadSummary();
        } else {
            const errData = await response.json();
            alert("Error: " + errData.error);
        }
    } catch (error) {
        console.error("API request failed:", error);
    }
});

// Delete handler
async function deleteExpense(id) {
    if (!confirm("Are you sure you want to delete this expense?")) return;

    try {
        const response = await fetch(`/expenses/${id}`, { method: 'DELETE' });
        if (response.status === 401) {
            showAuthScreen();
            return;
        }
        if (response.ok) {
            await loadExpenses();
            await loadSummary();
        }
    } catch (error) {
        console.error("Delete failed:", error);
    }
}

// Helper: Format Date strings
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' };
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', options);
}