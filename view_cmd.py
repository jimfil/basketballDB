def get_menu_choice(title, options, quit_text="Go Back"):
    """Generic function to display a menu and get a valid choice."""
    print(f"\n{title}")
    for key, value in options.items():
        print(f"{key}: {value}")
    print(f"q: {quit_text}")

    valid_answers = list(options.keys())
    prompt = f"Please Input a Valid Number ({valid_answers[0]}-{valid_answers[-1]})"

    while True:
        answer = input("Awaiting Response: ").strip()
        if answer.lower() == 'q':
            return 'q'
        if answer in valid_answers:
            return answer
        print(prompt)

def display_shot_percentage_menu():
    return get_menu_choice("Select Shot Type", {"1": "Free Throws", "2": "2 Point Shoots", "3": "3 Point Shoots"})

def display_years(years):
    print("Seasons:")
    for year in years: print(year)


def display_standings(standings_list, is_group_stage=False):
    if not is_group_stage or not standings_list or 'group_rank' not in standings_list[0]: # pragma: no cover
        # Fallback to simple display for knockout or old format
        header = f"\n{'Pos':<5}{'Team':<25}{'W':<5}{'L':<5}"
        print(header)
        print("-" * 50)
        for i, team in enumerate(standings_list):
            print(f"{i+1:<5}{team['name']:<25}{team['wins']:<5}{team['losses']:<5}")
    else:
        # Group-aware display logic
        current_group = None
        group_char = 'A'
        for team in standings_list:
            if team['group_identifier'] != current_group:
                current_group = team['group_identifier']
                print(f"\n--- Group {group_char} ---")
                print(f"{'Pos':<5}{'Team':<25}{'W':<5}{'L':<5}{'Status':<15}")
                print("-" * 55)
                group_char = chr(ord(group_char) + 1)

            status = "Qualified" if team['group_rank'] <= 4 else "Not Qualified"
            print(f"{team['group_rank']:<5}{team['name']:<25}{int(team['wins']):<5}{int(team['losses']):<5}{status:<15}")

    input("\nPress [Enter] to continue...")

def get_phase_selection(phases):
    """Displays phases and prompts the user to select a logical phase ID (1 or 2)."""
    print("\nSelect a Phase:")
    valid_ids = []
    for p in phases:
        p_name = "Group Stage" if p['phase_id'] == 1 else "Finals/Knockout"
        print(f"{p['phase_id']}: {p_name} (ID: {p['id']})")
        valid_ids.append(str(p['phase_id']))

    while True:
        choice = input("Enter Phase Number (1 or 2), or 'q' to quit: ").strip()
        if choice.lower() == 'q':
            return None
        if choice in valid_ids:
            return int(choice)
        invalid_input()

def get_round_selection(rounds):
    """Displays rounds for a phase and gets a valid logical round_id selection."""
    if not rounds:
        print("No rounds found for this phase.")
        return None
    
    print("\nSelect a Round:")
    valid_round_ids = []
    for r in rounds:
        print(f"Round Number: {r['round_id']} (ID: {r['id']})")
        valid_round_ids.append(str(r['round_id']))
    
    while True:
        choice = input(f"Enter Round Number ({', '.join(valid_round_ids)}), or 'q' to quit: ").strip()
        if choice.lower() == 'q':
            return None
        if choice in valid_round_ids:
            # Find the database ID for the chosen logical round ID
            for r in rounds:
                if str(r['round_id']) == choice:
                    return r['id']
        invalid_input()

def display_player_stats(stats):
    """Displays a formatted page of player stats."""
    print(f"{'Game':<8}{'Event Made':<28}{'Time'}")
    if not stats:
        print("No more stats found for this Player.")
        return
    for row in stats:
        print(f"{row['match_id']:<8}{row['name']:<28}{str(row['game_time'])}") 

def display_match_stats(stats):
    """Displays a formatted page of match events."""
    print(f"{'ID':<8}{'Team':<24}{'Shirt':<8}{'Player':<20}{'Event':<28}{'Time'}")
    if not stats:
        print("No more events found for this Match.")
        return
    for row in stats:
        print(f"{row['id']:<8}{row['team_name']:<24}{row['shirt_num']:<8}{row['last_name']:<20}{row['event_name']:<28}{str(row['game_time'])}") 

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

    print(f"{'ID':<10}{'First Name':<20}{'Last Name':<20}{'Shirt':<10}{'Speciality':<20}")
    for player in players:
        print(f"{player['id']:<10}{player['first_name']:<20}{player['last_name']:<20}{player['shirt_num']:<10}{player['speciality']:<20}")
    print("")

def display_event_types(events):
    """Displays a list of event types."""
    if not events:
        return
    print("\n--- Event Types ---")
    print(f"{'ID':<10}{'Name'}")
    for event in events:
        print(f"{event['id']:<10}{event['name']}")


