import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ------------------------------
# Page Configuration
# ------------------------------
st.set_page_config(page_title="💰 Expense Tracker", layout="wide")

# ------------------------------
# Initialize Session State
# ------------------------------
if "expenses" not in st.session_state:
    st.session_state["expenses"] = []

# ------------------------------
# Sidebar - Add Expense
# ------------------------------
st.sidebar.header("✨ Add New Expense")

with st.sidebar.form("expense_form", clear_on_submit=True):
    date = st.date_input("📅 Date", datetime.today())
    category = st.selectbox("📂 Category", ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"])
    amount = st.number_input("💵 Amount (₹)", min_value=1.0, step=10.0)
    description = st.text_input("📝 Description")
    submitted = st.form_submit_button("➕ Add Expense")
    
    if submitted:
        st.session_state["expenses"].append(
            {"Date": date, "Category": category, "Amount": amount, "Description": description}
        )
        st.sidebar.success("🎉 Expense Added!")

# ------------------------------
# Main Dashboard
# ------------------------------
st.title("🌈 Personal Expense Dashboard")

if st.session_state["expenses"]:
    df = pd.DataFrame(st.session_state["expenses"])

    # Quick Stats
    total_expense = df["Amount"].sum()
    top_category = df.groupby("Category")["Amount"].sum().idxmax()
    highest_spend = df["Amount"].max()

    # Gradient Summary Cards
    col1, col2, col3 = st.columns(3)

    col1.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #FF9A9E, #FAD0C4); 
                    padding:20px; border-radius:15px; text-align:center; color:white;">
            <h3>💰 Total Expenses</h3>
            <h2>₹{total_expense:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    col2.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #A18CD1, #FBC2EB); 
                    padding:20px; border-radius:15px; text-align:center; color:white;">
            <h3>⭐ Top Category</h3>
            <h2>{top_category}</h2>
        </div>
        """, unsafe_allow_html=True)

    col3.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #FDCB82, #F7797D); 
                    padding:20px; border-radius:15px; text-align:center; color:white;">
            <h3>🔥 Highest Spend</h3>
            <h2>₹{highest_spend:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Filters
    st.subheader("🔍 Filter Your Expenses")
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        category_filter = st.multiselect("📂 Select Categories", df["Category"].unique(), default=df["Category"].unique())
    with col_filter2:
        date_filter = st.date_input("📅 Select Date Range", [])

    # Apply Filters
    filtered_df = df[df["Category"].isin(category_filter)]
    if date_filter and len(date_filter) == 2:
        filtered_df = filtered_df[(filtered_df["Date"] >= date_filter[0]) & (filtered_df["Date"] <= date_filter[1])]

    # Expense Table
    st.subheader("📋 Expense Records")
    st.dataframe(filtered_df, use_container_width=True)

    # Charts
    st.subheader("📊 Expense Analysis")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        if not filtered_df.empty:
            fig1 = px.pie(filtered_df, names="Category", values="Amount", title="Expenses by Category",
                          color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        if not filtered_df.empty:
            fig2 = px.bar(filtered_df, x="Date", y="Amount", color="Category",
                          title="Daily Expenses by Category", barmode="group",
                          color_discrete_sequence=px.colors.qualitative.Vivid)
            st.plotly_chart(fig2, use_container_width=True)

    # Budget Tracker
    st.subheader("🎯 Budget Tracker")
    budget = st.number_input("Set Monthly Budget (₹)", min_value=1000.0, step=500.0)
    if budget > 0:
        progress = total_expense / budget
        st.progress(min(progress, 1.0))  
        if total_expense > budget:
            st.error("⚠️ You have exceeded your budget!")
        else:
            st.success(f"✅ Within Budget. Remaining: ₹{budget - total_expense:,.2f}")

    # Download Option
    st.download_button("📥 Download CSV", data=filtered_df.to_csv(index=False), file_name="expenses.csv", mime="text/csv")

else:
    st.info("💡 No expenses yet. Add your first expense from the sidebar!")
