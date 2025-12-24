from model import *
from view_cmd import *
import time

def admin_login_menu():
    """
    Controller for admin login menu.
    Returns True if login is successful, False otherwise.
    Supports q to cancel.
    """
    
    while True:
        username = get_admin_username_input()
        
        if username == 'q':
            print_operation_cancelled()
            return False
        
        password = get_admin_password_input()
        
        if password == 'q':
            print_operation_cancelled()
            return False
        
        if verify_admin_credentials(username, password):
            print_login_success(username)
            return True
        else:
            print_login_failed()
            return False

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


        if results and isinstance(results[0], (dict, tuple, list)) and len(results[0]) > 0:
            if 'id' in results[0]:
                all_ids.update(r['id'] for r in results)

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
        return
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

    team_name, _ = get_matches_by_team(team_id, 0)
    page = 0
    print_select_from_list("match")

    match_fetcher = lambda page: get_matches_by_team(team_id, page)[1]
    display_func = lambda matches: display_matches_for_team(team_name, matches)

    selected_match_id = handle_pagination(match_fetcher, display_func)
    if selected_match_id:
        find_matchstats(selected_match_id)

def find_matchstats(match_id):
    if not match_id:
        return
    
    handle_pagination_view_only(lambda page: get_match_stats(match_id, offset=page), display_match_stats)
    start = time.time()
    get_match_stats(match_id)
    end = time.time()

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

    if not create_season(year):
        print_season_creation_failed(year)
        return
    print_season_creation_success(year)

    group_stage_phase_id = create_phase(year, 1)
    knockout_phase_id = create_phase(year, 2)
    print_phases_creation_success()

    rounds_created = False
    if group_stage_phase_id:
        for round_num in range(1, 6):
            create_round(round_num, group_stage_phase_id)
        rounds_created = True

    if knockout_phase_id:
        for round_num in range(1, 5):
            create_round(round_num, knockout_phase_id)
        rounds_created = True

    if rounds_created:
        print_rounds_creation_success()

def cmd_create_events_in_match():
    """Controller to create one or more events for a selected match."""
    match_id = select_match()
    if not match_id:
        return print_operation_cancelled()
    
    match_details_list = get_match(match_id)
    match_details_list = get_match(match_id)
    if not match_details_list:
        return
    match_details = match_details_list[0]
    home_team_id = match_details['home_team_id']
    away_team_id = match_details['away_team_id']
    home_team_name = get_team_name(home_team_id)[0]['name']
    away_team_name = get_team_name(away_team_id)[0]['name']

    while True:
        
        
        
        team_choice = get_menu_choice(
            "Select the team for the event:",
            {"1": f"Home: {home_team_name}", "2": f"Away: {away_team_name}"}
        )
        if team_choice == 'q':
            break
        
        selected_team_id = home_team_id if team_choice == '1' else away_team_id

        
        print_select_from_list("player involved in the event")
        player_id = handle_pagination(lambda page: get_players(selected_team_id, offset=page), display_players_paginated)
        if not player_id:
            break

        
        print_select_from_list("event type")
        all_events = get_all_events()
        event_id = handle_pagination(lambda page: all_events, display_event_types)
        if not event_id:
            break

        
        game_time = get_game_time_input()
        if not game_time:
            break

        
        if create_match_event(match_id, player_id, event_id, game_time):
            event_name = next((e['name'] for e in all_events if e['id'] == event_id), "Unknown")
            print_event_creation_success(event_name, player_id, match_id)
        else:
            print_creation_failed("event", "for this match")

        another = input("Create another event for this match? (y/n): ").strip().lower()
        if another != 'y':
            break

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

def select_stadium():
    print_select_from_list("stadium")
    return handle_pagination(lambda page: get_stadiums(offset=page), display_stadiums_paginated)

