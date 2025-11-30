from model import get_match_stats, get_matches_by_team,get_player_stats, get_player_shot_stats, get_scores, get_teams, get_players
from view_cmd import display_main_menu, display_player_stats, display_match_stats, display_shot_analysis, display_match_score, get_stats_menu, display_teams, display_team_menu, shot_percentage_menu, display_players_paginated, display_matches_for_team, id_selection_input



def find_playerstats(player_id):
    if not player_id:
        return # User quit selection
    for i in range(1000):
        results = get_player_stats(player_id, i)    #epistrefei Game -> Event Name -> Time
        display_player_stats(i + 1, results)
        if not results:
            print("No more stats found for this Player. Exiting...")
            break
        user_input = input("\nPress [Enter] to get next 10, or type 'q' to break: ")
        if user_input.lower() == 'q':
            print("Exiting...")
            break

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
        if user_input.lower() == 'q': return user_input
        if int(user_input) in all_teams_id: return user_input
         
def find_matches_for_team():
    print("Please select a team from the list below.")
    user_input = view_teams()
    if user_input == 'q':
        return 
    page = 0
    print("Now select a match.")
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
        

def find_matchstats(match_id):
    page = 0
    while True:
        results = get_match_stats(match_id, page)
        if not results:
            break
        user_input = display_match_stats(page + 1, results)
        if user_input.lower() == 'q': return None
        if user_input == '': page += 1; continue




def select_player():
    all_player_ids = set()
    page = 0
    while True:
        players_to_show = get_players(page)
        if not players_to_show:
            print("No more players found.")
            break
        all_player_ids.update(p[1] for p in players_to_show)
        display_players_paginated(players_to_show)

        user_input = id_selection_input()
        if user_input.lower() == 'q': return None
        if user_input == '': page += 1; continue
        if user_input.isdigit() and int(user_input) in all_player_ids: return int(user_input)
        print("Invalid input. Please try again.")


def create_team():
    pass


def find_player_shot_percentage(player_id, shot_type, match_id=None):
    """
    Generic function to calculate and display shot percentages for a player.
    :param player_id: The ID of the player.
    :param shot_type: The base name of the shot (e.g., '2-Point Field Goal', 'Free Throw').
    :param match_id: Optional ID of a match to filter stats for.
    """
    # 1. Get data from the Model
    stats = get_player_shot_stats(player_id, shot_type, match_id)

    # 2. Perform business logic/calculations
    made = stats.get(f'{shot_type} Made', 0)
    missed = stats.get(f'{shot_type} Attempt', 0)
    total_attempts = made + missed

    if total_attempts == 0:
        percentage = 0
    else:
        percentage = (made / total_attempts) * 100

    # 3. Prepare data for the View
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

    # 4. Pass data to the View for display
    display_shot_analysis(analysis_data)

def obtain_match_scores(match_id):
    scores = get_scores(match_id)
    if scores:
        display_match_score(match_id, scores)
    else:
        print(f"Match with ID {match_id} not found.")


def team_menu():
    while True:
        index = int(display_team_menu())
        if index == 1:
            view_teams()
        elif index == 2:
            create_team()
        elif index == 3:
            return  # Go back

def shot_percentage_control():
    player_id = select_player()
    if not player_id:
        return # User quit selection

    choice = shot_percentage_menu()
    shot_map = {
        "1": "Free Throw",
        "2": "2-Point Field Goal",
        "3": "3-Point Field Goal"
    }
    if choice in shot_map:
        find_player_shot_percentage(player_id, shot_map[choice])
    # "4" is back, so we do nothing.




def stats_menu():
    while True:
        index = int(get_stats_menu())
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
    elif index==2: pass
    elif index==3: stats_menu()
    elif index==4: return True
    return False



if __name__ == "__main__":

    print("\n\t\t--->>Welcome to the BasketBall League<<---")
    exit = False
    while not exit:
        exit = main_menu(int(display_main_menu()))

    # Example of how to view a single team:
    # view_teams(team_id=1)
    