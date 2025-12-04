from model import *
from view_cmd import *

def handle_pagination(data_fetcher, display_function, *args):
    """
    Generic handler for paginating through data.
    - data_fetcher: A function that accepts a page number and other args, and returns data.
    - display_function: A function that displays the data.
    - *args: Arguments to pass to the data_fetcher function.
    """
    page = 0
    all_ids = set()
    while True:
        results = data_fetcher(page, *args)
        if not results:
            print_no_more_found("items")
            return None

        # Collect IDs if the result items are selectable
        if results and isinstance(results[0], (dict, tuple, list)) and len(results[0]) > 0:
            # Handle dicts with 'id' or tuples/lists where id is the first/second element
            if isinstance(results[0], dict) and 'id' in results[0]:
                all_ids.update(r['id'] for r in results)
            elif isinstance(results[0], (tuple, list)) and isinstance(results[0][0], int): # Assuming ID is first
                all_ids.update(r[0] for r in results)
            elif isinstance(results[0], (tuple, list)) and len(results[0]) > 1 and isinstance(results[0][1], int): # Assuming ID is second
                all_ids.update(r[1] for r in results)

        display_function(results)
        user_input = id_selection_input()

        if user_input.lower() == 'q':
            return None
        if user_input == '':
            page += 1
            continue
        if user_input.isdigit() and int(user_input) in all_ids:
            return int(user_input)
        invalid_input()

def handle_pagination_view_only(data_fetcher, display_function, *args):
    """
    A simplified pagination handler for display-only purposes.
    Allows paging through data without a selection prompt.
    """
    page = 0
    while True:
        results = data_fetcher(page, *args)
        if not results:
            print_no_more_found("items")
            input("Press [Enter] to continue...")
            return

        display_function(results)
        user_input = input("Press [Enter] for next page, or 'q' to quit: ").strip()

        if user_input.lower() == 'q':
            return
        if user_input == '':
            page += 1
        else:
            invalid_input()

def find_playerstats(player_id):
    if not player_id:
        return # User quit selection
    handle_pagination_view_only(lambda page: get_player_stats(player_id, offset=page), display_player_stats)

def view_teams():
    """Controller to view all teams or a single team."""
    team_id = select_team_for_action()
    if team_id:
        print_player_list_header(team_id)
        handle_pagination_view_only(lambda page: get_players(team_id, offset=page), display_players_paginated)

def cmd_view_all_matches():
    """Controller to view all matches, paginated."""
    handle_pagination_view_only(lambda page: get_all_matches_with_names(offset=page), display_all_matches)

def find_matches_for_team():
    team_id = select_team_for_action()
    if not team_id:
        return 

    team_name, _ = get_matches_by_team(team_id, 0) # Fetch team name
    page = 0
    print_select_from_list("match") # This is a view function, so it's OK.

    # Custom fetcher for matches as it returns a tuple (team_name, matches)
    # The generic paginator expects a list of items.
    match_fetcher = lambda page: get_matches_by_team(team_id, page)[1]
    display_func = lambda matches: display_matches_for_team(team_name, matches)

    selected_match_id = handle_pagination(match_fetcher, display_func)
    if selected_match_id:
        find_matchstats(selected_match_id)

def find_matchstats(match_id):
    if not match_id:
        return
    handle_pagination_view_only(lambda page: get_match_stats(match_id, offset=page), display_match_stats)

def select_player():
    team_id = select_team_for_action()
    if not team_id:
        return None

    print_select_from_list("players")
    return handle_pagination(lambda page: get_players(team_id, offset=page), display_players_paginated)

def cmd_create_team():
    team_name = get_team_name_input()
    if not team_name:
        print_operation_cancelled()
        return
    if create_team(team_name):
        print_team_creation_success(team_name)
    else:
        print_creation_failed("team", team_name)

