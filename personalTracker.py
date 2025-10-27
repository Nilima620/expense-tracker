import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# -------------------- Database Setup --------------------
def init_db():
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL,
                    category TEXT,
                    note TEXT,
                    date TEXT
                )''')
    conn.commit()
    conn.close()

# -------------------- Core Functions --------------------
def add_expense(amount, category, note):
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT INTO expenses (amount, category, note, date) VALUES (?, ?, ?, ?)",
              (amount, category, note, date))
    conn.commit()
    conn.close()

def get_expenses():
    conn = sqlite3.connect("expenses.db")
    df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC", conn)
    conn.close()
    return df

def delete_expense(expense_id):
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

# -------------------- Streamlit App --------------------
init_db()
st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")
st.title("💰 Expense Tracker (Web App)")

# Sidebar for navigation
menu = ["Add Expense", "View Expenses", "Summary", "Trend"]
choice = st.sidebar.selectbox("📌 Menu", menu)

if choice == "Add Expense":
    st.subheader("➕ Add New Expense")
    amount = st.number_input("Enter amount", min_value=1.0, step=0.5)
    category = st.text_input("Enter category (Food, Travel, Bills, etc.)")
    note = st.text_area("Enter note (optional)")
    if st.button("Add Expense"):
        add_expense(amount, category, note)
        st.success(f"✅ Expense of {amount} added under {category}")

elif choice == "View Expenses":
    st.subheader("📋 All Expenses")
    df = get_expenses()
    st.dataframe(df)

    if not df.empty:
        exp_id = st.number_input("Enter Expense ID to delete", min_value=1, step=1)
        if st.button("🗑️ Delete Expense"):
            delete_expense(exp_id)
            st.warning("Expense deleted successfully!")
            st.experimental_rerun()

elif choice == "Summary":
    st.subheader("📊 Monthly Summary")
    month = st.text_input("Enter month (MM)", value=datetime.now().strftime("%m"))

    df = get_expenses()
    if not df.empty:
        df['month'] = pd.to_datetime(df['date']).dt.strftime("%m")
        summary = df[df['month'] == month].groupby("category")["amount"].sum()

        if not summary.empty:
            st.write(summary)

            # Pie Chart
            fig, ax = plt.subplots()
            ax.pie(summary, labels=summary.index, autopct='%1.1f%%', startangle=90)
            ax.set_title(f"Expense Distribution - Month {month}")
            st.pyplot(fig)
        else:
            st.info("No expenses found for this month.")

elif choice == "Trend":
    st.subheader("📈 Monthly Spending Trend")
    df = get_expenses()
    if not df.empty:
        df['month'] = pd.to_datetime(df['date']).dt.strftime("%m")
        trend = df.groupby("month")["amount"].sum()

        fig, ax = plt.subplots()
        ax.bar(trend.index, trend.values)
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Expense")
        ax.set_title("Monthly Spending Trend")
        st.pyplot(fig)
    else:
        st.info("No data available to plot trend.")
