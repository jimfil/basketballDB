def display_main_menu():
    print("Press one of the following options:")
    print("1: Team Menu")
    print("2: View League")
    print("3: Stats")
    print("4: Exit")
    valid_answers = ["1", "2", "3", "4"] 
    
    answer = input("Awaiting Response: ")
    while answer not in valid_answers:
        print("Please Input a Valid Number (1-4)")
        answer = input("Awaiting Response: ")
    return answer

def display_team_menu(): 
    """Displays the team management menu and gets user input."""
    print("\n--- Team Management ---")
    print("1: View Teams")
    print("2: Create Team")
    print("3: Back to Main Menu")
    valid_answers = ["1", "2", "3"]
    answer = input("Awaiting Response: ")
    while answer not in valid_answers:
        print("Please Input a Valid Number (1-3)")
        answer = input("Awaiting Response: ")
    return answer

def display_stats_menu():
    print("What stats would you like to view?")
    print("1: Player Stats")
    print("2: Match Stats")
    print("3: Shot Analysis")
    print("4: Back")
    valid_answers = ["1", "2", "3", "4"]
    answer = input("Awaiting Response: ")
    while answer not in valid_answers:
        print("Please Input a Valid Number (1-4)")
        answer = input("Awaiting Response: ")
    return answer

def display_shot_percentage_menu():
    print("1: Free Throws")
    print("2: 2 Point Shoots")
    print("3: 3 Point Shoots")
    print("4: Back to Main Menu")
    valid_answers = ["1", "2", "3", "4"]
    answer = input("Awaiting Response: ")
    while answer not in valid_answers:
        print("Please Input a Valid Number (1-4)")
        answer = input("Awaiting Response: ")
    return answer

def display_league_menu():
    print("--- League Menu ---")
    print("1: View Standings (Group Stage)")
    print("2: View Match Schedule by Phase")
    print("3: Change Season")
    print("4: Back")
    valid_answers = ["1", "2", "3","4"]
    answer = input("Awaiting Response: ")
    while answer not in valid_answers:
        print("Please Input a Valid Number (1-4)")
        answer = input("Awaiting Response: ")
    return answer

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

def display_player_stats(page_num, stats):
    """Displays a formatted page of player stats."""
    print(f"\nPage {page_num}\t")
    print(f"{'Game':<8}{'Event Made':<28}{'Time'}")
    if not stats:
        print("No more stats found for this Player.")
        return
    for row in stats:
        match_id, event_name, game_time = row
        print(f"{match_id:<8}{event_name:<28}{str(game_time)}")
    return input("\nPress [Enter] for more, or type 'q' to return to Stats menu: ")    


def display_match_stats(page_num, stats):
    """Displays a formatted page of match events."""
    print(f"\nPage {page_num}\t")
    print(f"{'Team:':<24}{'Number Shirt':<15}{'Player':<20}{'Event Made':<28}{'Time'}")
    if not stats:
        print("No more events found for this Match.")
        return
    for row in stats:
        shirt_number, last_name, event_name, game_time, team_name = row
        print(f"{team_name:<24}{shirt_number:<15}{last_name:<20}{event_name:<28}{str(game_time)}")
    
    return input("\nPress [Enter] for more, or type 'q' to return to Stats menu: ")    

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
        print("End of teams list.")
        return 'q'
    
    print("--- Team List ---")
    print(f"{'ID':<10}{'Name'}")
    for team in teams:
        print(f"{team[0]:<10}{team[1]}")
    return input("\nPress [Enter] for next page, or 'q' to quit: ").strip()



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
    
    return input("\nPress [Enter] for next page, or 'q' to quit: ").strip()


def get_year_input(): return input("Please input the League's Year, or 'q' to go back:")
def id_selection_input(): return input("\nEnter the ID you want to select, press [Enter] for next page, or 'q' to quit: ").strip()

        
def print_select_from_list(example):print(f"Please select a {example} from the list below.")
def print_no_more_found(example):print(f"No more {example} found.Exiting...")
def invalid_input():print("Invalid input. Please try again.")

