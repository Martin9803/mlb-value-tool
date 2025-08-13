# File: scripts/update_data.R
# Purpose: pull season-to-date MLB leaders from FanGraphs and overwrite
#          batters_2025_2025.csv and pitchers_2025_2025.csv in repo root.
# Notes:
# - Preserves your existing Salary (Per Season) by merging from current CSVs.
# - Drops aggregated rows like "2 Tms" / "3 Tms".
# - Uses FanGraphs CSV export with a friendly User-Agent.

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(stringr)
  library(httr)
})

# ---- FanGraphs URLs (season-to-date) ----
# You can adjust enddate/qual in these URLs as needed.
BATTERS_URL  <- "https://www.fangraphs.com/leaders/major-league?pageitems=2000000000&startdate=2025-03-27&enddate=2025-08-09&season=2025&season1=2025&ind=0&team=0&pos=all&type=8&stats=bat&qual=1&month=1000"
PITCHERS_URL <- "https://www.fangraphs.com/leaders/major-league?pageitems=2000000000&startdate=2025-03-27&enddate=2025-08-09&season=2025&season1=2025&ind=0&team=0&pos=all&type=8&stats=pit&qual=1&month=1000"

# ---- Helpers ----
safe_select <- function(df, cols) dplyr::select(df, dplyr::any_of(cols))

fetch_fg_csv <- function(url) {
  u <- if (grepl("csv=1", url, fixed = TRUE)) url else paste0(url, "&csv=1")
  resp <- httr::GET(u, httr::user_agent("mlb-value-tool (github.com/Martin9803/mlb-value-tool)"))
  httr::stop_for_status(resp)
  readr::read_csv(httr::content(resp, as = "raw"), show_col_types = FALSE)
}

merge_salary <- function(new_df, existing_path) {
  if (file.exists(existing_path)) {
    sal <- readr::read_csv(existing_path, show_col_types = FALSE) %>%
      safe_select(c("Name", "Team", "Salary (Per Season)")) %>%
      mutate(Name = str_squish(Name), Team = str_trim(Team))
    new_df <- new_df %>%
      mutate(Name = str_squish(Name)) %>%
      left_join(sal, by = c("Name", "Team"))
  } else {
    new_df <- new_df %>% mutate(`Salary (Per Season)` = NA_real_)
  }
  # Drop legacy index columns if they exist
  new_df %>% select(-any_of(c("Unnamed: 0", "Unnamed: 0.1")))
}

# ---- Download ----
message("Downloading FanGraphs leaderboards…")
bat_raw <- fetch_fg_csv(BATTERS_URL)
pit_raw <- fetch_fg_csv(PITCHERS_URL)

# ---- Normalize columns your app expects ----
# Batters
bat <- bat_raw %>%
  rename(Name = "Name", Team = "Team") %>%
  mutate(Team = str_trim(Team)) %>%
  filter(!Team %in% c("2 Tms", "3 Tms")) %>%
  safe_select(c(
    "Name", "Team", "G", "PA", "R", "RBI", "SB", "BB%", "K%",
    "AVG", "OBP", "SLG", "HR", "WAR"
  ))

# Pitchers
pit <- pit_raw %>%
  rename(Name = "Name", Team = "Team") %>%
  mutate(Team = str_trim(Team)) %>%
  filter(!Team %in% c("2 Tms", "3 Tms")) %>%
  safe_select(c(
    "Name", "Team", "G", "IP", "W", "L", "SV", "K/9", "BB/9", "HR/9",
    "ERA", "FIP", "WAR"
  ))

# ---- Merge salary from current CSVs ----
bat <- merge_salary(bat, "batters_2025_2025.csv")
pit <- merge_salary(pit, "pitchers_2025_2025.csv")

# ---- Write out ----
readr::write_csv(bat, "batters_2025_2025.csv")
readr::write_csv(pit, "pitchers_2025_2025.csv")

message(sprintf("Saved batters_2025_2025.csv (%s rows)", nrow(bat)))
message(sprintf("Saved pitchers_2025_2025.csv (%s rows)", nrow(pit)))