def display_matches_for_team(team_name, matches):
    """Displays a list of matches for a specific team."""
    print(f"\n--- Matches for {team_name[0]["name"]} ---")
    if not matches:
        print("No matches found for this team.")
        return

    print(f"{'ID':<10}{'Date':<15}{'Home Team':<25}{'Away Team':<25}")
    print("-" * 75)
    for match in matches:
        print(f"{match['id']:<10}{str(match['match_date']):<15}{match['home_team_name']:<25}{match['away_team_name']:<25}")

def display_referees_paginated(referees):
    """Displays a paginated list of referees."""
    if not referees:
        print("No more referees found.")
        return

    print(f"\n--- Referee List ---")
    print(f"{'ID':<10}{'First Name':<20}{'Last Name':<20}")
    for referee in referees:
        print(f"{referee['id']:<10}{referee['first_name']:<20}{referee['last_name']:<20}")

def display_matches_for_referee(referee_details, matches):
    """Displays a list of matches for a specific referee."""
    if not matches:
        print("No more matches found for this referee.")
        return

    print(f"\n--- Matches for Referee: {referee_details['first_name']} {referee_details['last_name']} ---")
    print(f"{'ID':<10}{'Date':<15}{'Status':<12}{'Home Team':<25}{'Away Team':<25}{'Score'}")
    print("-" * 100)
    for match in matches:
        score_str = ""
        if match.get('home_score') is not None and match.get('away_score') is not None and match['status'] == 'Completed':
            score_str = f"{int(match['home_score'])}-{int(match['away_score'])}"

        print(f"{match['id']:<10}{str(match['match_date']):<15}{match['status']:<12}{match['home_team_name']:<25}{match['away_team_name']:<25}{score_str}")

def display_all_matches(matches):
    """Displays a paginated list of all matches."""
    if not matches:
        print("No more matches found.")
        return

    print(f"\n--- All Matches ---")
    print(f"{'ID':<10}{'Date':<15}{'Status':<12}{'Home Team':<25}{'Away Team':<25}{'Score'}")
    print("-" * 100)
    for match in matches:
        score_str = ""
        # Check if score data is present and the match is completed
        if match.get('home_score') is not None and match.get('away_score') is not None and match['status'] == 'Completed':
            score_str = f"{int(match['home_score'])}-{int(match['away_score'])}"

        print(f"{match['id']:<10}{str(match['match_date']):<15}{match['status']:<12}{match['home_team_name']:<25}{match['away_team_name']:<25}{score_str}")


def get_year_input(prompt="Please input the League's Year, or 'q' to go back:"):
    """Prompts the user for a year input with a customizable prompt."""
    return input(f"{prompt} ").strip()

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

def get_referee_info_input():
    """Prompts user for new referee details."""
    print("\nEnter new referee details (leave first name blank to cancel):")
    first_name = input("First Name: ").strip()
    if not first_name:
        return None
    
    last_name = input("Last Name: ").strip()
    while not last_name:
        print("Last name cannot be empty.")
        last_name = input("Last Name: ").strip()
        
    return {"first_name": first_name, "last_name": last_name}


def get_match_date_input(year=None):
    """Prompts user for a match date in YYYY-MM-DD format."""
    from datetime import datetime
    while True:
        if year:
            prompt = f"Enter the match date for {year} (MM-DD), or 'q' to quit: "
            date_input = input(prompt).strip()
            if date_input.lower() == 'q':
                return None
            date_str = f"{year}-{date_input}"
        else:
            prompt = "Enter the match date (YYYY-MM-DD), or 'q' to quit: "
            date_str = input(prompt).strip()
            if date_str.lower() == 'q':
                return None
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            print("Invalid date format. Please use the correct format.")

def get_game_time_input():
    """Prompts user for a game time in MM:SS format."""
    from datetime import datetime
    while True:
        time_str = input("Enter the game time (MM:SS), or 'q' to quit: ").strip()
        if time_str.lower() == 'q':
            return None
        try:
            # We parse it to validate, but will store it as a string for the DB which expects a timestamp-like format
            datetime.strptime(time_str, '%M:%S')
            return f"1970-01-01 00:{time_str}" # Format for DB timestamp
        except ValueError:
            print("Invalid time format. Please use MM:SS.")

def get_team_name_input(): return input("Enter the new team's name (or leave blank to cancel): ").strip()
def id_selection_input(): return input("\nEnter the ID you want to select, press [Enter] for next page, or 'q' to quit: ").strip()
def get_new_team_name_input(): return input("Enter the new team name: ").strip()
def get_updated_player_info_input(current_details):
    """
    Prompts user for updated player details, showing current values.
    Pressing Enter keeps the current value.
    Returns a dictionary of changed values.
    """
    print("\nEnter new player details. Press [Enter] to keep the current value.")
    
    changes = {}
    
    # First Name
    new_first_name = input(f"First Name [{current_details['first_name']}]: ").strip()
    if new_first_name and new_first_name != current_details['first_name']:
        changes['first_name'] = new_first_name
        
    # Last Name
    new_last_name = input(f"Last Name [{current_details['last_name']}]: ").strip()
    if new_last_name and new_last_name != current_details['last_name']:
        changes['last_name'] = new_last_name
        
    # Shirt Number
    current_shirt = current_details.get('shirt_num', 'N/A')
    new_shirt_num_str = input(f"Shirt Number [{current_shirt}]: ").strip()
    if new_shirt_num_str and new_shirt_num_str.isdigit():
        new_shirt_num = int(new_shirt_num_str)
        if new_shirt_num != current_shirt:
            changes['shirt_num'] = new_shirt_num
            
    return changes

