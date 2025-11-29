from model import get_match_stats,get_player_stats, get_player_shot_stats, get_scores, get_teams, get_player
from view_cmd import display_main_menu, display_player_stats, display_match_stats, display_shot_analysis, display_match_score, get_stats_menu, display_teams, display_team_menu, shot_percentage_menu, display_players_paginated, display_matches_for_team, get_player_selection_input



def find_playerstats(player_id):
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

def view_teams(team_id=None):
    """Controller to view all teams or a single team."""
    if team_id:
        teams = get_teams(team_id)
    else:
        teams = get_teams()
    display_teams(teams)
    input("Press Enter to continue...")
    return



def create_team():
    pass


def find_matchstats(match_id):
    for i in range(1000):
        results = get_match_stats(match_id, i)
        display_match_stats(i + 1, results)
        if not results:
            break
        user_input = input("\nPress [Enter] to get next 10, or type 'q' to break: ")
        if user_input.lower() == 'q':
            print("Exiting...")
            break

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



def team_menu(index):
    """Handles the team management menu logic."""
    if index == 1:
        view_teams()
    elif index == 2:
        create_team()
    elif index == 3:
        return  # Go back
    else: team_menu(int(display_team_menu()))

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

def select_player():
    all_player_ids = []
    page = 0
    while True:
        players_to_show = get_player(page)
        if not players_to_show:
            print("No more players found.")
            break
        all_player_ids.append(players_to_show)

        display_players_paginated(players_to_show)

        
        
        user_input = get_player_selection_input()
        if user_input.lower() == 'q': return None
        if user_input == '': page += 1; continue
        if user_input.isdigit() and int(user_input) in all_player_ids: return int(user_input)
        print("Invalid input. Please try again.")


def stats_menu(index):
    """Handles the team management menu logic."""
    if index == 1:
        find_playerstats(select_player())
    elif index == 2:
        pass
    elif index == 3:
        shot_percentage_control()
    elif index == 4:
        return  # Go back
    elif index == 5:
        return  # Go back
    else: stats_menu(int(get_stats_menu()))

def main_menu(index):
    if index==1: team_menu(int(display_team_menu()))
    elif index==2: pass
    elif index==3: stats_menu(int(get_stats_menu()))
    elif index==4: return True
    return False



if __name__ == "__main__":

    print("\n\t\t--->>Welcome to the BasketBall League<<---")
    exit = False
    while not exit:
        exit = main_menu(int(display_main_menu()))

    # Example of how to view a single team:
    # view_teams(team_id=1)
    