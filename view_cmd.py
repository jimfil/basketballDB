def get_menu_choice(title, options):
    """Generic function to display a menu and get a valid choice."""
    print(f"\n{title}")
    for key, value in options.items():
        print(f"{key}: {value}")

    valid_answers = options.keys()
    prompt = f"Please Input a Valid Number ({list(valid_answers)[0]}-{list(valid_answers)[-1]})"

    answer = input("Awaiting Response: ").strip()
    while answer not in valid_answers:
        print(prompt)
        answer = input("Awaiting Response: ")
    return answer

def display_shot_percentage_menu():
    return get_menu_choice("Select Shot Type", {"1": "Free Throws", "2": "2 Point Shoots", "3": "3 Point Shoots", "4": "Back"})

def display_years(years):
    print("Seasons:")
    for year in years: print(year)


def display_standings(standings_list):
    print(f"\n{'Pos':<5}{'Team':<25}{'W':<5}{'L':<5}")
    print("-" * 65)
    for i, team in enumerate(standings_list):
        print(f"{i+1:<5}{team['name']:<25}{team['wins']:<5}{team['losses']:<5}")
    input("\nPress [Enter] to continue...")

def display_phases(phases):
    print("\nSelect a Phase:")
    for p in phases:
        p_name = "Group Stage" if p['phase_id'] == 1 else "Finals/Knockout"
        print(f"{p['phase_id']}: {p_name} (ID: {p['id']})")
    return input("Enter Phase ID: ")

def display_player_stats(stats):
    """Displays a formatted page of player stats."""
    print(f"{'Game':<8}{'Event Made':<28}{'Time'}")
    if not stats:
        print("No more stats found for this Player.")
        return
    for row in stats:
        match_id, event_name, game_time = row
        print(f"{match_id:<8}{event_name:<28}{str(game_time)}") 

def display_match_stats(stats):
    """Displays a formatted page of match events."""
    print(f"{'Team:':<24}{'Number Shirt':<15}{'Player':<20}{'Event Made':<28}{'Time'}")
    if not stats:
        print("No more events found for this Match.")
        return
    for row in stats:
        shirt_number, last_name, event_name, game_time, team_name = row
        print(f"{team_name:<24}{shirt_number:<15}{last_name:<20}{event_name:<28}{str(game_time)}") 

def display_shot_analysis(analysis_data):
    """Displays the analysis of shot percentages."""
    print(f"\n--- {analysis_data['title']} for Player {analysis_data['player_id']} {analysis_data['scope']} ---")
    print(f"Shots Made:     {analysis_data['made']}")
    print(f"Shots Missed:   {analysis_data['missed']}")
    print(f"Total Attempts: {analysis_data['total']}")
    print(f"Percentage:     {analysis_data['percentage']:.2f}%")
    print("----------------------------------------------------")

def display_match_score(match_id, scores):
    """Displays the final score for a match."""
    print(f"\n--- Final Score for Match {match_id} ---")
    for team_id, score in scores.items():
        # In a more advanced version, you could fetch team names here
        print(f"Team {team_id}: {score}")
    print("------------------------------------")

def display_teams(teams):
    """Displays a list of teams in a formatted way."""
    if not teams:
        return
    print("--- Team List ---")
    print(f"{'ID':<10}{'Name'}")
    for team in teams:
        print(f"{team["id"]:<10}{team["name"]}")

def display_players_paginated(players):
    """Displays a paginated list of players."""
    if not players:
        print("No more players found.")
        return

    print(f"{'Speciality':<20}{'ID':<10}{'First Name':<20}{'Last Name':<20}{'Number Shirt':<20}{'Team ID'}")
    for player in players:
        print(f"{player[0]:<20}{player[1]:<10}{player[2]:<20}{player[3]:<20}{player[4]:<20}{player[5]:<20}")
    print("")

def display_matches_for_team(team_name, matches):
    """Displays a list of matches for a specific team."""
    print(f"\n--- Matches for {team_name[0]["name"]} ---")
    if not matches:
        print("No matches found for this team.")
        return

    print(f"{'ID':<10}{'Date':<15}{'Home Team ID':<15}{'Away Team ID'}")
    print("-" * 55)
    for match in matches:
        print(f"{match['id']:<10}{str(match['match_date']):<15}{match['home_team_id']:<15}{match['away_team_id']}")


def get_year_input(): return input("Please input the League's Year, or 'q' to go back:")

def get_player_info_input():
    """Prompts user for new player details and returns them as a dict."""
    print("\nEnter new player details (leave first name blank to cancel):")
    first_name = input("First Name: ").strip()
    if not first_name:
        return None
    last_name = input("Last Name: ").strip()
    while not last_name:
        print("Last name cannot be empty.")
        last_name = input("Last Name: ").strip()
    
    shirt_num = input("Shirt Number: ").strip()
    while not shirt_num.isdigit():
        print("Shirt number must be a valid number.")
        shirt_num = input("Shirt Number: ").strip()

    return {"first_name": first_name, "last_name": last_name, "shirt_num": int(shirt_num)}

def get_team_name_input(): return input("Enter the new team's name (or leave blank to cancel): ").strip()
def id_selection_input(): return input("\nEnter the ID you want to select, press [Enter] for next page, or 'q' to quit: ").strip()

        
def print_select_from_list(example):print(f"\nPlease select a {example} from the list below.")
def print_no_more_found(example):print(f"No more {example} found.")
def print_no_group_phase_found():print("No group phase found for the selected season.")
def print_no_knockout_rounds_found():print("No rounds found for the knock out phase.")
def print_team_creation_success(team_name): print(f"Team '{team_name}' created successfully.")
def print_player_creation_success(first_name, last_name): print(f"Player '{first_name} {last_name}' created successfully.")
def print_operation_cancelled(): print("Operation cancelled.")
def invalid_input():print("Invalid input. Please try again.")
