from bs4 import BeautifulSoup
from ff_espn_api import League
from datetime import datetime
import requests

CONFIG_FILE = 'config.yaml'


class Email:
    def __init__(self, config):
        self.url = config['mg_url']
        self.api_key = config['api_key']
        self.to = config['to']
        self.from_addr = config['from']

    def send(self, subject, html):
        return requests.post(self.url,
                             auth=('api', self.api_key),
                             data={'from': self.from_addr,
                                   'to': [self.to],
                                   'subject': '{} 🏈'.format(subject),
                                   'html': html})


class Football:
    def __init__(self, config):
        self.team_id = config['team_id']
        self.league = League(league_id=config['league_id'],
                             year=datetime.today().year,
                             espn_s2=config['espn_s2'],
                             swid=config['swid'])

    @staticmethod
    def _sanitize_players(players):
        for p in players:
            if p.position == 'D/ST':
                p.name = p.name.replace(' D/ST', '')
                p.position = 'DST'
            else:
                p.name = p.name.replace('.', '')
        return players

    def get_espn_roster(self, position):
        if position == 'DST':
            position = 'D/ST'
        players = self.league.get_team_data(self.team_id).roster
        position_players = [p for p in players if p.position == position]
        return self._sanitize_players(position_players)

    def get_espn_players(self, position):
        if position == 'DST':
            position = 'D/ST'
        free_agents = self.league.free_agents(week=None, size=1000, position=position)
        return self._sanitize_players(free_agents)

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
