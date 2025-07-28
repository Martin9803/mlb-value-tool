import pandas as pd
import streamlit as st
import numpy as np

st.set_page_config(page_title="MLB 2025 Value Explorer", layout="centered")
st.title("⚾ MLB 2025 Value Explorer")
st.caption("A simple app to explore player value based on salary and performance.")

batting_stats = {
    "WAR": "Wins Above Replacement – A catch-all stat estimating how many more wins this player provides compared to a replacement-level player",
    "SLG": "Slugging Percentage – Measures power by calculating total bases per at-bat",
    "OBP": "On-base Percentage – How often the player gets on base, whether by hit, walk, or hit by pitch",
    "HR": "Home Runs – Total home runs hit, showing power and run potential",
    "RBI": "Runs Batted In – Number of runners the player drove in to score",
    "SB": "Stolen Bases – Times the player stole a base, showing speed and baserunning",
    "R": "Runs – How often the player crossed home plate to score",
    "BB%": "Walk Percentage – How often the player earns a walk (base on balls) per plate appearance",
    "K%": "Strikeout Percentage – How often the player strikes out, lower is better",
    "AVG": "Batting Average – How often the player gets a hit per at-bat"
}

pitching_stats = {
    "W": "Wins – Games where the pitcher was in the game when their team took the lead for good",
    "L": "Losses – Games where the pitcher allowed the go-ahead run that led to a loss",
    "SV": "Saves – When a relief pitcher successfully protects a lead to end the game",
    "K/9": "Strikeouts per 9 innings – How many batters the pitcher strikes out every 9 innings",
    "BB/9": "Walks per 9 innings – How many batters the pitcher walks every 9 innings",
    "HR/9": "Home Runs per 9 innings – How many homers the pitcher allows per 9 innings",
    "ERA": "Earned Run Average – How many earned runs the pitcher gives up every 9 innings",
    "FIP": "Fielding Independent Pitching – A version of ERA that only looks at things the pitcher controls (strikeouts, walks, home runs)",
    "WAR": "Wins Above Replacement – An estimate of the pitcher’s total contribution to the team compared to a replacement-level pitcher"
}

player_type = st.selectbox("Choose player type:", ["", "Batters", "Pitchers"])

if player_type:
    filename = "batters_2025_2025.csv" if player_type == "Batters" else "pitchers_2025_2025.csv"

    try:
        df = pd.read_csv(filename, encoding="ISO-8859-1")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

    stat_dict = batting_stats if player_type == "Batters" else pitching_stats

    df = df[df["Salary (Per Season)"] > 0]
    if player_type == "Batters":
        df = df[df["PA"] >= 50]
    else:
        df = df[df["IP"] >= 10]

    st.markdown("""
        ### 🧮 How the Value Formula Works
        We want to see how much **value** a player provides compared to how much they're paid. So we use this formula:

        - We take the stat you care about (like Home Runs or WAR)
        - We give a small bonus for playing time (more games or innings played)
        - We divide that by how much money they make

        **The higher the score, the more performance you're getting for every dollar spent!**
    """)

    mode = st.radio("Would you like to look up a specific player or rank all players?", ["", "Player Lookup", "Rank All Players"])

    if mode == "Player Lookup":
        teams = [""] + sorted(df["Team"].unique())
        team_selected = st.selectbox("Select Team:", teams)

        if team_selected:
            players = [""] + df[df["Team"] == team_selected]["Name"].tolist()
            player_selected = st.selectbox("Select Player:", players)

            if player_selected:
                stat = st.selectbox("Select Stat to Rank Player by:", [""] + list(stat_dict.keys()))

                if stat:
                    st.markdown(f"**{stat}**: {stat_dict[stat]}")

                    df = df[df[stat].notna()]
                    if player_type == "Batters":
                        df["Value"] = (df[stat] * np.log1p(df["PA"])) / (np.sqrt(df["Salary (Per Season)"]) * np.log1p(df["G"]))
                    else:
                        df["Value"] = (df[stat] * np.log1p(df["IP"])) / (np.sqrt(df["Salary (Per Season)"]) * np.log1p(df["G"]))

                    df_sorted = df.sort_values(by="Value", ascending=False).reset_index(drop=True)
                    df_sorted.index += 1

                    if player_selected in df_sorted["Name"].values:
                        row = df_sorted[df_sorted["Name"] == player_selected].iloc[0]
                        rank = df_sorted[df_sorted["Name"] == player_selected].index[0]
                        st.success(f"📊 {player_selected} is ranked #{rank} in {stat} with a season stat of {row[stat]}.")
                    else:
                        st.warning("This player does not meet the qualification threshold.")

    elif mode == "Rank All Players":
        stat = st.selectbox("Choose a stat to rank players by:", [""] + list(stat_dict.keys()))

        if stat:
            with st.expander("📘 Stat Descriptions"):
                st.write(f"**{stat}**: {stat_dict[stat]}")

            df = df[df[stat].notna()]
            if player_type == "Batters":
                df["Value"] = (df[stat] * np.log1p(df["PA"])) / (np.sqrt(df["Salary (Per Season)"]) * np.log1p(df["G"]))
            else:
                df["Value"] = (df[stat] * np.log1p(df["IP"])) / (np.sqrt(df["Salary (Per Season)"]) * np.log1p(df["G"]))

            df_sorted = df.sort_values(by="Value", ascending=False).reset_index(drop=True)
            df_sorted.index += 1

            df_display = df_sorted[["Name", "Team", "Salary (Per Season)", stat]].copy()
            df_display["Salary (Per Season) (Raw)"] = df_sorted["Salary (Per Season)"]
            df_display["Salary (Per Season) (Formatted)"] = df_display["Salary (Per Season) (Raw)"].apply(lambda x: f"${x:,.0f}")

            st.subheader(f"📋 Ranked Players by {stat}")
            st.dataframe(df_display.sort_values(by="Salary (Per Season) (Raw)", ascending=False)[["Name", "Team", "Salary (Per Season) (Formatted)", stat]].rename(columns={"Salary (Per Season) (Formatted)": "Salary (Per Season)"}))
else:
    st.info("Please select a player type to begin.")








