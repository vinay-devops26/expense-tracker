import streamlit as st
import os
import sqlite3

db_file = "expense_tracker.db"

if not os.path.exists(db_file):
    print("Database file not found")

conn = sqlite3.connect(db_file)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type TEXT,
    description TEXT,
    amount REAL,
    category TEXT,
    date TEXT
)
""")

conn.commit()

st.title("💰 Expense Tracker")

transaction_type = st.radio(
    "Select Transaction Type",
    ["Income", "Expense"]
)

description = st.text_input("Description")

amount = st.number_input("Amount", min_value=0.0, step=100.0)

if transaction_type == "Income":
    category = st.selectbox(
        "Income Category",
        ["Salary", "Freelance", "Business", "Other Income"]
    )

else:
    category = st.selectbox(
        "Expense Category",
        [
            "Food",
            "Travel",
            "Shopping",
            "Bills",
            "Medical",
            "Education",
            "Entertainment",
            "Rent",
            "Other Expense"
        ]
    )

date = st.date_input("Date")

if st.button("Save Transaction"):
    cursor.execute(
        "INSERT INTO transactions (transaction_type, description, amount, category, date) VALUES (?, ?, ?, ?, ?)",
        (transaction_type, description, amount, category, str(date))
    )

conn.commit()

st.success("Transaction Saved Successfully! ✅")

total_income = cursor.execute(
    "SELECT SUM(amount) FROM transactions WHERE transaction_type = 'Income'"
).fetchone()[0] or 0

total_expense = cursor.execute(
    "SELECT SUM(amount) FROM transactions WHERE transaction_type = 'Expense'"
).fetchone()[0] or 0

balance = total_income - total_expense

st.subheader("💰 Expense Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Total Income", f"₹{total_income:,.2f}")

with col2:
    st.metric("💸 Total Expense", f"₹{total_expense:,.2f}")

with col3:
    st.metric("💵 Balance", f"₹{balance:,.2f}")


st.subheader("📋 All Transactions")

data = cursor.execute(
    "SELECT * FROM transactions ORDER BY id DESC"
).fetchall()

st.dataframe(
    data,
    column_config={
        "id": "ID",
        "transaction_type": "Type",
        "description": "Description",
        "amount": "Amount",
        "category": "Category",
        "date": "Date"
    },
    hide_index=True
)