def get_updated_referee_info_input(current_details):
    """
    Prompts user for updated referee details, showing current values.
    Pressing Enter keeps the current value.
    Returns a dictionary of changed values.
    """
    print("\nEnter new referee details. Press [Enter] to keep the current value.")
    
    changes = {}
    
    new_first_name = input(f"First Name [{current_details['first_name']}]: ").strip()
    if new_first_name and new_first_name != current_details['first_name']:
        changes['first_name'] = new_first_name
        
    new_last_name = input(f"Last Name [{current_details['last_name']}]: ").strip()
    if new_last_name and new_last_name != current_details['last_name']:
        changes['last_name'] = new_last_name
            
    return changes

def get_delete_confirmation_input(item_type, item_id):
    """Asks for confirmation by re-typing the ID."""
    print(f"\nWARNING: This action is irreversible and will delete the {item_type} and all associated data (like game events).")
    confirmation_id = input(f"To confirm, please re-enter the {item_type} ID ({item_id}): ").strip()
    return confirmation_id

        
def print_player_list_header(team_id): print(f"\n--- Players for Team ID: {team_id} ---")
def print_select_team_for_player(): print("First, select the team for the new player.")
def print_select_from_list(example):print(f"\nPlease select a {example} from the list below.")
def print_no_more_found(example):print(f"No more {example} found.")
def print_no_group_phase_found():print("No group phase found for the selected season.")
def print_no_knockout_rounds_found():print("No rounds found for the knock out phase.")
def print_season_creation_failed(year): print(f"Failed to create season '{year}'. It may already exist.")
def print_creation_failed(item_type, name): print(f"Failed to create {item_type} '{name}'. It may already exist or there was a database error.")
def print_season_creation_success(year): print(f"Season '{year}' created successfully.")
def print_phases_creation_success(): print("Group Stage and Knockout phases created.")
def print_rounds_creation_success(): print("Knockout rounds (Quarter-Finals, Semi-Finals, etc.) created.")
def print_team_creation_success(team_name): print(f"Team '{team_name}' created successfully.")
def print_referee_creation_success(first_name, last_name): print(f"Referee '{first_name} {last_name}' created successfully.")
def print_match_creation_success(match_id): print(f"Match created successfully with ID: {match_id}")
def print_player_creation_success(first_name, last_name): print(f"Player '{first_name} {last_name}' created successfully.")
def print_update_success(item): print(f"Successfully updated {item}.")
def print_update_failed(item): print(f"Failed to update {item}. The value may be a duplicate or a database error occurred.")
def print_delete_success(item_type, item_id): print(f"Successfully deleted {item_type} with ID {item_id}.")
def print_delete_failed(item_type, item_id, note=None):
    message = f"Failed to delete {item_type} with ID {item_id}."
    if note: message += f" {note}"
    print(message)
def print_confirmation_failed(): print("Confirmation failed. The entered ID did not match. Deletion cancelled.")
def print_operation_cancelled(): print("Operation cancelled.")
def print_create_match_header(): print("\n--- Create a New Match ---")
def print_select_home_team(): print("\nFirst, select the HOME team.")
def print_select_away_team(): print("\nNext, select the AWAY team.")
def print_status_set_to(status): print(f"Match status will be set to: {status}")
def print_invalid_team_selection(): print("The away team cannot be the same as the home team. Please select a different team.")
def print_no_phases_found(): print("No phases found for this season. Please create them first.")
def print_link_success(item1, id1, item2, id2): print(f"Successfully linked {item1} {id1} to {item2} {id2}.")
def print_unlink_success(item1, id1, item2, id2): print(f"Successfully unlinked {item1} {id1} from {item2} {id2}.")
def print_event_creation_success(event_name, player_id, match_id): print(f"Successfully created event '{event_name}' for player {player_id} in match {match_id}.")
def invalid_input():print("Invalid input. Please try again.")
def print_welcome(): print("\n--->>Welcome to the BasketBall League<<---")

def print_admin_login_header(): print("\n--- Admin Login ---")

def get_admin_username_input():
    """Prompts user for admin username or q to cancel."""
    return input("Enter admin username (or q to go back): ").strip()

def get_admin_password_input():
    """Prompts user for admin password or q to cancel."""
    return input("Enter admin password (or press q to go back): ").strip()

def print_login_success(username): print(f"\nLogin successful! Welcome, {username}.")

def print_login_failed(): print("\nLogin failed! Invalid username or password. Please try again.")