def cmd_create_season_with_phases():
    """Controller to create a season, its phases, and knockout rounds."""
    year = get_year_input(prompt="Enter the year for the new season, or 'q' to cancel:")
    if not year or not year.isdigit():
        print_operation_cancelled()
        return

    # 1. Create Season
    if not create_season(year):
        print_season_creation_failed(year)
        return
    print_season_creation_success(year)

    # 2. Create Phases (Group Stage and Knockout)
    group_stage_phase_id = create_phase(year, 1)  # phase_id 1 for Group Stage
    knockout_phase_id = create_phase(year, 2)  # phase_id 2 for Knockout
    print_phases_creation_success()

    # 3. Create Rounds for both phases
    rounds_created = False
    if group_stage_phase_id:
        # Group stage has 5 rounds (for a 6-team group round-robin)
        for round_num in range(1, 6):
            create_round(round_num, group_stage_phase_id)
        rounds_created = True

    if knockout_phase_id:
        # Knockout has 4 rounds (R16, QF, SF, Finals)
        for round_num in range(1, 5):
            create_round(round_num, knockout_phase_id)
        rounds_created = True

    if rounds_created:
        print_rounds_creation_success()

def cmd_create_player_for_team():
    """Controller function to create a player and assign them to a team."""
    team_id = select_team_for_action()
    if not team_id:
        print_operation_cancelled()
        return

    player_info = get_player_info_input()
    if not player_info:
        print_operation_cancelled()
        return

    player_info.update({"team_id": team_id, "speciality": "Player"})
    if create_player(player_info):
        print_player_creation_success(player_info['first_name'], player_info['last_name'])
    else:
        print_creation_failed("player", f"{player_info['first_name']} {player_info['last_name']}")

def cmd_update_player_info():
    """Controller to update a player's information."""
    player_id = select_player()
    if not player_id:
        print_operation_cancelled()
        return

    current_details = get_player_details(player_id)
    if not current_details:
        print_update_failed(f"player with ID {player_id} (not found)")
        return

    changes = get_updated_player_info_input(current_details)

    if not changes:
        print("No changes were made.")
        return

    # Separate changes for Person table and Person_Team table
    person_changes = {k: v for k, v in changes.items() if k in ['first_name', 'last_name']}
    shirt_num_change = changes.get('shirt_num')

    person_updated = True
    shirt_updated = True

    if person_changes:
        person_updated = update_entry('Person', player_id, person_changes)

    if shirt_num_change is not None:
        shirt_updated = update_player_shirt_number(player_id, shirt_num_change)

    if person_updated and shirt_updated:
        print_update_success(f"Player {player_id}'s information")
    else:
        print_update_failed(f"Player {player_id}'s information")

def cmd_update_team_info():
    """Controller to update a team's name."""
    team_id = select_team_for_action()
    if not team_id:
        print_operation_cancelled()
        return

    new_name = get_new_team_name_input()
    if update_entry('Team', team_id, {'name': new_name}):
        print_update_success(f"Team {team_id}'s name")
    else:
        print_update_failed(f"team {team_id}'s name")

def cmd_delete_player():
    """Controller to delete a player and their related records."""
    player_id = select_player() # select_player already uses the correct selection logic
    if not player_id:
        print_operation_cancelled()
        return
    
    # Add confirmation step
    confirmation_id_str = get_delete_confirmation_input("Player", player_id)
    if not confirmation_id_str.isdigit() or int(confirmation_id_str) != player_id:
        print_confirmation_failed()
        return

    # Proceed with deletion if confirmation is successful
    if delete_player(player_id): # This now deletes the player and their events via CASCADE
        print_delete_success("Player", player_id)
    else:
        print_delete_failed("Player", player_id, "An unexpected database error occurred.")

def cmd_delete_team():
    """Controller to delete a team."""
    team_id = select_team_for_action()
    if not team_id:
        print_operation_cancelled()
        return
    
    if delete_team(team_id):
        print_delete_success("Team", team_id)
    else:
        print_delete_failed("Team", team_id, "Note: Teams with existing matches cannot be deleted.")

