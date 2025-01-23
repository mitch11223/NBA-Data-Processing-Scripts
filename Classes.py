import json
import pandas
from tabulate import tabulate
from itertools import zip_longest
from nba_api.live.nba.endpoints import scoreboard
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

class DataLoader:
    def __init__(self):
        self.rosters = self._load_rosters()
        self.players = self._load_players()
        
    @staticmethod
    def _load_rosters():
        with open('teams/metadata/rosters/team_rosters.json', 'r') as rosters_file:
            return json.load(rosters_file)
    
    @staticmethod
    def _load_players():
        with open('players/player_json/player_info.json', 'r') as players_file:
            return json.load(players_file)




class League:
    def __init__(self):
        self.data_loader = DataLoader()		#Allows children to access League Data efficiently
        self.todays_games_object_roster = self._get_todays_games_object_roster()		#Game Dict
        self.todays_games_object_list = self._get_todays_games_object_list()			#Game Objects
        self.players = self._read_players()
        
    def _read_players(self):
        with open('players/player_json/player_info.json') as f:
            players = json.load(f)
        
        return players
    def _get_todays_games_object_roster(self):
        todays_games = scoreboard.ScoreBoard().games.get_dict()  # list
        todays_games_object_roster = {}
        for game_dict in todays_games:
            game = Game(game_dict, self.data_loader)
            todays_games_object_roster[game.gameCode] = game
        
        return todays_games_object_roster
    
    def _get_todays_games_object_list(self):
        todays_games_object_list = []
        for game_code, game_object in self.todays_games_object_roster.items():
            todays_games_object_list.append(game_object)
        
        return todays_games_object_list
    
   
class Game:
    def __init__(self, game_dict, data_loader):
        self.data_loader = data_loader
        self._unpack_game(game_dict)
    
    def Print_Game_Meta(self):
        away = self.away
        home = self.home
        
        print(f"{away.team_abbr}@{home.team_abbr}  {self.gameStatusText}")
        table_data = list(zip_longest(away.player_list, home.player_list, fillvalue=''))
        table = tabulate(table_data, headers=['Away Players', 'Home Players'], tablefmt="plain", stralign="left")
        print(table)
                
        
    def _unpack_game(self, game_dict):
        self.gameId = game_dict.get('gameId')
        self.gameCode = game_dict.get('gameCode')
        self.gameStatus = game_dict.get('gameStatus')
        self.gameStatusText = game_dict.get('gameStatusText')
        self.period = game_dict.get('period')
        self.gameClock = game_dict.get('gameClock')
        self.gameTimeUTC = game_dict.get('gameTimeUTC')
        self.gameEt = game_dict.get('gameEt')
        self.regulationPeriods = game_dict.get('regulationPeriods')
        self.ifNecessary = game_dict.get('ifNecessary')
        self.seriesGameNumber = game_dict.get('seriesGameNumber')
        self.gameLabel = game_dict.get('gameLabel')
        self.gameSubLabel = game_dict.get('gameSubLabel')
        self.seriesText = game_dict.get('seriesText')
        self.seriesConference = game_dict.get('seriesConference')
        self.poRoundDesc = game_dict.get('poRoundDesc')
        self.gameSubtype = game_dict.get('gameSubtype')
        
        #Home and Away Team Details
        self.homeTeam = game_dict.get('homeTeam', {})
        self.awayTeam = game_dict.get('awayTeam', {})
        
        #Game Leaders (Note: These might be empty if the game hasn't started)
        self.gameLeaders = game_dict.get('gameLeaders', {})
        
        #Betting Odds
        self.pbOdds = game_dict.get('pbOdds', {})
        
        if self.homeTeam:
            self.homeTeamId = self.homeTeam.get('teamId')
            self.homeTeamTricode = self.homeTeam.get('teamTricode')
            self.home = Team(self.homeTeamTricode, self.data_loader)
        
        if self.awayTeam:
            self.awayTeamId = self.awayTeam.get('teamId')
            self.awayTeamTricode = self.awayTeam.get('teamTricode')
            self.away = Team(self.awayTeamTricode, self.data_loader)





class Team:
    def __init__(self, team_abbr, data_loader):
        self.team_abbr = team_abbr
        self.data_loader = data_loader
        self.json_roster = self._get_roster()
        self.player_object_roster = self._build_player_object_roster() #{Aaron Wiggins: 'his object',...}
        self._set_attributes()
    
    def _get_roster(self):
        return self.data_loader.rosters.get(self.team_abbr, 'No Team Found')
        
    def _build_player_object_roster(self):
        player_object_roster = {}
        for player_name in self.json_roster.keys():
            player_object_roster[player_name] = Player(player_name, self.data_loader)
        return player_object_roster
    
    def _set_attributes(self):
        self.player_list = [key for key,value in self.json_roster.items()]		#All Rostered Players
        

class Player:
    def __init__(self, name, data_loader):
        self.name = name
        self.data_loader = data_loader
        self._set_player_attributes()
    
    def _set_player_attributes(self):
        self.player_info = self.data_loader.players.get(self.name, {})		#dict - {Jabari Smith: {attrs}...}
        self.props = {}
        



#####################

#####################
        



