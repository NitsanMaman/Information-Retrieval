import requests
import csv
import time
import re
from collections import defaultdict
from bs4 import BeautifulSoup

API_KEY = 'AAA55259E723CE31A80A0797843D5BC8'
CSV_FILE_PATH = '/content/drive/MyDrive/steam_ids.csv'
STOP_WORDS = set([
    'a', 'about', 'actually', 'almost', 'also', 'although', 'always', 'am', 'an', 'and', 'any', 'are', 'as', 'at',
    'be', 'became', 'become', 'but', 'by', 'can', 'could', 'did', 'do', 'does', 'each', 'either', 'else', 'for',
    'from', 'had', 'has', 'have', 'hence', 'how', 'i', 'if', 'in', 'is', 'it', 'its', 'just', 'may', 'maybe', 'me',
    'might', 'mine', 'must', 'my', 'neither', 'nor', 'not', 'of', 'oh', 'ok', 'when', 'where', 'whereas', 'wherever',
    'whenever', 'whether', 'which', 'while', 'who', 'whom', 'whoever', 'whose', 'why', 'will', 'with', 'within',
    'without', 'would', 'yes', 'yet', 'you', 'your', 'to', 'the', 'this'
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

def load_steam_ids_from_csv(file_path):
    steam_ids = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            steam_ids.append(row[0])
    return steam_ids

def clean_word(word):
    # Remove non-alphabetic characters from the start and end of the word
    word = re.sub(r'^[^a-zA-Z]+|[^a-zA-Z]+$', '', word)
    return word

def process_word(word):
    # Remove suffixes
    suffixes = ['ly', 'ed', 'ing', '’s', 'es', 's']
    for suffix in suffixes:
        if word.endswith(suffix):
            word = word[:-len(suffix)]
            break
    return word

def parse_game_description(appid):
    url = f'https://store.steampowered.com/app/{appid}'
    response = requests.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    description_div = soup.find(id='game_area_description')

    if not description_div:
        return []

    text = description_div.get_text()
    words = []
    for word in re.split(r'\s+|[-—]', text):
        word = clean_word(word.lower())
        if word and word not in STOP_WORDS and not any(char.isdigit() for char in word):
            words.append(process_word(word))

    print("For game page with id ", appid , " the words are:" , words)
    return words

def main():
    steam_ids = load_steam_ids_from_csv(CSV_FILE_PATH)
    game_player_count = {}
    description_word_count = defaultdict(int)

    for steam_id in steam_ids:
        owned_games = get_owned_games(steam_id)
        if 'response' in owned_games and 'games' in owned_games['response']:
            for game in owned_games['response']['games']:
                appid = game['appid']
                if appid not in game_player_count:
                    game_player_count[appid] = 0
                game_player_count[appid] += 1
        time.sleep(1)  # To avoid hitting API rate limits

    # Filter game IDs with 20 or more players
    popular_game_ids = [appid for appid, count in game_player_count.items() if count >= 20]

    for appid in popular_game_ids:
        words = parse_game_description(appid)
        for word in words:
            description_word_count[word] += 1
        time.sleep(1)  # To avoid hitting API rate limits

    sorted_description_word_count = dict(sorted(description_word_count.items(), key=lambda item: item[1], reverse=True))

    print('Number of games with 20 or more players:', len(popular_game_ids))
    print('Description word counts:', sorted_description_word_count)

if __name__ == '__main__':
    main()
