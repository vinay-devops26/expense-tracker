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
    person_name TEXT,
    description TEXT,
    amount REAL,
    category TEXT,
    date TEXT
)
""")

conn.commit()

st.title("💰 Income & Expense Tracker")

st.subheader("➕ Add Transaction")

transaction_type = st.radio(
    "Transaction Type",
    ["Income", "Expense"],
    horizontal=True
)

with st.form("transaction_form", clear_on_submit=True):

    person_name = st.text_input("Person Name")

    description = st.text_input("Description")

    amount = st.number_input(
        "Amount",
        min_value=0.0,
        step=100.0
    )

    if transaction_type == "Income":
        category = st.selectbox(
            "Income Category",
            [
                "Salary",
                "Freelance",
                "Business",
                "Other Income"
            ]
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

    save_transaction = st.form_submit_button(
        "💾 Save Transaction"
    )

if save_transaction:

    if person_name.strip() == "":
        st.warning("Please enter Person Name")

    elif description.strip() == "":
        st.warning("Please enter Description")

    elif amount <= 0:
        st.warning("Please enter a valid Amount")

    else:
        cursor.execute(
            """
            INSERT INTO transactions
            (
                transaction_type,
                person_name,
                description,
                amount,
                category,
                date
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                transaction_type,
                person_name.strip(),
                description.strip(),
                amount,
                category,
                str(date)
            )
        )

        conn.commit()

        st.success("Transaction Saved Successfully! ✅")

        st.rerun()

total_income = cursor.execute(
    """
    SELECT SUM(amount)
    FROM transactions
    WHERE transaction_type = 'Income'
    """
).fetchone()[0] or 0

total_expense = cursor.execute(
    """
    SELECT SUM(amount)
    FROM transactions
    WHERE transaction_type = 'Expense'
    """
).fetchone()[0] or 0

balance = total_income - total_expense

st.subheader("📊 Overall Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "💰 Total Income",
        f"₹{total_income:,.2f}"
    )

with col2:
    st.metric(
        "💸 Total Expense",
        f"₹{total_expense:,.2f}"
    )

with col3:
    st.metric(
        "💵 Balance",
        f"₹{balance:,.2f}"
    )

st.subheader("📅 Date-wise Expenses")

selected_date = st.date_input(
    "Select Date",
    key="expense_report_date"
)

selected_date = str(selected_date)

date_expenses = cursor.execute(
    """
    SELECT
        person_name,
        description,
        amount,
        category
    FROM transactions
    WHERE transaction_type = 'Expense'
    AND date = ?
    ORDER BY id DESC
    """,
    (selected_date,)
).fetchall()

if date_expenses:

    st.write(
        f"### 📅 Expenses on {selected_date}"
    )

    st.dataframe(
        date_expenses,
        column_config={
            "person_name": "Person Name",
            "description": "Description",
            "amount": "Amount",
            "category": "Category"
        },
        hide_index=True
    )

else:
    st.info("No expenses found for this date.")

date_total_expense = cursor.execute(
    """
    SELECT SUM(amount)
    FROM transactions
    WHERE transaction_type = 'Expense'
    AND date = ?
    """,
    (selected_date,)
).fetchone()[0] or 0

st.metric(
    "💸 Selected Date Total Expense",
    f"₹{date_total_expense:,.2f}"
)

st.subheader("👥 Person-wise Expenses")

person_data = cursor.execute(
    """
    SELECT
        person_name,
        SUM(amount)
    FROM transactions
    WHERE transaction_type = 'Expense'
    AND date = ?
    GROUP BY person_name
    ORDER BY SUM(amount) DESC
    """,
    (selected_date,)
).fetchall()

if person_data:

    for person, person_amount in person_data:
        st.write(
            f"**{person}** → ₹{person_amount:,.2f}"
        )

else:
    st.info("No person-wise expenses found.")

if person_data:

    person_count = len(person_data)

    each_person_share = (
        date_total_expense / person_count
    )

    st.subheader("⚖️ Equal Share")

    st.metric(
        "Each Person Share",
        f"₹{each_person_share:,.2f}"
    )

    st.subheader("🤝 Settlement")

    for person, paid_amount in person_data:

        difference = (
            paid_amount - each_person_share
        )

        if difference > 0:
            st.success(
                f"{person} → Receive ₹{difference:,.2f}"
            )

        elif difference < 0:
            st.warning(
                f"{person} → Pay ₹{abs(difference):,.2f}"
            )

        else:
            st.info(
                f"{person} → Settled ✅"
            )

st.subheader("📋 All Transactions")

all_data = cursor.execute(
    """
    SELECT
        id,
        transaction_type,
        person_name,
        description,
        amount,
        category,
        date
    FROM transactions
    ORDER BY id DESC
    """
).fetchall()

st.dataframe(
    all_data,
    column_config={
        "id": "ID",
        "transaction_type": "Type",
        "person_name": "Person Name",
        "description": "Description",
        "amount": "Amount",
        "category": "Category",
        "date": "Date"
    },
    hide_index=True
)

st.subheader("🗑️ Delete All Data")

confirm_delete = st.checkbox(
    "I understand that all transaction data will be deleted."
)

if st.button("🗑️ Delete All Data"):

    if confirm_delete:

        cursor.execute("DELETE FROM transactions")
        conn.commit()

        st.success(
            "All Transaction Data Deleted Successfully! 🗑️"
        )

        st.rerun()

    else:
        st.warning(
            "Please confirm before deleting all data."
        )

conn.close()
