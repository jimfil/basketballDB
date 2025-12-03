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

def find_playerstats(player_id):
    if not player_id:
        return # User quit selection
    # The pagination for stats is display-only, no selection, so we keep its simple loop.
    handle_pagination(lambda page: get_player_stats(player_id, page), display_player_stats)

def view_teams():
    """Controller to view all teams or a single team."""
    print_select_from_list("team")
    return handle_pagination(lambda page: get_teams(page), display_teams)

def find_matches_for_team():
    team_id = view_teams()
    if not team_id:
        return 

    team_name, _ = get_matches_by_team(team_id, 0) # Fetch team name
    page = 0
    print_select_from_list("match")

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
    handle_pagination(lambda page: get_match_stats(match_id, page), display_match_stats)

def select_player():
    team_id = view_teams()
    if not team_id:
        return None

    print_select_from_list("players")
    return handle_pagination(lambda page: get_players(team_id, page), display_players_paginated)

def cmd_create_team():
    team_name = get_team_name_input()
    if not team_name:
        print_operation_cancelled()
        return
    create_team(team_name)
    print_team_creation_success(team_name)

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
    """Calculates standings for a given phase_id using an optimized query."""
    if not phase_id:
        print("No phase selected.")
        return []

    matches = get_matches_by_phase(phase_id)
    standings = {}

    for match in matches:
        home_team_id = match['home_team_id']
        away_team_id = match['away_team_id']

        # Initialize teams in standings if not present
        if home_team_id not in standings:
            standings[home_team_id] = {'name': get_team_name(home_team_id)[0]['name'], 'wins': 0, 'losses': 0}
        if away_team_id not in standings:
            standings[away_team_id] = {'name': get_team_name(away_team_id)[0]['name'], 'wins': 0, 'losses': 0}

        scores = get_scores(match['match_id'])
        home_score = scores.get(home_team_id, 0)
        away_score = scores.get(away_team_id, 0)

        if home_score > away_score:
            standings[home_team_id]['wins'] += 1
            standings[away_team_id]['losses'] += 1
        else:
            standings[home_team_id]['losses'] += 1
            standings[away_team_id]['wins'] += 1

    return sorted(standings.values(), key=lambda x: x['wins'], reverse=True)
def team_menu():
    while True:
        choice = get_menu_choice(
            "--- Team Management ---",
            {"1": "View Teams", "2": "Create Team", "3": "Back to Main Menu"}
        )
        index = int(choice)

        if index == 1:
            view_teams()
        elif index == 2:
            cmd_create_team()
        elif index == 3:
            return  

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
            standings = calculate_standings(group_phase['id'])
            display_standings(standings)

        elif index == "2":
            phases = get_phases_by_season(year_id)
            knockout_phase = next((p for p in phases if p['phase_id'] == 2), None)
            if knockout_phase is None:
                print_no_knockout_rounds_found()
                continue
            standings = calculate_standings(knockout_phase['id'])
            display_standings(standings)
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
            find_playerstats(select_player())
        elif index == 2:                # dialegw omada -> blepw agwnes (Omada 1 - Omada 2) (73 - 68 )
            find_matches_for_team()                  
        elif index == 3:
            shot_percentage_control()
        elif index == 4:
            return  # Go back

def main_menu(index):
    if index==1: team_menu()
    elif index==2: league_menu()
    elif index==3: stats_menu()
    elif index==4: return True
    return False





if __name__ == "__main__":

    print("\n--->>Welcome to the BasketBall League<<---")
    exit = False
    while not exit:
        choice = get_menu_choice(
            "Press one of the following options:",
            {"1": "Team Menu", "2": "View League", "3": "Stats", "4": "Exit"}
        )
        exit = main_menu(int(choice))