def cmd_create_stadium():
    info = get_stadium_info_input()
    if not info:
        print_operation_cancelled()
        return
    if create_stadium(info['name'], info['location'], info['capacity']):
        print_stadium_creation_success(info['name'])
    else:
        print_creation_failed("stadium", info['name'])


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
        return

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
    choice = get_menu_choice("Select what to update:", {"1": "Team Name", "2": "Home Stadium"})

    if choice == "1":
        new_name = get_new_team_name_input()
        if not new_name or new_name == 'q':
            print_operation_cancelled()
            return
        if update_entry('Team', team_id, {'name': new_name}):
            print_update_success(f"Team {team_id}'s name")
        else:
            print_update_failed(f"team {team_id}'s name")
    elif choice == "2":
        
        year = get_year()
        if not year:
            print_operation_cancelled()
            return

        phases = get_phases_by_season(year)
        if not phases:
            print_no_phases_found()
            return

        logical_phase_id = get_phase_selection(phases)
        if logical_phase_id is None:
            print_operation_cancelled()
            return

        
        phase_db_id = next((p['id'] for p in phases if p['phase_id'] == logical_phase_id), None)
        if phase_db_id is None:
            print_operation_cancelled()
            return

        rounds = get_rounds_by_phase(phase_db_id)
        round_db_id = get_round_selection(rounds)
        if not round_db_id:
            print_operation_cancelled()
            return

        
        stadium_id = select_stadium()
        if not stadium_id:
            print_operation_cancelled()
            return

        if update_team_home_stadium(team_id, stadium_id, round_db_id):
            print_update_success("Team Stadium")
        else:
            print_update_failed("Team Stadium")

def cmd_update_referee_info():
    """Controller to update a referee's information."""
    referee_id = select_referee()
    if not referee_id:
        return print_operation_cancelled()

    current_details = get_referee_details(referee_id)
    if not current_details:
        print_update_failed(f"referee with ID {referee_id} (not found)")
        return

    changes = get_updated_referee_info_input(current_details)

    if not changes:
        return

    if update_entry('Referee', referee_id, changes):
        print_update_success(f"Referee {referee_id}'s information")
    else:
        print_update_failed(f"Referee {referee_id}'s information")

def cmd_delete_player():
    """Controller to delete a player and their related records."""
    player_id = select_player() 
    if not player_id:
        print_operation_cancelled()
        return
    
    
    confirmation_id_str = get_delete_confirmation_input("Player", player_id)
    if not confirmation_id_str.isdigit() or int(confirmation_id_str) != player_id:
        print_confirmation_failed()
        return

    
    if delete_player(player_id): 
        print_delete_success("Player", player_id)
    else:
        print_delete_failed("Player", player_id, "An unexpected database error occurred.")

def cmd_delete_team():
    """Controller to delete a team."""
    team_id = select_team_for_action()
    if not team_id:
        print_operation_cancelled()
        return
    
    confirmation_id_str = get_delete_confirmation_input("Team", team_id)
    if not confirmation_id_str.isdigit() or int(confirmation_id_str) != team_id:
        print_confirmation_failed()
        return

    if delete_team(team_id):
        print_delete_success("Team", team_id)
    else:
        print_delete_failed("Team", team_id, "Note: Teams with existing matches cannot be deleted.")

def cmd_create_match():
    """Controller to guide the user through creating a new match step-by-step."""
    from datetime import datetime
    print_create_match_header()

    
    year = get_year()
    if not year:
        return print_operation_cancelled()

    
    phases = get_phases_by_season(year)
    if not phases:
        return print_no_phases_found()

    logical_phase_id = get_phase_selection(phases)
    if logical_phase_id is None:
        return print_operation_cancelled()
    
    
    phase_db_id = next((p['id'] for p in phases if p['phase_id'] == logical_phase_id), None)
    if phase_db_id is None:
        return print_operation_cancelled()

    
    rounds = get_rounds_by_phase(phase_db_id)
    round_id = get_round_selection(rounds)
    if not round_id:
        return print_operation_cancelled()

    
    match_date_str = get_match_date_input(year)
    if not match_date_str:
        return print_operation_cancelled()
        
    match_date_obj = datetime.strptime(match_date_str, '%Y-%m-%d').date()
    status = 'Scheduled' if match_date_obj > datetime.now().date() else 'Completed'
    print_status_set_to(status)

    
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
            break  
        print_invalid_team_selection()

    
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

def cmd_view_referees_for_match():
    """Controller to view all referees linked to a specific match."""
    match_id = select_match()
    if not match_id:
        return print_operation_cancelled()

    referees = get_referees_in_match(match_id)
    if not referees:
        return

    display_referees_paginated(referees)
    input("Press [Enter] to continue...")

