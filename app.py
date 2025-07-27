import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Baseball Stats Explorer", layout="wide")

# --- Title ---
st.title("⚾ MLB Player Stats Explorer")
st.markdown("Explore and compare current player statistics for both hitters and pitchers.")

# --- Load Data ---
@st.cache_data
def load_data():
    # Replace this with your real data path
    df = pd.read_csv("data/mlb_player_stats.csv")

    # Example: Assume there's a 'Type' column that says 'Batter' or 'Pitcher'
    return df

df = load_data()

# --- Filters ---
player_type = st.sidebar.selectbox("Select Player Type", ["All", "Batter", "Pitcher"])
search_name = st.sidebar.text_input("Search Player Name")

# --- Filtered View ---
if player_type != "All":
    df = df[df["Type"] == player_type]

if search_name:
    df = df[df["Name"].str.contains(search_name, case=False)]

# --- Column Groupings ---
batting_stats = [
    "BA", "OBP", "SLG", "OPS", "BB%", "K%", "1B", "2B", "3B", "HR", "RBI", "SB"
]
pitching_stats = [
    "ERA", "FIP", "WHIP", "K/9", "BB%", "K%", "H/9", "HR/9", "W", "L", "SV"
]
common_stats = ["WAR", "Name", "Team", "Position", "Type"]

# --- Sort & Display ---
with st.sidebar:
    sort_by = st.selectbox("Sort players by", df.columns)
    ascending = st.checkbox("Sort Ascending", value=False)

df_sorted = df.sort_values(by=sort_by, ascending=ascending)

# --- Display Table ---
st.subheader(f"Showing {len(df_sorted)} players")
columns_to_display = common_stats + batting_stats + pitching_stats
columns_to_display = [col for col in columns_to_display if col in df_sorted.columns]

st.dataframe(df_sorted[columns_to_display], use_container_width=True)
