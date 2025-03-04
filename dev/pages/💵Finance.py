import streamlit as st
import pandas as pd
import datetime
from utils.database import finance_db

# Initialize DB
conn = finance_db()
c = conn.cursor()

# Page Title
st.title("💰 Finances")

# Sidebar for Navigation
st.sidebar.header("Navigation")
option = st.sidebar.radio("Choose an action", ["Log Transactions", "View Trends", "Set Budget", "Upload Transactions", "Net Worth", "Goals", "Export Data"])

# Log Transactions Form
if option == "Log Transactions":
    st.header("Log Your Transactions")
    tab1, tab2 = st.tabs(["💰 Income", "💸 Expense"])

    with tab1:
        with st.form("income_form"):
            date = st.date_input("Date", datetime.date.today())
            category = st.selectbox("Category", ["💼 Earned", "📈 Portfolio", "💰 Passive", "🎁 Gift"])
            amount = st.number_input("Amount", min_value=0.0, step=0.01)
            description = st.text_input("Description (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO transactions_data (date, type, category, amount, description) VALUES (?, ?, ?, ?, ?)",
                        (date, "income", category, amount, description))
                conn.commit()
                st.success("Transaction logged successfully!")
            
    with tab2:
        with st.form("expense_form"):
            date = st.date_input("Date", datetime.date.today())
            category = st.selectbox("Category", ["🍔 Food", "🚗 Transport", "🎉 Entertainment", "🏠 Rent", "💡 Utilities"])
            amount = st.number_input("Amount", min_value=0.0, step=0.01)
            description = st.text_input("Description (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO transactions_data (date, type, category, amount, description) VALUES (?, ?, ?, ?, ?)",
                        (date, "expense", category, amount, description))
                conn.commit()
                st.success("Transaction logged successfully!")
    

# View Trends
elif option == "View Trends":
    st.header("Financial Trends")
    finance_data = pd.read_sql("SELECT * FROM transactions_data", conn)
    budgets = pd.read_sql("SELECT * FROM budgets", conn)

    # Use tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Income Breakdown", "Expense Breakdown", "Budget Progress"])

    with tab1:
        st.subheader("Income Breakdown")
        if not finance_data.empty:
            income = finance_data[finance_data['type'] == 'income']
            if not income.empty:
                st.write("### Income by Category")
                category_income = income.groupby('category')['amount'].sum().reset_index()
                st.bar_chart(category_income.set_index('category'))
            else:
                st.warning("No income logged yet.")

    with tab2:
        st.subheader("Expense Breakdown")
        if not finance_data.empty:
            expenses = finance_data[finance_data['type'] == 'expense']
            if not expenses.empty:
                st.write("### Spending by Category")
                category_spending = expenses.groupby('category')['amount'].sum().reset_index()
                st.bar_chart(category_spending.set_index('category'))
            else:
                st.warning("No expenses logged yet.")

    with tab3:
        st.subheader("Budget Progress")
        if not budgets.empty:
            # Merge budgets with actual spending
            budget_progress = pd.merge(
                budgets,
                finance_data.groupby('category')['amount'].sum().reset_index(),
                how='left',
                left_on='category',
                right_on='category'
            )
            budget_progress['amount'] = budget_progress['amount'].fillna(0)  # Replace NaN with 0
            budget_progress['progress'] = (budget_progress['amount'] / budget_progress['budget']) * 100

            # Display progress bars
            for _, row in budget_progress.iterrows():
                st.write(f"**{row['category']}**")
                st.progress(row['progress'] / 100)
                st.write(f"Spent: ₹{row['amount']:.2f} / Budget: ₹{row['budget']:.2f} ({row['progress']:.1f}%)")
                if row['amount'] > row['budget']:
                    st.error(f"⚠️ You've exceeded your budget for {row['category']} by ₹{row['amount'] - row['budget']:.2f}!")

