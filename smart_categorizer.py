CATEGORY_KEYWORDS = {
    "Food": ["zomato", "swiggy", "restaurant", "food", "cafe", "lunch", "dinner", "grocery", "starbucks"],
    "Transport": ["uber", "ola", "petrol", "fuel", "bus", "train", "taxi", "cab", "metro"],
    "Shopping": ["amazon", "flipkart", "myntra", "mall", "shopping", "clothing", "electronics"],
    "Bills": ["electricity", "recharge", "wifi", "rent", "bill", "water", "gas"],
}

def categorize(note: str) -> str:
    # Convert the user's note to lowercase to make search case-insensitive
    note_lower = note.lower()
    
    # Loop through each category and its associated list of keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        # Check if any keyword in the list is present inside the user's note
        if any(keyword in note_lower for keyword in keywords):
            return category
            
    # Default category if no keywords match
    return "Other"