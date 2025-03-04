import streamlit as st
import pandas as pd
import datetime
from utils.database import projects_db
from utils.ai import get_project_insights

# Initialize DB
conn = projects_db()
c = conn.cursor()

# Page Title
st.title("💼 Projects Tracker")

# Sidebar for Navigation
st.sidebar.header("Navigation")
option = st.sidebar.radio("Choose an action", ["Projects", "Tasks", "Time Logs", "AI Insights"])

# Projects
if option == "Projects":
    st.header("Projects")
    tab1, tab2 = st.tabs(["Log Project", "View Projects"])

    with tab1:
        st.subheader("Log a New Project")
        with st.form("project_form"):
            name = st.text_input("Project Name")
            type = st.selectbox("Type", ["Personal", "Business", "Research", "Skill Development", "Content", "Collaboration"])
            status = st.selectbox("Status", ["Planning", "In Progress", "Completed"])
            start_date = st.date_input("Start Date", datetime.date.today())
            deadline = st.date_input("Deadline (optional)", datetime.date.today())
            notes = st.text_area("Notes (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO projects (name, type, status, start_date, deadline, notes) VALUES (?, ?, ?, ?, ?, ?)",
                          (name, type, status, start_date, deadline, notes))
                conn.commit()
                st.success("Project logged successfully!")

    with tab2:
        st.subheader("View Projects")
        projects = pd.read_sql("SELECT * FROM projects", conn)

        if not projects.empty:
            st.write("### Projects Overview")
            st.dataframe(projects)

            st.write("### Project Progress")
            for _, row in projects.iterrows():
                st.write(f"**{row['name']}**")
                st.progress(row['progress'] / 100)
                st.write(f"Progress: {row['progress']:.1f}%")
        else:
            st.warning("No projects logged yet.")

# Tasks
elif option == "Tasks":
    st.header("Tasks")
    tab1, tab2 = st.tabs(["Log Task", "View Tasks"])

    with tab1:
        st.subheader("Log a New Task")
        with st.form("task_form"):
            project_id = st.number_input("Project ID", min_value=1, step=1)
            name = st.text_input("Task Name")
            deadline = st.date_input("Deadline (optional)", datetime.date.today())
            notes = st.text_area("Notes (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO tasks (project_id, name, deadline, notes) VALUES (?, ?, ?, ?)",
                          (project_id, name, deadline, notes))
                conn.commit()

                 # Update project progress
                c.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ?", (project_id,))
                total_tasks = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND completed = 1", (project_id,))
                completed_tasks = c.fetchone()[0]
                progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
                c.execute("UPDATE projects SET progress = ? WHERE id = ?", (progress, project_id))
                conn.commit()

                st.success("Task logged successfully!")

    with tab2:
        st.subheader("View Tasks")
        tasks = pd.read_sql("SELECT * FROM tasks", conn)

        if not tasks.empty:
            st.write("### Tasks Overview")
            for _, row in tasks.iterrows():
                col1, col2 = st.columns([1, 4])
                with col1:
                    completed = st.checkbox("Completed", value=bool(row['completed']), key=f"task_{row['id']}")
                with col2:
                    st.write(f"**{row['name']}**")
                    st.write(f"Project ID: {row['project_id']}")
                    st.write(f"Deadline: {row['deadline']}")
                    st.write(f"Notes: {row['notes']}")

                # Update task completion status
                if completed != bool(row['completed']):
                    c.execute("UPDATE tasks SET completed = ? WHERE id = ?", (int(completed), row['id']))
                    conn.commit()

                    # Update project progress
                    c.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ?", (row['project_id'],))
                    total_tasks = c.fetchone()[0]
                    c.execute("SELECT COUNT(*) FROM tasks WHERE project_id = ? AND completed = 1", (row['project_id'],))
                    completed_tasks = c.fetchone()[0]
                    progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
                    c.execute("UPDATE projects SET progress = ? WHERE id = ?", (progress, row['project_id']))
                    conn.commit()

                    st.success("Task status updated!")
        else:
            st.warning("No tasks logged yet.")

# Time Logs
elif option == "Time Logs":
    st.header("Time Logs")
    tab1, tab2 = st.tabs(["Log Time", "View Time Logs"])

    with tab1:
        st.subheader("Log Time Spent on a Task")
        with st.form("time_log_form"):
            task_id = st.number_input("Task ID", min_value=1, step=1)
            date = st.date_input("Date", datetime.date.today())
            hours = st.number_input("Hours Spent", min_value=0.0, step=0.1)
            notes = st.text_area("Notes (optional)")

            if st.form_submit_button("Submit"):
                c.execute("INSERT INTO time_logs (task_id, date, hours, notes) VALUES (?, ?, ?, ?)",
                          (task_id, date, hours, notes))
                conn.commit()
                st.success("Time logged successfully!")

    with tab2:
        st.subheader("View Time Logs")
        time_logs = pd.read_sql("SELECT * FROM time_logs", conn)

        if not time_logs.empty:
            st.write("### Time Logs Overview")
            st.dataframe(time_logs)

            st.write("### Total Hours Spent")
            total_hours = time_logs['hours'].sum()
            st.write(f"Total Hours: {total_hours:.1f}")
        else:
            st.warning("No time logs recorded yet.")

# AI Insights
elif option == "AI Insights":
    st.header("AI-Powered Insights")
    projects = pd.read_sql("SELECT * FROM projects", conn)
    tasks = pd.read_sql("SELECT * FROM tasks", conn)

    if not projects.empty or not tasks.empty:
        insights = get_project_insights(projects, tasks)
        if insights:
            for insight in insights:
                st.write(insight)
        else:
            st.success("🎉 Everything looks great! Keep up the good work!")
    else:
        st.warning("No projects or tasks logged yet.")