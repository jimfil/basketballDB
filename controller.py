from model import get_match_stats,get_player_stats, get_player_shot_stats
from view import *



def find_playerstats(player_id):
    for i in range(1000):
        print(f"\nPage {i + 1}\t")
        print(f"{'Game':<8}{'Event Made':<28}{'Time'}") #dwse toulaxiston 28 spaces apo event mexri to time klp
        results = get_player_stats(player_id, i)    #epistrefei Game -> Event Name -> Time
        if not results:
            print("No more stats found for this Player.")
            break
        for row in results:
            match_id, event_name, game_time = row   
            print(f"{match_id:<8}{event_name:<28}{str(game_time)}")
        user_input = input("\nPress [Enter] to get next 10, or type 'q' to break: ")
        if user_input.lower() == 'q':
            print("Exiting...")
            break

def find_matchstats(match_id):
    for i in range(1000):
        print(f"\n\tPage {i + 1}\t")
        print(f"{'Team:':<20}{'Number Shirt':<15}{'Player':<20}{'Event Made':<28}{'Time'}")
        results = get_match_stats(match_id, i)
        if not results:
            print("No more events found for this Match.")
            break
        for row in results:
            shirt_number, last_name,event_name, game_time,team_id = row   
            print(f"{team_id:<20}{shirt_number:<15}{last_name:<20}{event_name:<28}{str(game_time)}")
        user_input = input("\nPress [Enter] to get next 10, or type 'q' to break: ")
        if user_input.lower() == 'q':
            print("Exiting...")
            break

def find_player_2pt_percentage(player_id, match_id=None):
    """ Έχουμε field goals attempts και field goals made. Τα attempts είναι καλάθια που ΔΕΝ έχουν μπει
    Άρα total = attempts + made"""

    stats = get_player_shot_stats(player_id, '2-Point Field Goal', match_id)
    made = stats.get('2-Point Field Goal Made', 0)
    attempts = stats.get('2-Point Field Goal Attempt', 0)
    total_attempts = made + attempts

    if total_attempts == 0:
        percentage = 0
    else:
        percentage = (made / total_attempts) * 100

    scope = f"in match {match_id}" if match_id else "for their career"
    print(f"\n--- 2-Point Shot Analysis for Player {player_id} {scope} ---")
    print(f"Shots Made:     {made}")
    print(f"Shots Missed:   {attempts}")
    print(f"Total Attempts: {total_attempts}")
    print(f"Percentage:     {percentage:.2f}%")

def find_player_3pt_percentage(player_id, match_id=None):
    """ Έχουμε field goals attempts και field goals made. Τα attempts είναι καλάθια που ΔΕΝ έχουν μπει
    Άρα total = attempts + made"""

    stats = get_player_shot_stats(player_id, '3-Point Field Goal', match_id)
    made = stats.get('3-Point Field Goal Made', 0)
    attempts = stats.get('3-Point Field Goal Attempt', 0)
    total_attempts = made + attempts

    if total_attempts == 0:
        percentage = 0
    else:
        percentage = (made / total_attempts) * 100

    scope = f"in match {match_id}" if match_id else "for their career"
    print(f"\n--- 3-Point Shot Analysis for Player {player_id} {scope} ---")
    print(f"Shots Made:     {made}")
    print(f"Shots Missed:   {attempts}")
    print(f"Total Attempts: {total_attempts}")
    print(f"Percentage:     {percentage:.2f}%")

def find_player_foul_shot_percentage(player_id, match_id=None):
    """ Έχουμε field goals attempts και field goals made. Τα attempts είναι καλάθια που ΔΕΝ έχουν μπει
    Άρα total = attempts + made"""

    stats = get_player_shot_stats(player_id, 'Free Throw', match_id)
    made = stats.get('Free Throw Made', 0)
    attempts = stats.get('Free Throw Attempt', 0)
    total_attempts = made + attempts

    if total_attempts == 0:
        percentage = 0
    else:
        percentage = (made / total_attempts) * 100

    scope = f"in match {match_id}" if match_id else "for their career"
    print(f"\n--- Foul Shot Analysis for Player {player_id} {scope} ---")
    print(f"Shots Made:     {made}")
    print(f"Shots Missed:   {attempts}")
    print(f"Total Attempts: {total_attempts}")
    print(f"Percentage:     {percentage:.2f}%")

if __name__ == "__main__":

    # Example Usage:
    # find_matchstats("50001")
    
    # Find career 2-point percentage for player 10001
    find_player_foul_shot_percentage("10001")
