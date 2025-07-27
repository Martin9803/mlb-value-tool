import pandas as pd
import os
import numpy as np

# === Stat Descriptions ===
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

mlb_teams = sorted([
    "ARI", "ATL", "BAL", "BOS", "CHC", "CHW", "CIN", "CLE", "COL", "DET",
    "HOU", "KCR", "LAA", "LAD", "MIA", "MIL", "MIN", "NYM", "NYY", "OAK",
    "PHI", "PIT", "SDP", "SEA", "SFG", "STL", "TBR", "TEX", "TOR", "WSN"
])

# === Load Data ===
def load_data(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filename)

    if not os.path.exists(full_path):
        print(f"\n❌ Data file not found at: {full_path}\n")
        print("📂 Files in project folder:", os.listdir(base_dir))
        exit()

    return pd.read_csv(full_path, encoding="ISO-8859-1")

# === Main App ===
def main():
    print("⚾ Welcome to the 2025 MLB Value Explorer (All-Star Break Edition)\n")

    while True:
        player_type = input("Do you want to view [B]atters or [P]itchers? ").strip().upper()
        if player_type in ['B', 'P']:
            break
        else:
            print("Please type 'B' for Batters or 'P' for Pitchers.")

    if player_type == 'B':
        filename = "batters_2025_2025.csv"
        stat_dict = batting_stats
    else:
        filename = "pitchers_2025_2025.csv"
        stat_dict = pitching_stats

    df = load_data(filename)

    while True:
        custom_player = input("\nWould you like to look up a specific player? [Y/N] or [Q]uit: ").strip().upper()
        if custom_player == 'Q':
            print("Goodbye!")
            return
        elif custom_player not in ['Y', 'N']:
            print("Please type 'Y' for yes, 'N' for no, or 'Q' to quit.")
            continue

        if custom_player == 'Y':
            print("\nSelect a team:")
            for idx, team in enumerate(mlb_teams, 1):
                print(f" {idx}. {team}")

            while True:
                try:
                    team_choice = int(input("\nChoose team (number): "))
                    if 1 <= team_choice <= len(mlb_teams):
                        team_selected = mlb_teams[team_choice - 1]
                        break
                    else:
                        print("Invalid team number.")
                except ValueError:
                    print("Enter a number.")

            players = df[df["Team"] == team_selected].reset_index(drop=True)
            print(f"\nPlayers on {team_selected}:")
            for idx, name in enumerate(players["Name"], 1):
                print(f" {idx}. {name}")

            while True:
                try:
                    player_choice = int(input("\nChoose player (number): "))
                    if 1 <= player_choice <= len(players):
                        player_row = players.iloc[player_choice - 1]
                        break
                    else:
                        print("Invalid player number.")
                except ValueError:
                    print("Enter a number.")

            print("\nAvailable Stats:")
            for i, (stat, desc) in enumerate(stat_dict.items(), 1):
                print(f" {i}. {stat} — {desc}")

            while True:
                try:
                    stat_choice = int(input("\nSelect stat to rank by (number): "))
                    if 1 <= stat_choice <= len(stat_dict):
                        chosen_stat = list(stat_dict.keys())[stat_choice - 1]
                        break
                    else:
                        print("Invalid number.")
                except ValueError:
                    print("Please enter a number.")

            df = df[(df["Salary (Per Season)"] > 0) & (df[chosen_stat].notna())]

            if player_type == 'B':
                df = df[df["PA"] >= 20]
                df["Value"] = df[chosen_stat] / df["Salary (Per Season)"] * df["PA"]
            else:
                df = df[df["IP"] >= 5]
                df["Value"] = df[chosen_stat] / df["Salary (Per Season)"] * df["IP"]

            df["Value"] = df["Value"] * 1e6
            df_sorted = df.sort_values(by="Value", ascending=False).reset_index(drop=True)
            df_sorted.index += 1

            player_name = player_row["Name"]
            player_stat = player_row[chosen_stat]

            if player_name in df_sorted["Name"].values:
                rank = df_sorted[df_sorted["Name"] == player_name].index[0]
                print(f"\n📊 {player_name} is ranked {rank} in {chosen_stat} based on our value formula and has {player_stat} this season.")
            else:
                print(f"\n⚠️ {player_name} does not meet the qualification threshold for ranking.")
        else:
            print("\nAvailable Stats to Compare Value:")
            for i, (stat, desc) in enumerate(stat_dict.items(), 1):
                print(f" {i}. {stat} — {desc}")

            stat_list = list(stat_dict.keys())

            while True:
                try:
                    choice = int(input("\nSelect a stat to evaluate by (number): "))
                    if 1 <= choice <= len(stat_list):
                        chosen_stat = stat_list[choice - 1]
                        if chosen_stat == "Salary":
                            print("\n❌ Cannot evaluate value by salary. Please choose a performance stat.")
                            return
                        break
                    else:
                        print("Invalid number.")
                except ValueError:
                    print("Please enter a number.")

            df = df[(df["Salary (Per Season)"] > 0) & (df[chosen_stat].notna())]

            if player_type == 'B':
                df = df[df["PA"] >= 20]
                df["Value"] = (df[chosen_stat] * np.log1p(df["PA"])) / (np.sqrt(df["Salary (Per Season)"]) * np.log1p(df["G"]))
            else:
                df = df[df["IP"] >= 5]
                df["Value"] = (df[chosen_stat] * np.log1p(df["IP"])) / (np.sqrt(df["Salary (Per Season)"]) * np.log1p(df["G"]))

            df["Value"] = df["Value"] * 1e6
            df_sorted = df.sort_values(by="Value", ascending=False).reset_index(drop=True)
            df_sorted.index += 1

            print(f"\n🧠 Stat: {chosen_stat} — {stat_dict.get(chosen_stat, '')}")
            output_df = df_sorted[["Name", "Team", "Salary (Per Season)", chosen_stat]]

            print(f"\n📋 Ranked List of All Qualified Players by '{chosen_stat}'")
            print(output_df.to_string(index=True, formatters={
                "Salary (Per Season)": "${:,.0f}".format
            }))

if __name__ == "__main__":
    main()


















