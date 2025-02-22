import streamlit as st

# Main Dashboard
st.title("AIMS - All-In-One Life Management System")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Health", "Fitness", "Finance", "Career", "Personal Development", "Social", "Hobbies", "Physical Store", "Digital Store"])

# Dashboard Page
if page == "Dashboard":
    st.header("Life Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sleep", "7 hrs", "-1 hr from target")
    with col2:
        st.metric("Spending", "$500", "+$100 from budget")
    with col3:
        st.metric("Steps", "8,000", "2,000 to goal")

    st.subheader("Upcoming Deadlines")
    st.write("1. Project X - Due in 3 days")
    st.write("2. Gym Session - Tomorrow at 7 AM")