def cmd_view_matches_for_referee():
    """Controller to view all matches for a specific referee."""
    referee_id = select_referee()
    if not referee_id:
        return print_operation_cancelled()

    referee_details = get_referee_details(referee_id)
    handle_pagination_view_only(lambda page: get_matches_for_referee(referee_id, offset=page), lambda matches: display_matches_for_referee(referee_details, matches))

def select_referee():
    """Controller to select a referee and return their ID."""
    print_select_from_list("referee")
    return handle_pagination(lambda page: get_referees(offset=page), display_referees_paginated)

def select_match():
    """Controller to select a match and return its ID."""
    print_select_from_list("match")
    return handle_pagination(lambda page: get_all_matches_with_names(offset=page), display_all_matches)

def cmd_link_referee_to_match():
    """Controller to link a referee to a match."""
    match_id = select_match()
    if not match_id:
        return print_operation_cancelled()

    print_select_from_list("unassigned referee")
    referee_id = handle_pagination(lambda page: get_unassigned_referees(match_id, offset=page), display_referees_paginated)

    if not referee_id:
        return print_operation_cancelled()

    if link_referee_to_match(match_id, referee_id):
        print_link_success("Referee", referee_id, "Match", match_id)
    else:
        print_creation_failed("link", f"between Referee {referee_id} and Match {match_id} (it may already exist)")

def cmd_unlink_referee_from_match():
    """Controller to unlink a referee from a match."""
    match_id = select_match()
    if not match_id:
        return print_operation_cancelled()

    referees = get_referees_in_match(match_id)
    if not referees:
        return

    display_referees_paginated(referees)
    
    valid_ids = {str(r['id']) for r in referees}
    while True:
        referee_id_str = input("Enter Referee ID to unlink, or 'q' to quit: ").strip()
        if referee_id_str.lower() == 'q':
            return print_operation_cancelled()
        if referee_id_str in valid_ids:
            referee_id = int(referee_id_str)
            break
        invalid_input()

    if unlink_referee_from_match(match_id, referee_id):
        print_unlink_success("Referee", referee_id, "Match", match_id)
    else:
        print_delete_failed("link for Referee", referee_id, "from Match", match_id)

def cmd_create_referee():
    """Controller to create a new referee."""
    ref_info = get_referee_info_input()
    if not ref_info:
        return print_operation_cancelled()

    if create_referee(ref_info['first_name'], ref_info['last_name']):
        print_referee_creation_success(ref_info['first_name'], ref_info['last_name'])
    else:
        print_creation_failed("referee", f"{ref_info['first_name']} {ref_info['last_name']}")

def cmd_delete_referee():
    """Controller to delete a referee."""
    referee_id = select_referee()
    if not referee_id:
        return print_operation_cancelled()

    
    confirmation_id_str = get_delete_confirmation_input("Referee", referee_id)
    if not confirmation_id_str.isdigit() or int(confirmation_id_str) != referee_id:
        print_confirmation_failed()
        return

    if delete_referee(referee_id):
        print_delete_success("Referee", referee_id)
    else:
        print_delete_failed("Referee", referee_id, "An unexpected database error occurred.")


def cmd_delete_stadium():
    """Controller to delete a stadium — only allowed if not linked to any team."""
    stadium_id = select_stadium()
    if not stadium_id:
        return print_operation_cancelled()

    
    confirmation_id_str = get_delete_confirmation_input("Stadium", stadium_id)
    if not confirmation_id_str.isdigit() or int(confirmation_id_str) != stadium_id:
        print_confirmation_failed()
        return

    if delete_stadium(stadium_id):
        print_stadium_deletion_success(stadium_id)
    else:
        print_delete_failed("Stadium", stadium_id, "It is still linked to a team or used by matches. Unlink it first.")


def cmd_delete_match():
    """Controller to delete a match with double confirmation."""
    match_id = select_match()
    if not match_id:
        return print_operation_cancelled()

    confirmation_id_str = get_delete_confirmation_input("Match", match_id)
    if not confirmation_id_str.isdigit() or int(confirmation_id_str) != match_id:
        print_confirmation_failed()
        return

    
    if delete_match(match_id):
        print_delete_success("Match", match_id)
    else:
        print_delete_failed("Match", match_id, "An unexpected database error occurred.")


def cmd_change_match_stadium():
    """Controller to change the stadium assigned to a match."""
    match_id = select_match()
    if not match_id:
        return print_operation_cancelled()

    stadium_id = select_stadium()
    if not stadium_id:
        return print_operation_cancelled()

    if update_match_stadium(match_id, stadium_id):
        print_update_success(f"Match {match_id} stadium")
    else:
        print_update_failed(f"Match {match_id} stadium")

