import requests
from bs4 import BeautifulSoup
import csv
import networkx as nx
import matplotlib.pyplot as plt

# Define the Steam URL for the top sellers
base_url = "https://store.steampowered.com/search/"

# Categories to scrape (updated categories)
categories = {
    "Action": "category1=998&tags=19",  # Action tag
    "Adventure": "category1=998&tags=21",  # Adventure tag
    "RPG": "category1=998&tags=122",  # RPG tag
    "Strategy": "category1=998&tags=9",  # Strategy tag
    "Indie": "category1=998&tags=492",  # Indie tag
    "Casual": "category1=998&tags=597",  # Casual tag
}

# Function to fetch top 10 games from a category
def fetch_top_games(category_url):
    try:
        response = requests.get(category_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the games section (Steam's structure might require specific adjustments)
        games_section = soup.find_all('a', class_='search_result_row')

        top_games = []
        for game in games_section[:10]:  # Limit to top 10 games
            game_title = game.find('span', class_='title').text.strip()
            top_games.append(game_title)

        return top_games

    except Exception as e:
        print(f"Error fetching category: {e}")
        return [""] * 10  # Return a list of empty strings if the category fails

# Main logic to fetch, save to CSV, and generate graphs
def main():
    all_top_games = []

    for category, params in categories.items():
        print(f"Fetching top 10 {category} games...")
        top_games = fetch_top_games(base_url + "?" + params)
        all_top_games.append(top_games)
        print(f"Top 10 {category} games: {top_games}")

        # Create a graph for each category
        G = nx.DiGraph()
        G.add_node(category, type='hub')

        for game in top_games:
            if game:  # Check if game title is not empty
                G.add_node(game, type='authority')
                G.add_edge(category, game)

        # Adjusted layout to shorten edges
        pos = nx.spring_layout(G, k=0.3, iterations=50)  # Decrease k to shorten edges
        plt.figure(figsize=(8, 6))

        # Draw nodes with different colors based on their type
        hub_nodes = [node for node, attr in G.nodes(data=True) if attr['type'] == 'hub']
        authority_nodes = [node for node, attr in G.nodes(data=True) if attr['type'] == 'authority']
        # Draw nodes with the same size and position legend with more space
        nx.draw_networkx_nodes(G, pos, nodelist=hub_nodes, node_color='skyblue', node_size=1000, label='Category')
        nx.draw_networkx_nodes(G, pos, nodelist=authority_nodes, node_color='lightgreen', node_size=1000, label='Games')

        nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrowstyle='->', arrowsize=15, edge_color='gray')

        # Add labels
        nx.draw_networkx_labels(G, pos, font_size=9, font_family='sans-serif')

        # Customize legend with more space between the legend and the graph
        plt.legend(
            scatterpoints=1,
            loc='upper right',  # Position in the top right corner
            fontsize='small',
            bbox_to_anchor=(1.1, 1.1),  # Add space between legend and graph
            ncol=2  # Place both labels in the same row
        )

        plt.title(f"Steam Top Games for {category}")
        plt.axis('off')
        plt.show()

    # Transpose the data so that each category becomes a column
    transposed_data = list(zip(*all_top_games))

    # Create and open a CSV file for writing
    with open('top_steam_games_by_category.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header row with category names
        writer.writerow(categories.keys())
        # Write each row of the transposed data
        writer.writerows(transposed_data)


main()
