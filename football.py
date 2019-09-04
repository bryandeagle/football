from ff_espn_api import League
from datetime import datetime
import yaml

CONFIG_FILE = 'config.yaml'


class Football:
    def __init__(self, config_file):
        # Load configuration file
        config = yaml.load(open(config_file, 'r'))

        # Initialize league
        self.league = League(league_id=config['league_id'],
                             year=datetime.today().year,
                             espn_s2=config['espn_s2'],
                             swid=config['swid'])

    def top_players(self, position):
        return self.league.free_agents(week=None, size=1000, position=position)


if __name__ == '__main__':

    league = Football(CONFIG_FILE)
    x = league.top_players('QB')
    for p in x:
        print(p.__dict__)
