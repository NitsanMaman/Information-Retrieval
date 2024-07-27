import requests
import csv
import time
from collections import defaultdict

API_KEY = 'AAA55259E723CE31A80A0797843D5BC8'
CSV_FILE_PATH = '/content/drive/MyDrive/steam_ids_SHORT.csv'
STOP_WORDS = set([
    'a', 'about', 'actually', 'almost', 'also', 'although', 'always', 'am', 'an', 'and', 'any', 'are', 'as', 'at',
    'be', 'became', 'become', 'but', 'by', 'can', 'could', 'did', 'do', 'does', 'each', 'either', 'else', 'for',
    'from', 'had', 'has', 'have', 'hence', 'how', 'i', 'if', 'in', 'is', 'it', 'its', 'just', 'may', 'maybe', 'me',
    'might', 'mine', 'must', 'my', 'neither', 'nor', 'not', 'of', 'oh', 'ok', 'when', 'where', 'whereas', 'wherever',
    'whenever', 'whether', 'which', 'while', 'who', 'whom', 'whoever', 'whose', 'why', 'will', 'with', 'within',
    'without', 'would', 'yes', 'yet', 'you', 'your'
])

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

def get_global_achievements(appid):
    url = f'https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/'
    params = {
        'gameid': appid
    }
    response = requests.get(url, params=params)
    return response.json()

def load_steam_ids_from_csv(file_path):
    steam_ids = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            steam_ids.append(row[0])
    return steam_ids

def process_word(word):
    # Remove suffixes
    suffixes = ['ly', 'ed', 'ing', 's']
    for suffix in suffixes:
        if word.endswith(suffix):
            word = word[:-len(suffix)]
            break
    return word

def main():
    steam_ids = load_steam_ids_from_csv(CSV_FILE_PATH)
    achievement_word_count = defaultdict(int)
    game_ids = []

    for steam_id in steam_ids:
        owned_games = get_owned_games(steam_id)
        if 'response' in owned_games and 'games' in owned_games['response']:
            for game in owned_games['response']['games']:
                game_ids.append(game['appid'])
        time.sleep(1)  # To avoid hitting API rate limits

    for appid in game_ids:
        achievments_words = []
        achievements = get_global_achievements(appid)
        if 'achievementpercentages' in achievements and 'achievements' in achievements['achievementpercentages']:
            for achievement in achievements['achievementpercentages']['achievements']:
                name = achievement['name']
                words = name.split('_')[1:]  # Ignore the first word
                achievments_words.extend(words)
                for word in words:
                    word = process_word(word.lower())
                    if word not in STOP_WORDS and not any(char.isdigit() for char in word):
                        achievement_word_count[word] += 1
            print('All the words of achievments for game', appid, ' are: ', achievments_words)
        time.sleep(1)  # To avoid hitting API rate limits

    sorted_achievement_word_count = dict(sorted(achievement_word_count.items(), key=lambda item: item[1], reverse=True))

    print('Achievement word counts:', dict(sorted_achievement_word_count))

if __name__ == '__main__':
    main()


