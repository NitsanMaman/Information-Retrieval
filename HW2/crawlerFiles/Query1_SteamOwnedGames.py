import requests
import json
import time
import csv

API_KEY = 'AAA55259E723CE31A80A0797843D5BC8'
CSV_FILE_PATH = '/content/drive/MyDrive/steam_ids.csv'
OUTPUT_CSV_PATH = '/content/drive/MyDrive/query1-gamesPlaytime.csv'

def get_owned_games(steam_id):
    url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
    params = {
        'key': API_KEY,
        'steamid': steam_id,
        'include_played_free_games': 1,
        'include_appinfo': 1
    }
    response = requests.get(url, params=params)
    return response.json()

def calculate_statistics(player_game_data):
    game_stats = {}

    for player, games in player_game_data.items():
        for game in games:
            if game['playtime_forever'] > 0:
                appid = game['appid']
                name = game['name']
                playtime_forever = game['playtime_forever'] / 60  # Convert minutes to hours

                if name not in game_stats:
                    game_stats[name] = {
                        'total_playtime': 0,
                        'num_players': 0,
                        'playtime_distribution': []
                    }

                game_stats[name]['total_playtime'] += playtime_forever
                game_stats[name]['num_players'] += 1
                game_stats[name]['playtime_distribution'].append(playtime_forever)

    for name, stats in game_stats.items():
        stats['average_playtime'] = stats['total_playtime'] / stats['num_players']

    # Filter games with 20 or more players
    filtered_game_stats = {name: stats for name, stats in game_stats.items() if stats['num_players'] >= 20}
    num_games_with_20_or_more_players = len(filtered_game_stats)

    return len(game_stats), num_games_with_20_or_more_players, filtered_game_stats

def load_steam_ids_from_csv(file_path):
    steam_ids = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            steam_ids.append(row[0])
    return steam_ids

def main():
    steam_ids = load_steam_ids_from_csv(CSV_FILE_PATH)
    player_game_data = {}

    for steam_id in steam_ids:
        owned_games = get_owned_games(steam_id)
        if 'response' in owned_games and 'games' in owned_games['response']:
            player_game_data[steam_id] = owned_games['response']['games']
        time.sleep(1)  # To avoid hitting API rate limits

    total_games, num_games_with_20_or_more_players, game_stats = calculate_statistics(player_game_data)

    with open(OUTPUT_CSV_PATH, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([f'Total number of games found: {total_games}'])
        writer.writerow([f'Number of games with 20 or more players: {num_games_with_20_or_more_players}'])
        writer.writerow(['game name', 'number of players', 'total playtime', 'playtime distribution', 'average playtime'])

        for name, stats in game_stats.items():
            writer.writerow([name, stats['num_players'], stats['total_playtime'], stats['playtime_distribution'], stats['average_playtime']])

    print(f'Results saved to {OUTPUT_CSV_PATH}')

if __name__ == '__main__':
    main()
