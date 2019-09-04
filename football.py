from ff_espn_api import League
from datetime import datetime
import yaml


if __name__ == '__main__':

    # Load configuration file
    config = yaml.load(open('config.yaml', 'r'))

    # Initialize league
    league = League(league_id=config['league_id'],
                    year=datetime.today().year,
                    espn_s2=config['espn_s2'],
                    swid=config['swid'])

    # Get free agents
    agents = league.free_agents(size=5)
    for agent in agents:
        print(agent.__dict__)
