from model import *
from view_cmd import *



def find_playerstats(player_id):
    if not player_id:
        return # User quit selection
    page = 0
    while True:
        results = get_player_stats(player_id, page)
        if not results:
            print_no_more_found("stats")
            break
        user_input =display_player_stats(page + 1, results)
        if user_input.lower() == 'q':
            break
        invalid_input()


def view_teams():
    """Controller to view all teams or a single team."""
    offset = 0
    all_teams = set()
    all_teams_id = set()
    while True:
        teams = get_teams(offset)
        all_teams.update(t[1] for t in teams)
        all_teams_id.update(t[0] for t in teams)
        user_input = display_teams(teams)
        if user_input == '': offset += 1; continue
        if user_input.lower() == 'q': return None
        if int(user_input) in all_teams_id: return user_input
        invalid_input()

         
def find_matches_for_team():
    print_select_from_list("team")
    user_input = view_teams()
    if not user_input:
        return 
    page = 0
    print_select_from_list("match")
    all_matches = set()
    while True:
        teamname, matches = get_matches_by_team(user_input,page)
        
        if not matches:
            break
        all_matches.update(m["id"] for m in matches)
        user_input2 = display_matches_for_team(teamname, matches)
        if user_input2 == '': page += 1; continue
        if user_input2.lower() == 'q': return None
        if int(user_input2) in all_matches: return find_matchstats(user_input2)
        invalid_input()

        

def find_matchstats(match_id):
    page = 0
    while True:
        results = get_match_stats(match_id, page)
        if not results:
            break
        user_input = display_match_stats(page + 1, results)
        if user_input.lower() == 'q': return None
        if user_input == '': page += 1; continue
        invalid_input()


def select_player():
    print_select_from_list("team")
    team_id = view_teams()
    if not team_id:
        return 
    all_player_ids = set()
    page = 0
    print_select_from_list("players")
    while True:
        players_to_show = get_players(team_id,page)
        if not players_to_show:
            print_no_more_found("players")
            break
        all_player_ids.update(p[1] for p in players_to_show)
        display_players_paginated(players_to_show)

        user_input = id_selection_input()
        if user_input.lower() == 'q': return None
        if user_input == '': page += 1; continue
        if user_input.isdigit() and int(user_input) in all_player_ids: return int(user_input)
        invalid_input()
    

def create_team():
    pass


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
    return calculate_standings_for_phase(phase_id)

def team_menu():
    while True:
        index = int(display_team_menu())
        if index == 1:
            view_teams()
        elif index == 2:
            create_team()
        elif index == 3:
            return  

def get_year():
    giwrgos = get_seasons()
    display_years(giwrgos)
    while True:
        year_id = get_year_input() 
        if year_id.lower() == 'q': return None
        if int(year_id) in giwrgos: break
        invalid_input()
    return year_id
    
def league_menu():
    year_id = get_year()
    while True:
        index = display_league_menu()
        if index == "1":
            phases = get_phases_for_year(year_id)
            group_phase = next((p for p in phases if p['phase_id'] == 1), None)
            print("\nCalculating Standings... (this may take a second)")
            standings = calculate_standings(group_phase['id'])
            display_standings(standings)

        elif index == "2":
            phases = get_phases_for_year(year_id)
            group_phase = next((p for p in phases if p['phase_id'] == 2), None)
            print("\nCalculating Standings... (this may take a second)")
            standings = calculate_standings(group_phase['id'])
            display_standings(standings)
        elif index == "3": 
            year_id = get_year()
            continue
        elif index == "4": return
        else:
            invalid_input()

        

def stats_menu():
    while True:
        index = int(display_stats_menu())
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
        exit = main_menu(int(display_main_menu()))
