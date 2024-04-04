from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.library.parameters import Season
from nba_api.stats.library.parameters import SeasonType
import csv

nba_teams = teams.get_teams()
heat = [team for team in nba_teams if team['abbreviation'] == 'MIA'][0]
heat_id = heat['id']


gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=heat_id,
                            season_nullable=Season.default,
                            season_type_nullable=SeasonType.regular)  

games_dict = gamefinder.get_normalized_dict()
games = games_dict['LeagueGameFinderResults']
game_ids = []
for game in games:
    game_id = game['GAME_ID']
    game_ids.append(game_id)
print(len(game_ids))
print(game_ids)



def copy_rows_with_game_ids(input_csv_file, output_csv_file, game_ids):
    with open(input_csv_file, 'r', newline='') as input_file, \
        open(output_csv_file, 'w', newline='') as output_file:
        csv_reader = csv.reader(input_file)
        csv_writer = csv.writer(output_file)
        
        for row in csv_reader:
            if row[0] in game_ids:
                csv_writer.writerow(row)


highlight_input = 'D:/Documents/GFA/SportsPython/Basketball/2023_play_by_play.csv'  # Replace with the path to your input CSV file
highlight_output = 'D:/Documents/GFA/SportsPython/Basketball/dadbirthday2024/data/heat_play_by_play_2023.csv'  # Path to the output CSV file
game_info_input = 'D:/Documents/GFA/SportsPython/Basketball/game_info_2023.csv'  # Replace with the path to your input CSV file
game_info_output = 'D:/Documents/GFA/SportsPython/Basketball/dadbirthday2024/data/heat_game_info_2023.csv'  # Path to the output CSV file
copy_rows_with_game_ids(highlight_input, highlight_output, game_ids)
copy_rows_with_game_ids(game_info_input, game_info_output, game_ids)