from model import get_match_stats,get_player_stats
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
        results = get_match_stats(match_id, i)
        if not results:
            print("No more stats found for this Player.")
            break
        for row in results:
            print(row)
        user_input = input("\nPress [Enter] to get next 10, or type 'q' to break: ")
        if user_input.lower() == 'q':
            print("Exiting...")
            break

if __name__ == "__main__":

    find_playerstats(10000)