def cmd_delete_event_from_match():
    """Controller to delete a specific event from a match."""
    match_id = select_match()
    if not match_id:
        return print_operation_cancelled()

    print_select_from_list("event to delete")
    event_id_to_delete = handle_pagination(lambda page: get_match_stats(match_id, offset=page), display_match_stats)

    if not event_id_to_delete:
        return print_operation_cancelled()

    
    confirmation_id_str = get_delete_confirmation_input("Event", event_id_to_delete)
    if not confirmation_id_str.isdigit() or int(confirmation_id_str) != event_id_to_delete:
        print_confirmation_failed()
        return

    if delete_match_event(event_id_to_delete):
        print_delete_success("Event", event_id_to_delete)
    else:
        print_delete_failed("Event", event_id_to_delete, "An unexpected database error occurred.")

def select_team_for_action():
    """
    A dedicated controller for selecting a team and returning its ID for further actions.
    """
    print_select_from_list("team")
    return handle_pagination(lambda page: get_teams(page), display_teams)


def cmd_view_team_stadiums():
    """Controller to view a team's stadium history (paginated)."""
    team_id = select_team_for_action()
    if not team_id:
        return print_operation_cancelled()

    print_select_from_list("team stadium history")
    handle_pagination_view_only(lambda page: get_team_stadiums(team_id, offset=page), display_team_stadiums)

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
        return

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
    if phase_id == 1: 
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
                "4": "Create a new stadium"
            }
        )
        if choice == "1":
            cmd_create_team()
        elif choice == "2":
            cmd_create_player_for_team()
        elif choice == "3":
            cmd_create_season_with_phases()
        elif choice == "4":
            cmd_create_stadium()
        elif choice == 'q':
            return

def change_info_menu():
    """Handles the sub-menu for changing information."""
    while True:
        choice = get_menu_choice(
            "--- Change Information Menu ---",
            {
                "1": "Change Team Information",
                "2": "Change Player Information"
            }
        )
        if choice == "1":
            cmd_update_team_info()
        elif choice == "2":
            cmd_update_player_info()
        elif choice == 'q':
            return

def delete_menu():
    """Handles the sub-menu for deleting entities."""
    while True:
        choice = get_menu_choice(
            "--- Delete Menu ---",
            {
                "1": "Delete a Team",
                "2": "Delete a Player",
                "3": "Delete a Stadium",
                "4": "Delete a Match"
            }
        )
        if choice == "1":
            cmd_delete_team()
        elif choice == "2":
            cmd_delete_player()
        elif choice == "3":
            cmd_delete_stadium()
        elif choice == "4":
            cmd_delete_match()
        elif choice == 'q':
            return

def matches_events_menu():
    """Handles the sub-menu for creating/updating matches and events."""
    while True:
        choice = get_menu_choice(
            "--- Match/Referees Menu ---",
            {
                "1": "Create a new match",
                "2": "Manage Referees",
                "3": "Create events in a match",
                "4": "Delete an event from a match",
                "5": "Change match stadium"
            }
        )
        if choice == "1":
            cmd_create_match()
        elif choice == "2":
            referee_menu()
        elif choice == "3":
            cmd_create_events_in_match()
        elif choice == "4":
            cmd_delete_event_from_match()
        elif choice == "5":
            cmd_change_match_stadium()
        elif choice == 'q':
            return

def referee_menu():
    """Handles the sub-menu for managing referees."""
    while True:
        choice = get_menu_choice(
            "--- Referee Management ---",
            {
                "1": "Link a referee to a match",
                "2": "Unlink a referee from a match",
                "3": "Create a new referee",
                "4": "Delete a referee",
                "5": "Update Referee Information"
            }
        )
        if choice == 'q': return
        if choice == "1":
            cmd_link_referee_to_match()
        elif choice == "2":
            cmd_unlink_referee_from_match()
        elif choice == "3":
            cmd_create_referee()
        elif choice == "4":
            cmd_delete_referee()
        elif choice == "5":
            cmd_update_referee_info()

