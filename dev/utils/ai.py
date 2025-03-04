import streamlit as st
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

def predict_mood(health_data):
    """
    Predict mood based on sleep, water, and nutrition data.
    """
    try:
        # Encode mood labels (e.g., "😊 Happy" -> 0, "😢 Sad" -> 1)
        label_encoder = LabelEncoder()
        health_data['mood_encoded'] = label_encoder.fit_transform(health_data['mood'])

        # Features: sleep, water, calories, protein, carbs, fats
        X = health_data[['sleep', 'water', 'calories', 'protein', 'carbs', 'fats']]
        y = health_data['mood_encoded']

        # Train a logistic regression model (better for classification)
        model = LogisticRegression()
        model.fit(X, y)

        # Example prediction
        example_input = [[7, 8, 2000, 50, 300, 70]]  # sleep, water, calories, protein, carbs, fats
        predicted_mood_encoded = model.predict(example_input)[0]  # Predict discrete label
        return label_encoder.inverse_transform([predicted_mood_encoded])[0]
    except Exception as e:
        st.error(f"Failed to predict mood: {e}")
        return "Unknown"


def categorize_expense(description):
    """
    Auto-categorize expenses based on description.
    """
    if "uber" in description.lower() or "lyft" in description.lower():
        return "🚗 Transport"
    elif "restaurant" in description.lower() or "coffee" in description.lower():
        return "🍔 Food"
    elif "netflix" in description.lower() or "spotify" in description.lower():
        return "🎉 Entertainment"
    else:
        return "💡 Utilities"


def get_project_insights(projects, tasks):
    """
    Generate AI-powered insights for projects and tasks.
    """
    insights = []

    # Rule 1: Identify projects with no tasks
    for _, project in projects.iterrows():
        project_tasks = tasks[tasks['project_id'] == project['id']]
        if project_tasks.empty:
            insights.append(f"⚠️ **{project['name']}** has no tasks. Add tasks to start making progress!")

    # Rule 2: Identify overdue tasks
    today = datetime.today().date()
    overdue_tasks = tasks[(pd.to_datetime(tasks['deadline']).dt.date < today) & (tasks['completed'] == 0)]
    if not overdue_tasks.empty:
        insights.append("🚨 **Overdue Tasks**:")
        for _, task in overdue_tasks.iterrows():
            project_name = projects[projects['id'] == task['project_id']]['name'].values[0]
            insights.append(f"- **{task['name']}** in **{project_name}** is overdue (deadline: {task['deadline']}).")

    # Rule 3: Identify projects with low progress
    low_progress_projects = projects[projects['progress'] < 50]
    if not low_progress_projects.empty:
        insights.append("🐌 **Projects with Low Progress**:")
        for _, project in low_progress_projects.iterrows():
            insights.append(f"- **{project['name']}** is only {project['progress']:.1f}% complete. Focus on completing tasks!")

    # Rule 4: Suggest tasks to prioritize
    upcoming_tasks = tasks[pd.to_datetime(tasks['deadline']).dt.date >= today]
    if not upcoming_tasks.empty:
        insights.append("📅 **Tasks to Prioritize**:")
        for _, task in upcoming_tasks.iterrows():
            project_name = projects[projects['id'] == task['project_id']]['name'].values[0]
            insights.append(f"- **{task['name']}** in **{project_name}** (deadline: {task['deadline']}).")

    return insights

def get_personal_development_insights(journal_entries, networking_activities, skills, books, courses, goals):
    """
    Generate AI-powered insights for personal development.
    """
    insights = []

    # Rule 1: Analyze journal entries for recurring themes
    if not journal_entries.empty:
        common_words = ["stress", "happy", "productive", "tired", "excited"]
        word_counts = {word: 0 for word in common_words}
        for entry in journal_entries['entry']:
            for word in common_words:
                if word in entry.lower():
                    word_counts[word] += 1

        insights.append("📝 **Journal Insights**:")
        for word, count in word_counts.items():
            if count > 0:
                insights.append(f"- The word '{word}' appears {count} times in your journal entries.")

    # Rule 2: Suggest networking opportunities
    if not networking_activities.empty:
        last_activity_date = pd.to_datetime(networking_activities['date']).max()
        days_since_last_activity = (datetime.today().date() - last_activity_date.date()).days
        if days_since_last_activity > 30:
            insights.append("🤝 **Networking Suggestion**:")
            insights.append(f"- It's been {days_since_last_activity} days since your last networking activity. Consider attending an event or reaching out to a contact!")

    # Rule 3: Suggest skills, books, or courses based on goals
    if not goals.empty:
        for _, goal in goals.iterrows():
            if goal['progress'] < 50:
                insights.append(f"🎯 **Goal Progress**:")
                insights.append(f"- Your goal **{goal['name']}** is only {goal['progress']:.1f}% complete. Consider focusing on it!")

    # Rule 4: Suggest books or courses based on skills
    if not skills.empty:
        for _, skill in skills.iterrows():
            if skill['progress'] < 50:
                insights.append(f"📚 **Skill Development**:")
                insights.append(f"- You're learning **{skill['name']}** (progress: {skill['progress']:.1f}%). Check out related books or courses to improve!")

    return insights