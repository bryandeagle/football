from bs4 import BeautifulSoup
from ff_espn_api import League
from datetime import datetime
import requests
import yaml


class Football:
    def __init__(self, config_file):
        config = yaml.load(open(config_file, 'r'))
        self.team_id = config['team_id']
        self.league = League(league_id=config['league_id'],
                             year=datetime.today().year,
                             espn_s2=config['espn_s2'],
                             swid=config['swid'])

    def get_espn_roster(self, position):
        players = self.league.get_team_data(self.team_id).roster
        if position == 'DST':
            return [p.name.replace(' D/ST', '') for p in players if p.position == 'D/ST']
        else:
            return [p.name.replace('.', '') for p in players if p.position == position]

    def get_espn_players(self, position):
        if position == 'DST':
            return [x.name.replace(' D/ST', '') for x in self.league.free_agents(week=None, size=1000, position='D/ST')]
        else:
            return [x.name.replace('.', '') for x in self.league.free_agents(week=None, size=1000, position=position)]

    @staticmethod
    def get_fpros_rankings(position, time):
        """ Scrapes ranking data from Fantasy Pros """
        if position in ['RB', 'WR', 'TE', 'FLEX']:
            position = 'PPR-{}'.format(position)
        if time == 'week':
            url = '{}.php?week={}'.format(position, datetime.today().isocalendar()[1] - 35)
        elif time == 'season':
            url = 'ros-{}.php?year={}'.format(position, datetime.today().year)
        else:
            raise ValueError('Valid times are week and season.')
        page = requests.get('{}/{}'.format('https://www.fantasypros.com/nfl/rankings', url.lower()))
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find('table', id='rank-data').find('tbody')
        players = list()
        for row in table.findAll('tr', {'class': 'player-row'}):
            name = row.find('a', {'class': 'fp-player-link'})['fp-player-name'].replace('.', '')
            if position == 'DST':
                players.append(name.split(' ')[-1])
            else:
                players.append(name)
        return players