# Set Budget
elif option == "Set Budget":
    st.header("Set Your Budget")
    with st.form("budget_form"):
        category = st.selectbox("Category", ["🍔 Food", "🚗 Transport", "🎉 Entertainment", "🏠 Rent", "💡 Utilities"])
        budget = st.number_input("Monthly Budget", min_value=0.0, step=0.01)
        month = st.date_input("Month", datetime.date.today()).strftime('%Y-%m')

        if st.form_submit_button("Set Budget"):
            # Check if a budget already exists for this category and month
            c.execute("SELECT * FROM budgets WHERE category = ? AND month = ?", (category, month))
            existing_budget = c.fetchone()

            if existing_budget:
                # Update existing budget
                c.execute("UPDATE budgets SET budget = ? WHERE id = ?", (budget, existing_budget[0]))
            else:
                # Insert new budget
                c.execute("INSERT INTO budgets (category, budget, month) VALUES (?, ?, ?)",
                          (category, budget, month))
            conn.commit()
            st.success(f"Budget set for {category}: ₹{budget:.2f} for {month}")

# Upload Transactions
elif option == "Upload Transactions":
    st.header("Upload Transaction History")
    uploaded_file = st.file_uploader("Upload CSV File", type="csv")
    if uploaded_file is not None:
        try:
            # Parse CSV file
            transactions = pd.read_csv(uploaded_file)
            st.write("### Preview of Uploaded Data")
            st.dataframe(transactions.head())

            # Save transactions to database
            for _, row in transactions.iterrows():
                c.execute("INSERT INTO transactions_data (date, type, category, amount, description) VALUES (?, ?, ?, ?, ?)",
                          (row['Date'], row['Type'], row['Category'], row['Amount'], row['Description']))
            conn.commit()
            st.success("Transactions uploaded successfully!")
        except Exception as e:
            st.error(f"Error uploading transactions: {e}")

# Net Worth Tracking
elif option == "Net Worth":
    st.header("Net Worth Tracker")
    tab1, tab2, tab3 = st.tabs(["Log Assets", "Log Liabilities", "View Net Worth"])

    with tab1:
        st.subheader("Log Assets")
        with st.form("asset_form"):
            date = st.date_input("Date", datetime.date.today())
            asset_type = st.selectbox("Asset Type", ["💰 Savings", "📈 Investments", "🏠 Property", "🚗 Vehicle"])
            amount = st.number_input("Amount", min_value=0.0, step=0.01)
            description = st.text_input("Description (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO assets (date, type, amount, description) VALUES (?, ?, ?, ?)",
                          (date, asset_type, amount, description))
                conn.commit()
                st.success("Asset logged successfully!")

    with tab2:
        st.subheader("Log Liabilities")
        with st.form("liability_form"):
            date = st.date_input("Date", datetime.date.today())
            liability_type = st.selectbox("Liability Type", ["💳 Credit Card Debt", "🏦 Loan", "📜 Other Debt"])
            amount = st.number_input("Amount", min_value=0.0, step=0.01)
            description = st.text_input("Description (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO liabilities (date, type, amount, description) VALUES (?, ?, ?, ?)",
                          (date, liability_type, amount, description))
                conn.commit()
                st.success("Liability logged successfully!")

    with tab3:
        st.subheader("View Net Worth")
        assets = pd.read_sql("SELECT * FROM assets", conn)
        liabilities = pd.read_sql("SELECT * FROM liabilities", conn)

        if not assets.empty or not liabilities.empty:
            # Calculate total assets and liabilities
            total_assets = assets['amount'].sum()
            total_liabilities = liabilities['amount'].sum()
            net_worth = total_assets - total_liabilities

            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Assets", f"₹{total_assets:,.2f}")
            with col2:
                st.metric("Total Liabilities", f"₹{total_liabilities:,.2f}")
            with col3:
                st.metric("Net Worth", f"₹{net_worth:,.2f}")

            # Plot net worth over time
            if not assets.empty:
                assets['date'] = pd.to_datetime(assets['date'])
                assets = assets.groupby('date')['amount'].sum().reset_index()
            if not liabilities.empty:
                liabilities['date'] = pd.to_datetime(liabilities['date'])
                liabilities = liabilities.groupby('date')['amount'].sum().reset_index()

            # Merge assets and liabilities
            net_worth_data = pd.merge(
                assets,
                liabilities,
                how='outer',
                on='date',
                suffixes=('_assets', '_liabilities'))
            net_worth_data = net_worth_data.fillna(0)  # Replace NaN with 0
            net_worth_data['net_worth'] = net_worth_data['amount_assets'] - net_worth_data['amount_liabilities']

            # Plot net worth over time
            st.write("### Net Worth Over Time")
            st.line_chart(net_worth_data.set_index('date')['net_worth'])
        else:
            st.warning("No assets or liabilities logged yet.")

