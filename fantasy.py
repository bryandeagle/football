from bs4 import BeautifulSoup
from datetime import datetime, date
import requests


class Player:
    def __init__(self, name, rank):
        self.name = name
        self.rank = rank

    def __repr__(self):
        return '{} ({})'.format(self.name, self.rank)


def position_url(position):
    """ Add PPR to appropriate positions """
    if position.lower() in ['rb', 'wr', 'te']:
        return 'ppr-{}'.format(position.lower())
    else:
        return position.lower()


class Fantasy:
    def __init__(self):
        self.base_url = 'https://www.fantasypros.com/nfl/rankings'
        self.week = datetime.today().isocalendar()[1]-35
        self.year = datetime.today().year

    def _parse_table(self, page):
        """ Parses a Fantasy Pros ranking table """
        page = requests.get('{}/{}'.format(self.base_url, page))
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find('table', id='rank-data').find('tbody')
        for row in table.findAll('tr', {'class': 'player-row'}):
            yield (Player(name=row.find('a', {'class': 'fp-player-link'})['fp-player-name'],
                          rank=int(row.find('td').text)))

    def season_rankings(self, position):
        """ Get season rankings """
        return self._parse_table('ros-{}.php?year={}'.format(position_url(position), self.year))

    def week_rankings(self, position):
        """ Get weekly rankings """
        return self._parse_table('ros-{}.php?week={}'.format(position_url(position), self.week))
