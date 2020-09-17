from logging import Formatter, getLogger, INFO, StreamHandler
from functools import cached_property, lru_cache
from ff_espn_api import League
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import toml
import sys
import os
import re

# Create handler
_handler = StreamHandler(sys.stdout)
_handler.setFormatter(Formatter(fmt='[%(levelname)s] %(message)s'))
_handler.setLevel(INFO)

# Creat log object
log = getLogger(__name__)
log.addHandler(_handler)
log.setLevel(INFO)


def _create_id(name, position, custom_ids=None):
    if custom_ids and name.replace(' ', '_') in custom_ids:
        return custom_ids[name.replace(' ', '_')]
    name = re.sub(r'(IX|IV|V?I{0,3})$|(Jr\.?)$|(D/?ST)$', '', name)

    if position != 'DST':  # Shorten to first-initial last name
        name = name.split()[0][0] + name.split()[-1]

    pid = '{}{}'.format(position.lower(), name.lower())
    return re.compile('[^a-z]').sub('', pid)


class Player:
    def __init__(self, espn_player):
        self.name = espn_player.name
        self.espn_id = espn_player.playerId
        self.position = re.compile('[^A-Z]').sub('', espn_player.position)
        self.team = espn_player.proTeam
        self.projection = {'week': 0, 'season': 0}
        self.id = _create_id(self.name, self.position, {})

    def __repr__(self):
        return self.name


class Football:
    def __init__(self):
        self.config = self._read_config()
        swid, espn_s2 = self._get_secrets('SWID', 'ESPN_S2')
        self._week = self._get_week(self.config['general']['start_week'])

        # Initiatlize ESPN league API
        self.league = League(league_id=self.config['general']['league_id'],
                             year=datetime.today().year,
                             espn_s2=espn_s2,
                             swid=swid)

        self._team_id = self._get_team_id(self.config['general']['owner'])

    def _get_team_id(self, owner):
        """ Get the team ID given the owner """
        for team in self.league.standings():
            if team.owner == owner:
                return team.team_id

    @staticmethod
    def _get_week(week_one):
        """ Get the NFL week number given the first week """
        week_dt = datetime.strptime(week_one, '%Y-%m-%d')
        return int(datetime.today().strftime('%W')) - int(week_dt.strftime('%W')) + 1

    @staticmethod
    def _read_config():
        """ Read the configuration TOML file """
        this_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(this_dir, 'config.toml')) as f:
            return toml.loads(f.read())

    @staticmethod
    def _get_secrets(*kwargs):
        """ Get the secrets from environment variables """
        var_list = list()
        for var_name in kwargs:
            var_val = os.getenv(var_name)
            if var_val is None:
                raise ValueError('{} secret not found'.format(var_name))
            var_list.append(var_val)
        return var_list

    @lru_cache(maxsize=12)
    def _stats(self, position, time):
        week = 'draft' if time == 'season' else self._week
        url = 'https://www.fantasypros.com/nfl/projections'
        page = requests.get('{}/{}.php?week={}'.format(url, position.lower(), week))
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find('table', id='data').find('tbody')
        stats = dict()
        for row in table.findAll('tr'):
            # Get player information
            columns = row.find_all('td')
            name = columns[0].find('a', {'class': 'player-name'}).text
            team = columns[0].find_all(text=True)[1]

            stat = dict()
            for i, cell in enumerate(columns[1:-1]):
                col = self.config['fantasy_pros'][position][i]
                if col != '':
                    stat[col] = float(cell.contents[0].replace(',', ''))
            stats[_create_id(name, position, self.config['custom_ids'])] = stat
        return stats

    def _calc_score(self, player):
        """ Calculates a players projected weekly and season scores """
        scores = dict()
        for time in ['week', 'season']:
            if player.id not in self._stats(player.position, time):
                log.warning('{} not found in Fantasy Pros {}'.format(player.name, time))
                scores[time] = 0
            score = 0
            stats = self._stats(player.position, time)[player.id]
            for item in stats:
                if item in self.config['espn_scoring']:
                    score += stats[item] * self.config['espn_scoring'][item]
                elif item in ['points_allowed', 'yards_allowed']:
                    for v in self.config[item]:
                        if stats[item] < int(v):
                            score += self.config[item][v]
                            break
                else:
                    raise ValueError('Unknown stat {}'.format(item))
            scores[time] = score
        return scores

    @cached_property
    def roster(self):
        """ Get the team roster """
        result = {'QB': [], 'RB': [], 'WR': [], 'TE': [], 'K': [], 'DST': []}
        for p in self.league.get_team_data(self._team_id).roster:
            player = Player(p)
            player.projection = self._calc_score(player)
            result[player.position].append(player)
        return result

    @lru_cache(maxsize=6)
    def free_agents(self, position):
        """ Get free agents for a given position """
        agents = []
        for p in self.league.free_agents(week=None, size=1000, position=position):
            player = Player(p)
            player.projection = self._calc_score(player)
            agents.append(player)
        return agents