def cmd_create_match():
    """Controller to guide the user through creating a new match step-by-step."""
    from datetime import datetime
    print_create_match_header()

    # 1. Choose a Season
    year = get_year()
    if not year:
        return print_operation_cancelled()

    # 2. Choose a Phase
    phases = get_phases_by_season(year)
    if not phases:
        return print_no_phases_found()

    logical_phase_id = get_phase_selection(phases)
    if logical_phase_id is None:
        return print_operation_cancelled()
    
    # Find the database ID for the selected logical phase
    phase_db_id = next((p['id'] for p in phases if p['phase_id'] == logical_phase_id), None)
    if phase_db_id is None: # Should not happen if logic is correct
        return print_operation_cancelled()

    # 3. Choose a Round
    rounds = get_rounds_by_phase(phase_db_id)
    round_id = get_round_selection(rounds)
    if not round_id:
        return print_operation_cancelled()

    # 4. Get Date and determine Status
    match_date_str = get_match_date_input()
    if not match_date_str:
        return print_operation_cancelled()
        
    match_date_obj = datetime.strptime(match_date_str, '%Y-%m-%d').date()
    status = 'Scheduled' if match_date_obj > datetime.now().date() else 'Completed'
    print_status_set_to(status)

    # 5. Choose Teams
    print_select_home_team()
    home_team_id = select_team_for_action()
    if not home_team_id:
        return print_operation_cancelled()

    print_select_away_team()
    while True:
        away_team_id = select_team_for_action()
        if not away_team_id:
            print_operation_cancelled()
            return
        if away_team_id != home_team_id:
            break  # Valid selection
        print_invalid_team_selection()

    # 6. Create the match
    match_data = {
        'home_team_id': home_team_id,
        'away_team_id': away_team_id,
        'round_id': round_id,
        'match_date': match_date_str,
        'status': status
    }
    new_match_id = create_match(match_data)
    if new_match_id:
        print_match_creation_success(new_match_id)
    else:
        print_creation_failed("match", f"between {home_team_id} and {away_team_id}")

def select_team_for_action():
    """
    A dedicated controller for selecting a team and returning its ID for further actions.
    """
    print_select_from_list("team")
    return handle_pagination(lambda page: get_teams(page), display_teams)

def find_player_shot_percentage(player_id, shot_type, match_id=None):
    stats = get_player_shot_stats(player_id, shot_type, match_id)
    made = stats.get(f'{shot_type} Made', 0)
    missed = stats.get(f'{shot_type} Attempt', 0)
    total_attempts = made + missed

    if total_attempts == 0: percentage = 0
    else: percentage = (made / total_attempts) * 100

    scope = f"in match {match_id}" if match_id else "for their career"
    analysis_data = {
        'title': f'{shot_type} Analysis',
        'player_id': player_id,
        'scope': scope,
        'made': made,
        'missed': missed,
        'total': total_attempts,
        'percentage': percentage
    }
    display_shot_analysis(analysis_data)

def obtain_match_scores(match_id):
    scores = get_scores(match_id)
    if scores:
        display_match_score(match_id, scores)
    else:
        print(f"Match with ID {match_id} not found.")

def shot_percentage_control():
    player_id = select_player()
    if not player_id:
        return 

    choice = display_shot_percentage_menu()
    shot_map = {
        "1": "Free Throw",
        "2": "2-Point Field Goal",
        "3": "3-Point Field Goal"
    }
    if choice in shot_map:
        find_player_shot_percentage(player_id, shot_map[choice])

def calculate_standings(phase_id):
    if phase_id == 1: # Assuming phase_id 1 is always group stage
        return calculate_group_stage_standings(phase_id)
    else:
        return calculate_standings_for_phase(phase_id)

def create_menu():
    """Handles the sub-menu for creating entities."""
    while True:
        choice = get_menu_choice(
            "--- Create Menu ---",
            {
                "1": "Create a new team",
                "2": "Create a player for a team",
                "3": "Create a new season",
                "4": "Back"
            }
        )
        if choice == "1":
            cmd_create_team()
        elif choice == "2":
            cmd_create_player_for_team()
        elif choice == "3":
            cmd_create_season_with_phases()
        elif choice == "4":
            return

def change_info_menu():
    """Handles the sub-menu for changing information."""
    while True:
        choice = get_menu_choice(
            "--- Change Information Menu ---",
            {
                "1": "Change Team Information",
                "2": "Change Player Information",
                "3": "Back"
            }
        )
        if choice == "1":
            cmd_update_team_info()
        elif choice == "2":
            cmd_update_player_info()
        elif choice == "3":
            return

