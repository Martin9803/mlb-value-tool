suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(stringr)
  library(httr)
})

# ---- FanGraphs URLs (season-to-date) ----
# You can tweak the dates or qual= if you like.
BATTERS_URL  <- "https://www.fangraphs.com/leaders/major-league?pageitems=2000000000&startdate=2025-03-27&enddate=2025-10-01&season=2025&season1=2025&ind=0&team=0&pos=all&type=8&stats=bat&qual=0&month=1000"
PITCHERS_URL <- "https://www.fangraphs.com/leaders/major-league?pageitems=2000000000&startdate=2025-03-27&enddate=2025-10-01&season=2025&season1=2025&ind=0&team=0&pos=all&type=8&stats=pit&qual=0&month=1000"

fetch_fg_csv <- function(url) {
  u <- if (grepl("csv=1", url, fixed = TRUE)) url else paste0(url, "&csv=1")
  resp <- httr::GET(u, httr::user_agent("mlb-value-tool (github.com/Martin9803/mlb-value-tool)"))
  httr::stop_for_status(resp)
  readr::read_csv(httr::content(resp, as = "raw"), show_col_types = FALSE)
}

message("Downloading FanGraphs leaderboards...")
bat_raw <- fetch_fg_csv(BATTERS_URL)
pit_raw <- fetch_fg_csv(PITCHERS_URL)

# ---- Keep/rename only the columns your app uses ----
bat <- bat_raw %>%
  rename(Name = "Name", Team = "Team") %>%
  mutate(Team = str_trim(Team)) %>%
  filter(!Team %in% c("2 Tms", "3 Tms")) %>%
  select(
    Name, Team, G, PA, R, RBI, SB, `BB%`, `K%`,
    AVG, OBP, SLG, HR, WAR
  )

pit <- pit_raw %>%
  rename(Name = "Name", Team = "Team") %>%
  mutate(Team = str_trim(Team)) %>%
  filter(!Team %in% c("2 Tms", "3 Tms")) %>%
  select(
    Name, Team, G, IP, W, L, SV, `K/9`, `BB/9`, `HR/9`,
    ERA, FIP, WAR
  )

# ---- Merge Salary from current CSVs so the app retains salaries ----
merge_salary <- function(new_df, existing_path) {
  if (file.exists(existing_path)) {
    sal <- readr::read_csv(existing_path, show_col_types = FALSE) %>%
      select(Name, Team, `Salary (Per Season)`) %>%
      mutate(
        Name = str_squish(Name),
        Team = str_trim(Team)
      )
    new_df <- new_df %>%
      mutate(Name = str_squish(Name)) %>%
      left_join(sal, by = c("Name", "Team"))
  } else {
    new_df <- new_df %>% mutate(`Salary (Per Season)` = NA_real_)
  }
  new_df
}

bat <- merge_salary(bat, "batters_2025_2025.csv")
pit <- merge_salary(pit, "pitchers_2025_2025.csv")

# ---- Write out the refreshed CSVs ----
readr::write_csv(bat, "batters_2025_2025.csv")
readr::write_csv(pit, "pitchers_2025_2025.csv")

message("Done. Files written: batters_2025_2025.csv, pitchers_2025_2025.csv")
