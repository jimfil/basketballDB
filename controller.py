from model import get_match_stats,get_player_stats, get_player_shot_stats, get_scores
from view_cmd import *



def find_playerstats(player_id):
    for i in range(1000):
        results = get_player_stats(player_id, i)    #epistrefei Game -> Event Name -> Time
        display_player_stats(i + 1, results)
        if not results:
            break
        user_input = input("\nPress [Enter] to get next 10, or type 'q' to break: ")
        if user_input.lower() == 'q':
            print("Exiting...")
            break

def view_teams():
    pass

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



def main_menu(index):
    if index==1: view_teams()
    elif index==2: create_team()
    elif index==3: get_stats_menu()
    elif index==4: return True
    return False




if __name__ == "__main__":

    print("\n\t\t--->>Welcome to the BasketBall League<<---")
    exit = False
    while not exit:
        exit = main_menu(display_main_menu())

    
