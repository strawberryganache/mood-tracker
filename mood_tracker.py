import streamlit as st

st.set_page_config(
    page_title="My Mood Tracker",
    page_icon="🧘",
    layout="centered"
)

import sqlite3
from datetime import date
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import matplotlib.pyplot as plt
import random

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Database
def init_db():
    conn = sqlite3.connect('moods.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS moods (
            username TEXT,
            date TEXT,
            mood TEXT,
            note TEXT,
            sentiment REAL
        )
    ''')
    conn.commit()
    return conn, c

# Initialize Database
conn, c = init_db()

# Title
st.title("🧘 Mental Health Mood Tracker")
st.markdown("Track your daily mood, add a note, and reflect on your well-being over time.")

# Username

st.sidebar.title("Login")
username = st.sidebar.text_input("Enter your username:", value="", max_chars=20)

if username:
    st.session_state["username"] = username
    st.sidebar.success(f"Logged in as: {username}")
else:
    st.stop()

# Input
st.subheader(f"Hi {username}, how are you feeling today?")
mood = st.radio("Mood", ["😊 Happy", "😐 Neutral", "😢 Sad"])
note = st.text_area("Add a short note (optional)")

if st.button("Save Entry"):
    sentiment = sia.polarity_scores(note)["compound"] if note else 0.0
    c.execute("INSERT INTO moods (username, date, mood, note, sentiment) VALUES (?, ?, ?, ?, ?)",
              (username, str(date.today()), mood, note, sentiment))
    conn.commit()
    st.success("Your mood has been saved! 💚")

# Suggestions    
    if mood == "😊 Happy":
        st.info("Awesome! Keep spreading the positivity! ☀️")
    elif mood == "😐 Neutral":
        st.info("Try doing something you enjoy today! 🎨📚🎧")
    elif mood == "😢 Sad":
        st.info("It's okay to feel down sometimes. Talk to a friend or take a walk. 💙")

# Show Data
if st.checkbox("Show my mood history"):
    c.execute("SELECT date, sentiment FROM moods WHERE username = ? ORDER BY date", (username,))
    data = c.fetchall()
    if data:
        dates = [x[0] for x in data]
        scores = [x[1] for x in data]
        
        plt.clf()
        plt.figure(figsize=(10, 6))
        plt.plot(dates, scores, marker='o', color='mediumseagreen')
        plt.xticks(rotation=45)
        plt.title(f"{username}'s Sentiment Over Time")
        plt.ylabel("Sentiment Score")
        plt.xlabel("Date")
        plt.grid(True, alpha=0.3)
        st.pyplot(plt)
    else:
        st.info("No mood data available yet. Start tracking your moods!")

#Load Quotes
def get_random_quote():
    try:
        with open("quotes.txt", "r", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
            if quotes:
                return random.choice(quotes)
            else:
                return "Your mind is powerful — take care of it! 💚"
    except FileNotFoundError:
        return "No quotes file found. Please add a quotes.txt."

#Show Quotes
if st.button("Get A Positive Quote"):
    quote = get_random_quote()
    st.info(quote)

# Display Recent Entries
if st.checkbox("Show my recent entries"):
    c.execute("SELECT date, mood, note, sentiment FROM moods WHERE username = ? ORDER BY date DESC LIMIT 5", (username,))
    recent_data = c.fetchall()
    if recent_data:
        st.write("### Recent Entries:")
        for entry in recent_data:
            st.write(f"**{entry[0]}** - {entry[1]}")
            if entry[2]:
                st.write(f"Note: {entry[2]}")
            st.write(f"Sentiment: {entry[3]:.2f}")
            st.write("---")
    else:
        st.info("No entries found.")

if st.checkbox("Show my mood summary"):
    c.execute("SELECT mood FROM moods WHERE username=?", (username,))
    rows = c.fetchall()
    if rows:
        from collections import Counter
        import matplotlib.pyplot as plt

        moods = [r[0] for r in rows]
        counts = Counter(moods)
        labels = list(counts.keys())
        values = list(counts.values())

        # Emoji-friendly labels
        emoji_labels = [f"{label} ({counts[label]})" for label in labels]

        # Pie chart
        fig, ax = plt.subplots()
        ax.pie(values, labels=emoji_labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

        # Most common mood
        most_common = counts.most_common(1)[0][0]
        st.markdown(f"🌟 Your most frequent mood is: **{most_common}**")
    else:
        st.info("Not enough mood data to show pie chart yet.")

conn.close()
