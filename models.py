from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "note": self.note,
            "category": self.category,
            "date": self.date
        }

