#@title Graphical description of deviding the games (that returned in our query) into categories: Casual, Intense, Competitive  
import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact, widgets, VBox, HBox, Layout, HTML

# Load the CSV file, skipping the first two rows
file_path = 'query1-gamesPlaytime-new.csv'
data = pd.read_csv(file_path, skiprows=2)

# Assign correct column names based on the data provided
data.columns = ['game name', 'number of players', 'total playtime', 'playtime distribution', 'average playtime', 'Category']

def plot_side_by_side(data):
    # Create a figure with two subplots side by side
    fig, ax = plt.subplots(1, 2, figsize=(15, 6))

    # Plot 1: Number of Games by Game Category (horizontal bar chart)
    category_count = data['Category'].value_counts().sort_values(ascending=False)
    category_avg_playtime = data.groupby('Category')['average playtime'].mean().sort_values(ascending=False)
    
    # Assign playtime range labels based on the average playtime
    playtime_labels = []
    for category in category_avg_playtime.index:
        avg_playtime = category_avg_playtime[category]
        if avg_playtime > 70:
            label = f"{category} (70+ Average Playtime (hours))"
        elif avg_playtime > 30:
            label = f"{category} (30-70 Average Playtime (hours))"
        else:
            label = f"{category} (1-30 Average Playtime (hours))"
        playtime_labels.append(label)
    
    # Plotting the bar chart
    category_count.plot(kind='barh', color='skyblue', ax=ax[0])
    ax[0].set_title('Number of Games by Steam Game Category')
    ax[0].set_xlabel('Number of Games')
    ax[0].set_ylabel('Game Category')
    ax[0].grid(axis='x')

    # Annotate each bar with the number of games and the playtime range label
    for index, (value, label) in enumerate(zip(category_count, playtime_labels)):
        ax[0].annotate(f'{value}', xy=(value, index), 
                       xytext=(5, 0), textcoords='offset points',
                       ha='left', va='center', fontsize=10, color='black')
        ax[0].annotate(label, xy=(0, index), 
                       xytext=(5, -15), textcoords='offset points',
                       ha='left', va='center', fontsize=9, color='gray')

    # Plot 2: Number of Players vs. Average Playtime (scatter plot)
    ax[1].scatter(data['number of players'], data['average playtime'], alpha=0.7, color='teal')
    ax[1].set_title('Number of Players vs. Average Playtime')
    ax[1].set_xlabel('Number of Players')
    ax[1].set_ylabel('Average Playtime (hours)')
    ax[1].grid(True)

    plt.tight_layout()
    plt.show()

plot_side_by_side(data)



def interactive_game_selection(data):
    category_list = sorted(data['Category'].unique())  # Sort categories lexicographically

    category_dropdown = widgets.Dropdown(
        options=[(f'Select a Category', None)] + [(category, category) for category in category_list],  # Non-selectable placeholder
        description='Category',
        layout=Layout(width='50%')
    )

    game_dropdown = widgets.Dropdown(
        options=[],
        description='Game',
        layout=Layout(width='50%')
    )

    selected_game_label = HTML(value="")
    less_time_label = HTML(value="")
    more_time_label = HTML(value="")

    def update_game_list(*args):
        if category_dropdown.value:  # Ensure a category is selected
            filtered_data = data[data['Category'] == category_dropdown.value]
            game_list = sorted(filtered_data['game name'].unique())  # Sort games lexicographically
            game_dropdown.options = [(f'Select a Game', None)] + [(game, game) for game in game_list]  # Non-selectable placeholder
            game_dropdown.value = None  # Reset the game dropdown

            # Clear the labels if no game is selected
            selected_game_label.value = ""
            less_time_label.value = ""
            more_time_label.value = ""

    def display_playtime(*args):
        if game_dropdown.value:  # Ensure a game is selected
            game = game_dropdown.value
            selected_game = data[data['game name'] == game]
            avg_playtime = selected_game['average playtime'].values[0]
            num_players = selected_game['number of players'].values[0]

            # Find less and more time-consuming games in the same category
            category = selected_game['Category'].values[0]
            category_games = data[data['Category'] == category]

            # Find the closest less and more time-consuming games in the same category
            closest_less_time = category_games[category_games['average playtime'] < avg_playtime]
            if not closest_less_time.empty:
                closest_less_time = closest_less_time.iloc[(avg_playtime - closest_less_time['average playtime']).abs().argsort()[:1]]

            closest_more_time = category_games[category_games['average playtime'] > avg_playtime]
            if not closest_more_time.empty:
                closest_more_time = closest_more_time.iloc[(closest_more_time['average playtime'] - avg_playtime).abs().argsort()[:1]]

            # Updating the labels
            selected_game_label.value = f"<b>Selected Game:</b> {game} - Average Playtime: {avg_playtime:.2f} hours - Number of Players: {num_players}"

            if not closest_less_time.empty:
                less_game = closest_less_time['game name'].values[0]
                less_time_playtime = closest_less_time['average playtime'].values[0]
                less_time_players = closest_less_time['number of players'].values[0]
                less_time_label.value = f"<b>Less Time-Consuming Option:</b> {less_game} - {less_time_playtime:.2f} hours - Number of Players: {less_time_players}"
            else:
                less_time_label.value = "<b>Less Time-Consuming Option:</b> None"

            if not closest_more_time.empty:
                more_game = closest_more_time['game name'].values[0]
                more_time_playtime = closest_more_time['average playtime'].values[0]
                more_time_players = closest_more_time['number of players'].values[0]
                more_time_label.value = f"<b>More Time-Consuming Option:</b> {more_game} - {more_time_playtime:.2f} hours - Number of Players: {more_time_players}"
            else:
                more_time_label.value = "<b>More Time-Consuming Option:</b> None"


    category_dropdown.observe(update_game_list, 'value')
    game_dropdown.observe(display_playtime, 'value')

    ui = VBox([
        HBox([category_dropdown, game_dropdown]),
        selected_game_label,
        less_time_label,
        more_time_label
    ])

    display(ui)
print('\n\n\n')
interactive_game_selection(data)
