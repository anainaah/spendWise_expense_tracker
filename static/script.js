// Elements
const form = document.getElementById('expense-form');
const tbody = document.getElementById('expense-body');
const insightEl = document.getElementById('insight');
let categoryChart; // Tracks Chart.js instance to prevent hover rendering glitches

// Helper: Set default date to today's date in local timezone (UX Polish)
document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date');
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
    
    // Initial fetch of data
    loadExpenses();
    loadSummary();
});

// Fetch and display all transactions in the table
async function loadExpenses() {
    try {
        const response = await fetch('/expenses');
        const expenses = await response.json();
        
        tbody.innerHTML = ''; // Reset the table content
        
        if (expenses.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 24px;">No transactions recorded yet.</td></tr>`;
            return;
        }

        expenses.forEach(e => {
            // Append rows with a modern category pill and delete button
            tbody.innerHTML += `
                <tr>
                    <td>${formatDate(e.date)}</td>
                    <td style="font-weight: 500;">${e.note}</td>
                    <td><span class="category-pill">${e.category}</span></td>
                    <td style="font-weight: 600;">₹${parseFloat(e.amount).toFixed(2)}</td>
                    <td>
                        <button class="btn-delete" onclick="deleteExpense(${e.id})">Delete</button>
                    </td>
                </tr>
            `;
        });
    } catch (error) {
        console.error("Error loading expenses:", error);
    }
}

// Fetch totals, insights, and update Chart.js categories
async function loadSummary() {
    try {
        const response = await fetch('/summary');
        const data = await response.json();
        
        // Update the AI Insights Banner
        insightEl.innerText = data.insight;

        const labels = Object.keys(data.by_category);
        const values = Object.values(data.by_category);

        // If the chart already exists, destroy it before drawing a new one
        if (categoryChart) {
            categoryChart.destroy();
        }

        // Draw new chart only if we have data
        if (labels.length > 0) {
            categoryChart = new Chart(document.getElementById('categoryChart'), {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        // Clean Mint and Teal themed color palette for chart segments
                        backgroundColor: [
                            '#0d9488', // Dark Teal
                            '#2dd4bf', // Bright Mint
                            '#14b8a6', // Turquoise
                            '#059669', // Emerald Green
                            '#94a3b8', // Cool Slate Gray
                            '#64748b'  // Dark Muted Slate
                        ],
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
                                font: {
                                    family: 'Inter',
                                    size: 12
                                },
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

// Handle Form Submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const amountVal = parseFloat(document.getElementById('amount').value);
    const noteVal = document.getElementById('note').value;
    const dateVal = document.getElementById('date').value;

    const payload = {
        amount: amountVal,
        note: noteVal,
        date: dateVal
    };

    try {
        const response = await fetch('/expenses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            form.reset();
            
            // Re-apply today's default date
            document.getElementById('date').value = new Date().toISOString().split('T')[0];
            
            // Refresh table list & charts
            await loadExpenses();
            await loadSummary();
        } else {
            const errData = await response.json();
            alert("Error: " + errData.error);
        }
    } catch (error) {
        console.error("Error submitting expense:", error);
    }
});

// Handle Delete Request
async function deleteExpense(id) {
    if (!confirm("Are you sure you want to delete this expense?")) return;

    try {
        const response = await fetch(`/expenses/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            await loadExpenses();
            await loadSummary();
        } else {
            alert("Error deleting record.");
        }
    } catch (error) {
        console.error("Error deleting expense:", error);
    }
}

// Helper: Format Date strings from YYYY-MM-DD to a more readable format
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', options);
}