# Goal Tracking
elif option == "Goals":
    st.header("Financial Goals")
    tab1, tab2 = st.tabs(["Set Goal", "Track Goals"])

    with tab1:
        st.subheader("Set a New Goal")
        with st.form("goal_form"):
            name = st.text_input("Goal Name")
            target_amount = st.number_input("Target Amount", min_value=0.0, step=0.01)
            deadline = st.date_input("Deadline")

            if st.form_submit_button("Set Goal"):
                c.execute("INSERT INTO goals (name, target_amount, current_amount, deadline) VALUES (?, ?, ?, ?)",
                          (name, target_amount, 0.0, deadline))
                conn.commit()
                st.success("Goal set successfully!")

    with tab2:
        st.subheader("Track Your Goals")
        goals = pd.read_sql("SELECT * FROM goals", conn)

        if not goals.empty:
            for _, row in goals.iterrows():
                st.write(f"**{row['name']}**")
                st.write(f"Target: ₹{row['target_amount']:.2f} by {row['deadline']}")
                progress = (row['current_amount'] / row['target_amount']) * 100
                st.progress(progress / 100)
                st.write(f"Current: ₹{row['current_amount']:.2f} ({progress:.1f}%)")
                if row['current_amount'] >= row['target_amount']:
                    st.success(f"🎉 Congratulations! You've achieved your goal: {row['name']}!")
                elif row['current_amount'] / row['target_amount'] >= 0.9:
                    st.warning(f"⚠️ You're close to achieving your goal: {row['name']}!")

                # Add a form to update the current amount
                with st.form(f"update_goal_{row['id']}"):
                    update_amount = st.number_input("Add Amount", min_value=0.0, step=0.01, key=f"update_{row['id']}")
                    if st.form_submit_button("Update"):
                        new_amount = row['current_amount'] + update_amount
                        c.execute("UPDATE goals SET current_amount = ? WHERE id = ?", (new_amount, row['id']))
                        conn.commit()
                        st.success(f"Updated {row['name']} to ₹{new_amount:.2f}")
        else:
            st.warning("No goals set yet.")

# Export Data
elif option == "Export Data":
    st.header("Export Your Data")

    # Export Transactions
    transactions = pd.read_sql("SELECT * FROM transactions_data", conn)
    if not transactions.empty:
        st.write("### Transactions")
        st.dataframe(transactions)
        csv = transactions.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Transactions as CSV",
            data=csv,
            file_name="transactions.csv",
            mime="text/csv",
        )
    else:
        st.warning("No transactions logged yet.")

    # Export Budgets
    budgets = pd.read_sql("SELECT * FROM budgets", conn)
    if not budgets.empty:
        st.write("### Budgets")
        st.dataframe(budgets)
        csv = budgets.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Budgets as CSV",
            data=csv,
            file_name="budgets.csv",
            mime="text/csv",
        )
    else:
        st.warning("No budgets set yet.")

    # Export Assets
    assets = pd.read_sql("SELECT * FROM assets", conn)
    if not assets.empty:
        st.write("### Assets")
        st.dataframe(assets)
        csv = assets.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Assets as CSV",
            data=csv,
            file_name="assets.csv",
            mime="text/csv",
        )
    else:
        st.warning("No assets logged yet.")

    # Export Liabilities
    liabilities = pd.read_sql("SELECT * FROM liabilities", conn)
    if not liabilities.empty:
        st.write("### Liabilities")
        st.dataframe(liabilities)
        csv = liabilities.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Liabilities as CSV",
            data=csv,
            file_name="liabilities.csv",
            mime="text/csv",
        )
    else:
        st.warning("No liabilities logged yet.")

    # Export Goals
    goals = pd.read_sql("SELECT * FROM goals", conn)
    if not goals.empty:
        st.write("### Goals")
        st.dataframe(goals)
        csv = goals.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Goals as CSV",
            data=csv,
            file_name="goals.csv",
            mime="text/csv",
        )
    else:
        st.warning("No goals set yet.")