import streamlit as st
import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect("ai_memory.db")
cursor = conn.cursor()

# Fetch data from the memory table
cursor.execute("SELECT query, response, feedback FROM memory")
data = cursor.fetchall()

# Convert to DataFrame
df = pd.DataFrame(data, columns=["Query", "Response", "Feedback"])

# Streamlit Dashboard
st.title("📊 Athena Feedback Dashboard")
st.write("Analyze how Athena is performing and track feedback.")

# Show feedback summary
st.subheader("Feedback Summary")
positive_feedback = df[df["Feedback"] == "good"].shape[0]
negative_feedback = df[df["Feedback"] == "corrected"].shape[0]

total_queries = len(df)
st.metric("Total Queries", total_queries)
st.metric("Positive Feedback (👍)", positive_feedback)
st.metric("Corrections Made (👎)", negative_feedback)

# Show full query history
st.subheader("📜 Query & Response History")
st.dataframe(df)

# Close database connection
conn.close()
