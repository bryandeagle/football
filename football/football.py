from logging import Formatter, getLogger, INFO, ERROR, StreamHandler
from functools import cached_property, lru_cache
from ff_espn_api import League
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import toml
import json
import sys
import os
import re


class Player:
    def __init__(self, espn_player, player_id, position):
        self.name = espn_player.name
        self.espn_id = espn_player.playerId
        self.ffn_id = 0
        self.position = re.compile('[^A-Z]').sub('', position)
        self.team = espn_player.proTeam
        self.projection = {'week': 0, 'season': 0}
        self.id = player_id
        if self.position == 'DT':
            raise ValueError(str(espn_player.__dict__))

    def __repr__(self):
        return self.name


class Football:
    def __init__(self, debug=False):
        self.config = self._read_config()
        self._week = self._get_week(self.config['general']['start_week'])
        self.league = League(league_id=self.config['general']['league_id'],
                             year=datetime.today().year,
                             espn_s2=self.secret['espn_s2'],
                             swid=self.secret['swid'])
        self._team_id = self._get_team_id(self.config['general']['owner'])
        self._level = INFO if debug else ERROR

    @cached_property
    def log(self):
        # Create handler
        _handler = StreamHandler(sys.stdout)
        _handler.setFormatter(Formatter(fmt='[%(levelname)s] %(message)s'))
        _handler.setLevel(self._level)

        # Creat log object
        log = getLogger(__name__)
        log.addHandler(_handler)
        log.setLevel(self._level)
        return log

    def _create_id(self, name, position, team):

        # Remove Jr, II, II, IV, etc from name
        name = re.sub(r'(IX|IV|V?I{0,3})$|(Jr\.?)$|(D/?ST)$', '', name)

        # Remove non alphanumeric characters from player ID
        name = re.compile(r'[^a-zA-Z0-9\s]').sub('', name).strip()
        position = re.compile(r'[^a-zA-Z]').sub('', position)
        team = re.compile(r'[^a-zA-Z]').sub('', team).lower()

        # Came from FantasyPros and needs to be looked up
        if len(team) <= 1 and position.lower() == 'dst':
            look_up = name.replace(' ', '')
            return self.config['custom_ids'][look_up]

        # Fix team discrepancies
        teams = {'jac': 'jax', 'lv': 'oak', 'was': 'wsh'}
        if team in teams:
            team = teams[team]

        # Shorten players to first-initial last-name
        if position.lower() != 'dst':
            split = [n.capitalize() for n in name.split()]
            name = split[0][0] + split[-1]

        # Format ID as Team + Position + Name
        return '{}{}{}'.format(team.capitalize(),
                               position.capitalize(),
                               name)

    def _get_team_id(self, owner):
        """ Get the team ID given the owner """
        for team in self.league.standings():
            if team.owner == owner:
                return team.team_id

    @staticmethod
    def _get_week(week_one):
        """ Get the NFL week number given the first week """
        week_dt = datetime.strptime(week_one, '%Y-%m-%d')
        return int(datetime.today().strftime('%W')) \
            - int(week_dt.strftime('%W')) + 1

    @staticmethod
    def _read_config():
        """ Read the configuration TOML file """
        this_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(this_dir, 'config.toml')) as f:
            return toml.loads(f.read())

    @cached_property
    def secret(self):
        """ Get the secrets from JSON file """
        if not os.path.isfile('secrets.json'):
            raise ValueError('Secrets file missing')
        with open('secrets.json', 'rt') as f:
            return json.loads(f.read())

    @lru_cache(maxsize=12)
    def _stats(self, position, time):
        week = 'draft' if time == 'season' else self._week
        url = 'https://www.fantasypros.com/nfl/projections'
        page = requests.get('{}/{}.php?week={}'
                            .format(url, position.lower(), week))
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find('table', id='data').find('tbody')
        stats = dict()
        for row in table.findAll('tr'):
            # Get player information
            columns = row.find_all('td')
            name = columns[0].find('a', {'class': 'player-name'}).text
            team = columns[0].find_all(text=True)[1]
            # Loop through stats cells
            stat = dict()
            for i, cell in enumerate(columns[1:-1]):
                col = self.config['fantasy_pros'][position][i]
                if col != '':
                    stat[col] = float(cell.contents[0].replace(',', ''))
            player_id = self._create_id(name, position, team)
            stats[player_id] = stat
        return stats

    def _calc_score(self, player):
        """ Calculates a players projected weekly and season scores """
        scores = dict()
        for time in ['week', 'season']:
            if player.id in self._stats(player.position, time):
                score = 0
                stats = self._stats(player.position, time)[player.id]
                for item in stats:
                    if item in self.config['espn_scoring']:
                        score += stats[item] * \
                                 self.config['espn_scoring'][item]
                    elif item in ['points_allowed', 'yards_allowed']:
                        for v in self.config[item]:
                            if stats[item] < int(v):
                                score += self.config[item][v]
                                break
                    else:
                        raise ValueError('Unknown stat {}'.format(item))
                scores[time] = score
            else:
                self.log.warning('{} not found in Fantasy Pros {}'
                                 .format(player.id, time))
                scores[time] = 0
        return scores

    @cached_property
    def roster(self):
        """ Get the team roster """
        result = {'QB': [], 'RB': [], 'WR': [], 'TE': [], 'K': [], 'DST': []}
        for p in self.league.get_team_data(self._team_id).roster:
            player_id = self._create_id(p.name, p.position, p.proTeam)
            player = Player(p, player_id, p.position)
            player.projection = self._calc_score(player)
            result[player.position].append(player)
        return result

    @lru_cache(maxsize=6)
    def free_agents(self, position):
        """ Get free agents for a given position """
        position = 'D/ST' if position == 'DST' else position
        agents = []
        for p in self.league.free_agents(week=None,
                                         size=1000,
                                         position=position):
            player_id = self._create_id(p.name, p.position, p.proTeam)
            player = Player(p, player_id, position)
            if player.team != 'None':
                player.projection = self._calc_score(player)
                agents.append(player)
        return agents
