#!/usr/bin/python
#2024-25
from Cdata_getter2024 import DataGetter
import time
#games/{season}/{game_id}/**files.csv:    Created in accessNBA_API_BoxScores
#                After they have been created, you can set manual_pull to false and build the player dict from these files
#p_inf_meta arg: True: Manually builds player dict, for start of each season
#                False: Reads the dict saved to players/player_json/player_info.json
#manual_pull:    True: Builds the player dict from NBA API endpoints
#                False: Builds the player dict from saved games

start_time = time.time()

DataGetter(execution='run1', p_inf_meta=True, manual_pull=False, season='2024-25')
runone_time = time.time() / 60

DataGetter(execution='run2', season='2024-25')
runtwo_time = time.time() / 60




'''
1. Predict possessions for a game -Active Team Data, Static Attributes |where: game
2. Use the player pace to projected minutes to calculate expcted team pace
3. use both team paces to project total pace
4. Apply total pace to 48 minutes for total possessions
5. predict team possession results
'''

import os
import pandas as pd

# Define your directories and columns
directory = 'players/matchups/data/'
output_directory = 'players/gameMicro/'
subdirs = ['offense', 'defense']
performance_columns = ['Player Points', 'Team Points', 'Matchup Assists']

# Ensure the output directory exists
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

def calculate_adjusted_metrics(df, total_possessions_by_game):
    """
    Calculate adjusted metrics for the DataFrame and append as new columns.
    """
    for col in performance_columns:
        adjusted_col_name = f"Adjusted_{col}"
        df[adjusted_col_name] = df[col] * total_possessions_by_game / df['partialPossessions']
        if col == 'Player Points' and 'Avg Pts' in df.columns:
            # Compute the difference and create a new column
            df['Adjusted_Points_Difference'] = df[adjusted_col_name] - df['Avg Pts']
    return df

def process_player_file(filepath):
    """
    Process each player file to calculate and append adjusted metrics.
    """
    try:
        df = pd.read_csv(filepath)
        df['partialPossessions'].replace(0, pd.NA, inplace=True)
        total_possessions_by_game = df.groupby('Game_Id')['partialPossessions'].transform('sum')
        df = calculate_adjusted_metrics(df, total_possessions_by_game)
        return df
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def main():
    for subdir in subdirs:
        current_output_directory = f'players/gameMicro/{subdir}/'  # Avoid overwriting the global output_directory variable
        path = os.path.join(directory, subdir)
        for filename in os.listdir(path):
            if 'processed' in filename:
                pass
            else:                    
                if filename.endswith(".csv") and not filename.startswith('._'):
                    filepath = os.path.join(path, filename)
                    processed_df = process_player_file(filepath)
                    if processed_df is not None:
                        new_filepath = os.path.join(current_output_directory, filename)
                        processed_df.to_csv(new_filepath, index=False)
                        print(f"Processed and saved: {new_filepath}")

main()  # Call the main function to start the process



print(f"Run One: {runone_time - start_time}   Run Two: {runtwo_time - runone_time}")


#for sub dir in subdirs, go through each of these directories for every file in it 'directory + subdir', and then all the player files will be here
#i want each player file read into a csv, i want it subgrouped by 'Game_Id' column so that i can calculate submetrics for each game.
#i want to use the total possessions (sum of 'partialPossessions' column, and calculate each row's(opposing player) performance relative to a full game of the players stattistics
#for example if one row the partialPossessions was 32.3 and the total possessions is 55, i want to use 55/32.5 to caputre its relation to ttoal playing time and use this factor to multiply all the performance columns by to find the expected stats peformance for the whole game
#we will be able to see, irregardless of possessions guarded the variances in statistics for each opponents efficieny
#for example to see if one player was matched up for all possessions ina  game, what would the 'Player Points' be?
#We examine the efficenies betweeen playes to see who drops or spikes where in what performance categories