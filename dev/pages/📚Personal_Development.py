import streamlit as st
import pandas as pd
import datetime
from utils.database import personal_development_db
from utils.ai import get_personal_development_insights

# Initialize DB
conn = personal_development_db()
c = conn.cursor()

# Page Title
st.title("📚 Personal Development")

# Sidebar for Navigation
st.sidebar.header("Navigation")
option = st.sidebar.radio("Choose an action", ["Skills", "Books", "Courses", "Goals", "Journaling", "Networking", "AI Insights"])

# Skills
if option == "Skills":
    st.header("Skill Tracking")
    tab1, tab2 = st.tabs(["Log Skill", "View Skills"])

    with tab1:
        st.subheader("Log a New Skill")
        with st.form("skill_form"):
            name = st.text_input("Skill Name")
            start_date = st.date_input("Start Date", datetime.date.today())
            target_date = st.date_input("Target Date (optional)", datetime.date.today())
            progress = st.number_input("Progress (%)", min_value=0.0, max_value=100.0, step=0.1)
            notes = st.text_area("Notes (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO skills (name, start_date, target_date, progress, notes) VALUES (?, ?, ?, ?, ?)",
                          (name, start_date, target_date, progress, notes))
                conn.commit()
                st.success("Skill logged successfully!")

    with tab2:
        st.subheader("View Skills")
        skills = pd.read_sql("SELECT * FROM skills", conn)

        if not skills.empty:
            st.write("### Skills Overview")
            for _, row in skills.iterrows():
                st.write(f"**{row['name']}**")
                st.progress(row['progress'] / 100)
                st.write(f"Progress: {row['progress']:.1f}%")
                st.write(f"Start Date: {row['start_date']}")
                st.write(f"Target Date: {row['target_date']}")
                st.write(f"Notes: {row['notes']}")
        else:
            st.warning("No skills logged yet.")

# Books
elif option == "Books":
    st.header("Book Tracking")
    tab1, tab2 = st.tabs(["Log Book", "View Books"])

    with tab1:
        st.subheader("Log a New Book")
        with st.form("book_form"):
            title = st.text_input("Title")
            author = st.text_input("Author")
            start_date = st.date_input("Start Date", datetime.date.today())
            target_date = st.date_input("Target Date (optional)", datetime.date.today())
            progress = st.number_input("Progress (%)", min_value=0.0, max_value=100.0, step=0.1)
            notes = st.text_area("Notes (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO books (title, author, start_date, target_date, progress, notes) VALUES (?, ?, ?, ?, ?, ?)",
                          (title, author, start_date, target_date, progress, notes))
                conn.commit()
                st.success("Book logged successfully!")

    with tab2:
        st.subheader("View Books")
        books = pd.read_sql("SELECT * FROM books", conn)

        if not books.empty:
            st.write("### Books Overview")
            for _, row in books.iterrows():
                st.write(f"**{row['title']}** by {row['author']}")
                st.progress(row['progress'] / 100)
                st.write(f"Progress: {row['progress']:.1f}%")
                st.write(f"Start Date: {row['start_date']}")
                st.write(f"Target Date: {row['target_date']}")
                st.write(f"Notes: {row['notes']}")
        else:
            st.warning("No books logged yet.")

# Courses
elif option == "Courses":
    st.header("Course Tracking")
    tab1, tab2 = st.tabs(["Log Course", "View Courses"])

    with tab1:
        st.subheader("Log a New Course")
        with st.form("course_form"):
            name = st.text_input("Course Name")
            platform = st.text_input("Platform (e.g., Coursera, Udemy)")
            start_date = st.date_input("Start Date", datetime.date.today())
            target_date = st.date_input("Target Date (optional)", datetime.date.today())
            progress = st.number_input("Progress (%)", min_value=0.0, max_value=100.0, step=0.1)
            notes = st.text_area("Notes (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO courses (name, platform, start_date, target_date, progress, notes) VALUES (?, ?, ?, ?, ?, ?)",
                          (name, platform, start_date, target_date, progress, notes))
                conn.commit()
                st.success("Course logged successfully!")

    with tab2:
        st.subheader("View Courses")
        courses = pd.read_sql("SELECT * FROM courses", conn)

        if not courses.empty:
            st.write("### Courses Overview")
            for _, row in courses.iterrows():
                st.write(f"**{row['name']}** on {row['platform']}")
                st.progress(row['progress'] / 100)
                st.write(f"Progress: {row['progress']:.1f}%")
                st.write(f"Start Date: {row['start_date']}")
                st.write(f"Target Date: {row['target_date']}")
                st.write(f"Notes: {row['notes']}")
        else:
            st.warning("No courses logged yet.")

