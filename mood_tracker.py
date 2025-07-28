import streamlit as st
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

# Title and Logo
st.title("🧘 Mental Health Mood Tracker")
st.logo(🧘)

# Input
st.write("How are you feeling today?")
mood = st.radio("Mood", ["😊 Happy", "😐 Neutral", "😢 Sad"])
note = st.text_area("Add a short note (optional)")

if st.button("Save Entry"):
    sentiment = sia.polarity_scores(note)["compound"] if note else 0.0
    c.execute("INSERT INTO moods (date, mood, note, sentiment) VALUES (?, ?, ?, ?)",
              (str(date.today()), mood, note, sentiment))
    conn.commit()
    st.success("Your mood has been saved! 💚")

# Show Data
if st.checkbox("Show mood chart"):
    c.execute("SELECT date, sentiment FROM moods ORDER BY date")
    data = c.fetchall()
    if data:
        dates = [x[0] for x in data]
        scores = [x[1] for x in data]
        
        plt.clf()
        plt.figure(figsize=(10, 6))
        plt.plot(dates, scores, marker='o', color='mediumseagreen')
        plt.xticks(rotation=45)
        plt.title("Mood Sentiment Over Time")
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
if st.button("Get Positive Quote"):
    quote = get_random_quote()
    st.info(quote)

# Display Recent Entries
if st.checkbox("Show recent entries"):
    c.execute("SELECT date, mood, note, sentiment FROM moods ORDER BY date DESC LIMIT 5")
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

conn.close()
