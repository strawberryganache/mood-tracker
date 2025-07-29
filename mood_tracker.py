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
 
#Title
st.title("🧘 Mental Health Mood Tracker")
st.markdown("Track your daily mood, add a note, and reflect on your well-being over time.")

# Username

st.sidebar.title("Welcome!")
username = st.sidebar.text_input("Enter your username:", value="", max_chars=20)

if username:
    st.session_state["username"] = username
    st.sidebar.success(f"Logged in as: {username}")

    section = st.sidebar.radio("Go to", [
        "New Entry",
        "Mood History",
        "Recent Entries",
        "Mood Summary",
        "Play Game"
    ])
    
else:
    st.stop()

if section == "New Entry":
    
    # Input
    st.subheader(f"Hi {username}, how are you feeling today?")
    mood = st.radio("Mood", ["😊 Happy", "😐 Neutral", "😢 Sad"])
    note = st.text_area("Add a short note (optional)")
    
    if st.button("Save Entry"):
    
        if note.strip():
            sentiment = sia.polarity_scores(note)["compound"]
        else:
            if mood == "😊 Happy":
                sentiment = 0.5
            elif mood == "😐 Neutral":
                sentiment = 0.0
            elif mood == "😢 Sad":
                sentiment = -0.5
            st.markdown("No note entered. Using selected mood to estimate your feeling.")
            
        c.execute("INSERT INTO moods (username, date, mood, note, sentiment) VALUES (?, ?, ?, ?, ?)",
                  (username, str(date.today()), mood, note, sentiment))
        conn.commit()
        st.success("Your mood has been saved! 💚")
    
    # Suggestions    
        if mood == "😊 Happy":
            st.info("💡 Suggestion: Awesome! Keep spreading the positivity!")
        elif mood == "😐 Neutral":
            st.info("💡 Suggestion: Try doing something you enjoy today!")
        elif mood == "😢 Sad":
            st.info("💡 Suggestion: Take it easy. Talk to a friend or take a walk to lift your spirits.")

if section == "Mood History":

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

if section == "Recent Entries":

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

if section == "Mood Summary":

    #Show Mood Summary
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
    
            emoji_labels = [f"{label} ({counts[label]})" for label in labels]
    
            # Pie Chart
            fig, ax = plt.subplots()
            ax.pie(values, labels=emoji_labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
    
            # Most Common Mood
            most_common = counts.most_common(1)[0][0]
            st.markdown(f"🌟 Your most frequent mood is: **{most_common}**")
        else:
            st.info("Not enough mood data to show pie chart yet.")

if section == "Play Game":

    # Tic-Tac-Toe Functions
    def create_board():
        return [[" " for _ in range(3)] for _ in range(3)]
    
    def check_win(board, player):
        for i in range(3):
            if all(board[i][j] == player for j in range(3)) or \
               all(board[j][i] == player for j in range(3)):
                return True
        if all(board[i][i] == player for i in range(3)) or \
           all(board[i][2 - i] == player for i in range(3)):
            return True
        return False
    
    def get_empty_positions(board):
        return [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]
    
    def computer_move(board):
        return random.choice(get_empty_positions(board))
    
    # Start Game 
    st.subheader("🎯 How About a Game to Cheer Up?")
    st.markdown ("Let's play Tic-Tac-Toe!")
    
    # Game Mode Selection
    mode = st.selectbox("Choose Game Mode:", ["Play vs Computer 💻", "Play vs Friend 👥"])
    
    # Session State to Store Game State
    if "board" not in st.session_state:
        st.session_state.board = create_board()
    if "turn" not in st.session_state:
        st.session_state.turn = "X"
    if "game_over" not in st.session_state:
        st.session_state.game_over = False
    if "winner" not in st.session_state:
        st.session_state.winner = ""
    
    # Handle Move
    def handle_move(i, j):
        if st.session_state.board[i][j] == " " and not st.session_state.game_over:
            st.session_state.board[i][j] = st.session_state.turn
    
            if check_win(st.session_state.board, st.session_state.turn):
                st.session_state.game_over = True
                st.session_state.winner = st.session_state.turn
            elif not get_empty_positions(st.session_state.board):
                st.session_state.game_over = True
                st.session_state.winner = "Tie"
            else:
                st.session_state.turn = "O" if st.session_state.turn == "X" else "X"
    
    # Display the Board
    for i in range(3):
        cols = st.columns(3)
        for j in range(3):
            cell = st.session_state.board[i][j]
            with cols[j]:
                if cell == " " and not st.session_state.game_over:
                    if st.button(" ", key=f"{i}-{j}"):
                        handle_move(i, j)
    
                        # If Playing vs Computer and it's O's Turn
                        if mode == "Play vs Computer 💻" and st.session_state.turn == "O" and not st.session_state.game_over:
                            row, col = computer_move(st.session_state.board)
                            handle_move(row, col)
                else:
                    st.markdown(f"### {cell}")
    
    # Show result
    if st.session_state.game_over:
        if st.session_state.winner == "Tie":
            st.success("It's a tie!")
        else:
            st.success(f"{'Computer 💻' if (mode == 'Play vs Computer 💻' and st.session_state.winner == 'O') else 'Player ' + st.session_state.winner} wins! 🎉")
    
    # Restart button
    if st.button("🔁 Restart Game"):
        st.session_state.board = create_board()
        st.session_state.turn = "X"
        st.session_state.game_over = False
        st.session_state.winner = ""
    
    conn.close()