def delete_menu():
    """Handles the sub-menu for deleting entities."""
    while True:
        choice = get_menu_choice(
            "--- Delete Menu ---",
            {
                "1": "Delete a Team",
                "2": "Delete a Player",
                "3": "Back"
            }
        )
        if choice == "1":
            cmd_delete_team()
        elif choice == "2":
            cmd_delete_player()
        elif choice == "3":
            return

def matches_events_menu():
    """Handles the sub-menu for creating/updating matches and events."""
    while True:
        choice = get_menu_choice(
            "--- Create/Update Matches/Events Menu ---",
            {
                "1": "Create a new match",
                "2": "Back"
            }
        )
        if choice == "1":
            cmd_create_match()
        elif choice == "2":
            return

def management_menu():
    """Handles the main management menu and its sub-menus."""
    while True:
        choice = get_menu_choice(
            "--- Management Menu ---",
            {
                "1": "Create Team/Players/Season",
                "2": "Change Information Menu",
                "3": "Create/Update Matches/Events",
                "4": "Delete Menu",
                "5": "Force Delete Menu",
                "6": "Back to Main Menu"
            }
        )
        if choice == "1":
            create_menu()
        elif choice == "2":
            change_info_menu()
        elif choice == "3":
            matches_events_menu()
        elif choice == "4":
            delete_menu()
        elif choice == "5":
            print("This feature is not yet implemented.")
        elif choice == "6":
            return

def get_year():
    giwrgos = get_seasons()
    lista = [item["year"] for item in giwrgos]
    display_years(lista)
    while True: # pragma: no cover
        year_id = get_year_input() 
        if year_id.lower() == 'q': return None
        if int(year_id) in lista: break
        invalid_input()
    return year_id

def view_menu():
    """Handles the sub-menu for viewing league and teams."""
    while True:
        choice = get_menu_choice(
            "--- View Menu ---",
            {"1": "View League by Season", "2": "View Teams", "3": "View All Matches", "4": "Back to Main Menu"}
        )
        if choice == "1":
            league_menu()
        elif choice == "2":
            view_teams() # This now shows teams and then players for the selected team.
        elif choice == "3":
            cmd_view_all_matches()
        elif choice == "4":
            return
    
def league_menu():
    year_id = get_year()
    while True:
        index = get_menu_choice(
            "--- League Menu ---",
            {"1": "View Standings (Group Stage)", "2": "View Rounds in the Knockout Stage", "3": "Change Season", "4": "Back"}
        )

        if index == "1":
            phases = get_phases_by_season(year_id)
            group_phase = next((p for p in phases if p['phase_id'] == 1), None)
            if group_phase is None:
                print_no_group_phase_found()
                continue
            standings = calculate_group_stage_standings(group_phase['id'])
            display_standings(standings, is_group_stage=True)

        elif index == "2":
            phases = get_phases_by_season(year_id)
            knockout_phase = next((p for p in phases if p['phase_id'] == 2), None)
            if knockout_phase is None:
                print_no_knockout_rounds_found()
                continue
            standings = calculate_standings(knockout_phase['id'])
            display_standings(standings, is_group_stage=False)
        elif index == "3": 
            year_id = get_year()
            continue
        elif index == "4": return
        else:
            invalid_input()

        

def stats_menu():
    while True:
        choice = get_menu_choice(
            "What stats would you like to view?",
            {"1": "Player Stats", "2": "Match Stats", "3": "Shot Analysis", "4": "Back"}
        )
        index = int(choice)
        if index == 1:
            find_playerstats(select_player()) # select_player uses select_team_for_action
        elif index == 2:                # dialegw omada -> blepw agwnes (Omada 1 - Omada 2) (73 - 68 )
            find_matches_for_team() # find_matches_for_team uses select_team_for_action
        elif index == 3:
            shot_percentage_control()
        elif index == 4:
            return  # Go back

def main_menu(index):
    if index==1: management_menu()
    elif index==2: view_menu()
    elif index==3: stats_menu()
    elif index==4: return True
    return False





if __name__ == "__main__":

    print("\n--->>Welcome to the BasketBall League<<---")
    exit = False
    while not exit:
        choice = get_menu_choice(
            "Press one of the following options:",
            {"1": "Management Menu", "2": "View League and Teams", "3": "Stats", "4": "Exit"}
        )
        exit = main_menu(int(choice))