class Scraper:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.driver = None

    def get_player_stat_url(self, player_name, stat):
        """Format the URL for the player's stat."""
        base_url = "https://www.bettingpros.com/nba/props/"
        player_name_fmt = name_normalizer_bp(player_name)
        formatted_name = player_name_fmt.lower().replace(" ", "-")
        return f"{base_url}{formatted_name}/{stat}/"
    



    def fetch_historical_odds(self, url, max_attempts=3):
        """Fetch the historical odds for a given player and stat using Selenium with retry logic."""
        try:
            if not self.driver:
                self.driver = webdriver.Chrome(options=self.options)
            
            for attempt in range(max_attempts):
                self.driver.get(url)
                WebDriverWait(self.driver, 10)  # Wait for elements to be present, but does not wait for content to load fully
                sleep_time = 10 + (attempt * 3)  # Increase sleep time with each attempt
                time.sleep(sleep_time)  # Wait for the page to fully load
                
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                tables = soup.find_all('table')

                for table in tables:
                    headers = table.find('thead')
                    if headers:
                        header_rows = headers.find_all('tr')
                        header_cols = header_rows[0].find_all('th')
                        column_names = [header.text.strip() for header in header_cols]
                        
                        if 'Matchup' in column_names:
                            body = table.find('tbody')
                            if body:
                                rows = body.find_all('tr')
                                data = []
                                for row in rows:
                                    cols = row.find_all('td')
                                    cols = [col.text.strip() for col in cols]
                                    if cols:  
                                        data.append(cols)
                                
                                df = pandas.DataFrame(data, columns=column_names)                            
                                df = normalize_date_col(df)
                                
                                return df
                
                if attempt == max_attempts - 1:
                    return "No table with 'Matchup' column found after multiple attempts"
                else:
                    print(f"Attempt {attempt + 1} failed. Retrying with longer wait...")

            return "Failed to fetch data"  # This should not be reached if max_attempts logic is correct

        except Exception as e:
            print(f"An error occurred: {e}. Probably a player -> bp format mismatch.")
            return "Failed to fetch data"
        
        
    def scrape_historical(self, player):
        stats_to_scrape = ['points', 'assists', 'rebounds', 'points-assists-rebounds']
        all_data = {}

        for stat in stats_to_scrape:
            url = self.get_player_stat_url(player, stat)
            print(f"Scraping URL: {url}")
            artifact = self.fetch_historical_odds(url)  # df
            
            if isinstance(artifact, pandas.DataFrame):
                prop_df = pandas.DataFrame({
                    'GAME_DATE': artifact['GAME_DATE'],
                    f'{stat}_line': artifact['Prop Line']
                })
                all_data[stat] = prop_df
            else:
                print(f"{player} - {stat} data not found: {artifact}\n")

        if all_data:
            combined_df = pandas.concat(all_data.values(), axis=1, join='outer')
            combined_df = combined_df.reset_index()
            if 'index' in combined_df.columns:
                combined_df = combined_df.rename(columns={'index': 'GAME_DATE'})
            return combined_df
        else:
            return "No valid data found for any stat."
                    
                    
           
            
        
        

   
        
        
    
    def fetch_todays_odds(self, url):
        """Fetch the odds for a given player and stat using Selenium."""
        try:
            if not self.driver:
                self.driver = webdriver.Chrome(options=self.options)
            
            self.driver.get(url)
            # Adjust this wait time based on network speed and page load time
            time.sleep(5)
            
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            odds_element = soup.find('span', class_='typography odds-cell__line')
            
            if odds_element:
                return odds_element.text.strip()
            else:
                return "Odds not found"
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return "Failed to fetch data"

    def scrape_today(self, League):
        """Scrape odds for players playing today."""
        todays_participants = []
        for Game in League.todays_games_object_list:
            teams = [Game.home.player_object_roster, Game.away.player_object_roster]
            for team in teams:
                for player_name, obj in team.items():
                    if 'gamelogs' in obj.player_info.keys() and obj.player_info['gamelogs']['AVG_MIN'] >= 15:
                        todays_participants.append({'player': player_name, 'stat': 'points'})

        results = []
        invalid_results = []
        for player in todays_participants:
            url = self.get_player_stat_url(player['player'], player['stat'])
            prop = self.fetch_todays_odds(url)
            if self.is_valid_prop_format(prop):
                prop = prop.replace('O ','')
                results.append((player['player'], player['stat'], prop))
                print(f"{player['player']} {player['stat']}: {prop}")
            else:
                invalid_results.append((player['player'], player['stat'], prop))

        return results, invalid_results

    def __del__(self):
        """Ensure the driver is closed when the object is destroyed."""
        if self.driver:
            self.driver.quit()
    
    def is_valid_prop_format(self, prop):
        return '+' not in prop and '-' not in prop and prop != 'Odds not found'



















####################
#Utils
####################
#Normalizes the player name format for betting pros scraping
def name_normalizer_bp(name):
    if name == 'Nic Claxton':
        return 'Nicolas Claxton'
    else:
        return name
    

def normalize_date_col(df):
    df = df.rename(columns={'Date': 'GAME_DATE'})
    try:
        df['GAME_DATE'] = df['GAME_DATE'].apply(lambda x: pandas.to_datetime(
            f'2024-{x}' if int(x.split('/')[0]) >= 6 else f'2025-{x}', 
            format='%Y-%m/%d', errors='coerce'
        ))
        df['GAME_DATE'] = df['GAME_DATE'].dt.strftime('%b %d, %Y').str.upper()
    except ValueError:
        pass
    except AttributeError as e:
        print(f'Attribute Error in normalize_date_col {e}')
    
    return df

#Matches a player, spec. dataframe col to the players gamelogs file
def match_and_append_artifact_columns(player, dataframe):
    print('Trying Prop Gamelogs Merge for Player: ', player)
    first_csv = pandas.read_csv(f"players/gamelogsv2/{player}_log.csv")
    prop_df = normalize_date_col(dataframe)
    
    stat_columns = [col for col in prop_df.columns if col != 'GAME_DATE']
    merged_df = pandas.merge(first_csv, prop_df[['GAME_DATE'] + stat_columns], on='GAME_DATE', how='left') 
    merged_df.to_csv(f"test/{player}.csv", index=False)
    
    
    
    