def management_menu():
    """Handles the main management menu and its sub-menus."""
    while True:
        choice = get_menu_choice(
            "--- Management Menu ---",
            {
                "1": "Create Team/Players/Season",
                "2": "Change Information Menu",
                "3": "Match/Referees Menu",
                "4": "Delete Menu",
                "5": "Add admin user",
                "6": "Remove admin user"
            }
        )
        if choice == 'q': return
        if choice == "1":
            create_menu()
        elif choice == "2":
            change_info_menu()
        elif choice == "3":
            matches_events_menu()
        elif choice == "4":
            delete_menu()
        elif choice == "5":
            cmd_add_admin_user()
        elif choice == "6":
            cmd_remove_admin_user()

def cmd_add_admin_user():
    username, password = get_new_admin_credentials()
    if not username or not password:
        print_operation_cancelled()
        return

    if add_admin_user(username, password):
        print_admin_creation_success(username)
    else:
        print_creation_failed("admin user", username)

def cmd_remove_admin_user():
    username = get_admin_username_input()
    if username == 'q':
        print_operation_cancelled()
        return
    password = get_admin_password_input()
    if password == 'q':
        print_operation_cancelled()
        return
    if not password or not username:
        print_operation_cancelled()
        return

    if verify_admin_credentials(username,password):
        if remove_admin_user(username):
            print_admin_removal_success(username)
        else:
            print_removal_failed("admin user", username)
    else:
            print_removal_failed("admin user", username)

def get_year():
    giwrgos = get_seasons()
    lista = [item["year"] for item in giwrgos]
    display_years(lista)
    while True: 
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
            {"1": "View League by Season", "2": "View Teams", "3": "View All Matches", "4": "View Team Stadium History",
             "5": "View referees for a match",
            "6": "View matches for a referee",}
        )
        if choice == 'q': return 
        if choice == "1":
            league_menu()
        elif choice == "2":
            view_teams() 
        elif choice == "3":
            cmd_view_all_matches()
        elif choice == "4":
            cmd_view_team_stadiums()
        elif choice == "5":
            cmd_view_referees_for_match()
        elif choice == "6":
            cmd_view_matches_for_referee()
    
def league_menu():
    year_id = get_year()
    while True:
        index = get_menu_choice(
            "--- League Menu ---",
            {"1": "View Standings (Group Stage)", "2": "View Rounds in the Knockout Stage", "3": "Change Season"}
        )
        if index == 'q': return
        if index == "1":
            phases = get_phases_by_season(year_id)
            group_phase = next((p for p in phases if p['phase_id'] == 1), None)
            if group_phase is None:
                print_no_group_phase_found()
                continue
            start = time.time()
            standings = calculate_group_stage_standings(group_phase['id'])
            end = time.time()
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

def stats_menu():
    while True:
        choice = get_menu_choice(
            "What stats would you like to view?",
            {"1": "Player Stats", "2": "Match Stats", "3": "Shot Analysis", "4": "Season MVP"}
        )
        if choice == 'q': return 
        index = int(choice)
        if index == 1:
            find_playerstats(select_player())
        elif index == 2:
            find_matches_for_team()
        elif index == 3:
            shot_percentage_control()
        elif index == 4:
            year = get_year()
            if not year:
                print_operation_cancelled()
                continue
            mvp_data = get_year_mvp(year)
            if mvp_data:
                display_season_mvp(year, mvp_data)
            


def main_menu(index):
    if index==1:
        if admin_login_menu():
            management_menu()
    elif index==2: view_menu()
    elif index==3: stats_menu()
    elif index==4: check_time()
    elif index==0: return True 
    return False

def check_time():
    """
    This function is useless in TiDB cloud databases because the connection interferes with the time measurement
    """
    drop_all_defined_indexes()
    start_no_idx = time.time()
    run_benchmark_query()
    end_no_idx = time.time()
    time_no_idx = end_no_idx - start_no_idx

    apply_indexes()
    start_idx = time.time()
    run_benchmark_query()
    end_idx = time.time()
    time_idx = end_idx - start_idx

    if time_idx > 0:
        speedup = time_no_idx / time_idx


if __name__ == "__main__":
    print_welcome()
    exit = False
    while not exit:
        choice = get_menu_choice(
            "Press one of the following options:",
            {"1": "Management Menu", "2": "View League and Teams", "3": "Stats","4": "Check times"},
            quit_text="Exit application"
        )
        if choice == 'q':
            exit = main_menu(0)
        else:
            exit = main_menu(int(choice))
