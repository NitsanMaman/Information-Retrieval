import requests
import csv
import time

API_KEY = 'AAA55259E723CE31A80A0797843D5BC8'
INITIAL_STEAM_ID = '76561198027836520'
MAX_IDS = 100
FILE_PATH = '/content/drive/MyDrive/steam_ids_SHORT.csv'

def get_friend_list(steam_id):
    url = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/'
    params = {
        'key': API_KEY,
        'steamid': steam_id,
        'relationship': 'friend'
    }
    response = requests.get(url, params=params)
    return response.json()

def collect_steam_ids(current_steam_id, collected_ids, processed_ids):
    if len(collected_ids) >= MAX_IDS:
        return collected_ids

    if current_steam_id in processed_ids:
        return collected_ids

    processed_ids.add(current_steam_id)

    friend_list = get_friend_list(current_steam_id)

    if 'friendslist' in friend_list:
        friends = friend_list['friendslist']['friends']
        for friend in friends:
            steam_id = friend['steamid']
            if steam_id not in collected_ids:
                collected_ids.add(steam_id)
                if len(collected_ids) >= MAX_IDS:
                    break
                time.sleep(1)  # To avoid hitting API rate limits
                collect_steam_ids(steam_id, collected_ids, processed_ids)

    return collected_ids

def save_to_csv(steam_ids):
    with open(FILE_PATH, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['SteamID'])
        for steam_id in steam_ids:
            writer.writerow([steam_id])

def main():
    collected_ids = set()
    processed_ids = set()

    collected_ids = collect_steam_ids(INITIAL_STEAM_ID, collected_ids, processed_ids)

    save_to_csv(collected_ids)
    print('Collected Steam IDs saved to steam_ids.csv')

if __name__ == '__main__':
    main()
