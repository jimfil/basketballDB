def display_main_menu():
    print("Press one of the following options:")
    print("1: View Teams")
    print("2: Create Team")
    print("3: Stats")
    print("4: Exit")
    valid_answers = ["1", "2", "3", "4"] 
    
    answer = input("Awaiting Response: ")
    while answer not in valid_answers:
        print("Please Input a Valid Number (1-4)")
        answer = input("Awaiting Response: ")
    return answer

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

def display_match_stats(page_num, stats):
    """Displays a formatted page of match events."""
    print(f"\n\tPage {page_num}\t")
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
        print("No teams found.")
        return
    
    print("\n--- Team List ---")
    print(f"{'ID':<10}{'Name'}")
    print("-" * 25)
    for team in teams:
        print(f"{team['id']:<10}{team['name']}")
    print("-----------------")

def get_stats_menu():
    print("What stats would you like to view?")
    print("1: Player Stats")
    print("2: Match Stats")
    print("3: Shot Analysis")
    print("4: Match Score")
    print("5: Back")
    valid_answers = ["1", "2", "3", "4","5"]
    answer = input("Awaiting Response: ")
    while answer not in valid_answers:
        print("Please Input a Valid Number (1-5)")
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