# Goals
elif option == "Goals":
    st.header("Personal Development Goals")
    tab1, tab2 = st.tabs(["Set Goal", "Track Goals"])

    with tab1:
        st.subheader("Set a New Goal")
        with st.form("goal_form"):
            name = st.text_input("Goal Name")
            target_date = st.date_input("Target Date")
            progress = st.number_input("Progress (%)", min_value=0.0, max_value=100.0, step=0.1)
            notes = st.text_area("Notes (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO personal_goals (name, target_date, progress, notes) VALUES (?, ?, ?, ?)",
                          (name, target_date, progress, notes))
                conn.commit()
                st.success("Goal set successfully!")

    with tab2:
        st.subheader("Track Your Goals")
        goals = pd.read_sql("SELECT * FROM personal_goals", conn)

        if not goals.empty:
            for _, row in goals.iterrows():
                st.write(f"**{row['name']}**")
                st.write(f"Target Date: {row['target_date']}")
                st.progress(row['progress'] / 100)
                st.write(f"Progress: {row['progress']:.1f}%")
                st.write(f"Notes: {row['notes']}")
        else:
            st.warning("No goals set yet.")

# Journaling
elif option == "Journaling":
    st.header("Journaling")
    tab1, tab2 = st.tabs(["Log Entry", "View Entries"])

    with tab1:
        st.subheader("Log a New Journal Entry")
        with st.form("journal_form"):
            date = st.date_input("Date", datetime.date.today())
            entry = st.text_area("Journal Entry")
            notes = st.text_area("Notes (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO journal_entries (date, entry, notes) VALUES (?, ?, ?)",
                          (date, entry, notes))
                conn.commit()
                st.success("Journal entry logged successfully!")

    with tab2:
        st.subheader("View Journal Entries")
        entries = pd.read_sql("SELECT * FROM journal_entries", conn)

        if not entries.empty:
            st.write("### Journal Entries Overview")
            for _, row in entries.iterrows():
                st.write(f"**Date: {row['date']}**")
                st.write(f"Entry: {row['entry']}")
                st.write(f"Notes: {row['notes']}")
                st.write("---")
        else:
            st.warning("No journal entries logged yet.")

# Networking
elif option == "Networking":
    st.header("Networking")
    tab1, tab2 = st.tabs(["Log Activity", "View Activities"])

    with tab1:
        st.subheader("Log a New Networking Activity")
        with st.form("networking_form"):
            event_name = st.text_input("Event Name")
            date = st.date_input("Date", datetime.date.today())
            notes = st.text_area("Notes (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO networking_activities (event_name, date, notes) VALUES (?, ?, ?)",
                          (event_name, date, notes))
                conn.commit()
                st.success("Networking activity logged successfully!")

    with tab2:
        st.subheader("View Networking Activities")
        activities = pd.read_sql("SELECT * FROM networking_activities", conn)

        if not activities.empty:
            st.write("### Networking Activities Overview")
            for _, row in activities.iterrows():
                st.write(f"**Event: {row['event_name']}**")
                st.write(f"Date: {row['date']}")
                st.write(f"Notes: {row['notes']}")
                st.write("---")
        else:
            st.warning("No networking activities logged yet.")

# AI Insights
elif option == "AI Insights":
    st.header("AI-Powered Insights")
    journal_entries = pd.read_sql("SELECT * FROM journal_entries", conn)
    networking_activities = pd.read_sql("SELECT * FROM networking_activities", conn)
    skills = pd.read_sql("SELECT * FROM skills", conn)
    books = pd.read_sql("SELECT * FROM books", conn)
    courses = pd.read_sql("SELECT * FROM courses", conn)
    goals = pd.read_sql("SELECT * FROM personal_goals", conn)

    if not journal_entries.empty or not networking_activities.empty or not skills.empty or not books.empty or not courses.empty or not goals.empty:
        insights = get_personal_development_insights(journal_entries, networking_activities, skills, books, courses, goals)
        if insights:
            for insight in insights:
                st.write(insight)
        else:
            st.success("🎉 Everything looks great! Keep up the good work!")
    else:
        st.warning("No data logged yet.")