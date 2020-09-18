from logging import Formatter, getLogger, INFO, ERROR, StreamHandler
from functools import cached_property
from ff_espn_api import League
from datetime import datetime
import requests
import json
import toml
import sys
import os
import re


class Football:
    def __init__(self, debug=False):
        self.level = INFO if debug else ERROR
        self.league_id = 1752514
        self.owner = 'Bryan Deagle'
        self.start_week = '2020-09-07'
        self.total_weeks = 13 + 2
        self.discount = 0.9

    @cached_property
    def log(self):
        # Create handler
        _handler = StreamHandler(sys.stdout)
        _handler.setFormatter(Formatter(fmt='[%(levelname)s] %(message)s'))
        _handler.setLevel(self.level)

        # Creat log object
        log = getLogger(__name__)
        log.addHandler(_handler)
        log.setLevel(self.level)
        return log

    def roster_by_pos(self, position):
        """ Return team roster by position """
        return [p for p in self.roster if p['position'] == position]

    @cached_property
    def week(self):
        """ Get the NFL week number given the first week """
        week_dt = datetime.strptime(self.start_week, '%Y-%m-%d')
        return int(datetime.today().strftime('%W')) \
            - int(week_dt.strftime('%W')) + 1

    @cached_property
    def espn_team(self):
        """ Get the ESPN team ID """
        for team in self.espn.standings():
            if team.owner == self.owner:
                return team.team_id

    @cached_property
    def espn(self):
        """ The ESPN league object """
        return League(league_id=self.league_id,
                      year=datetime.today().year,
                      espn_s2=self.secret['espn_s2'],
                      swid=self.secret['swid'])

    @cached_property
    def secret(self):
        """ Get the secrets from JSON file """
        if not os.path.isfile('secrets.json'):
            raise ValueError('Secrets file missing')
        with open('secrets.json', 'rt') as f:
            return json.loads(f.read())

    @cached_property
    def roster(self):
        """ Current team roster """
        espn_players = self.espn.get_team_data(self.espn_team).roster
        return list(map(self.espn_to_dict, espn_players))

    @cached_property
    def free_agents(self):
        """ Free Agents """
        agents = self.espn.free_agents(size=0)
        on_teams = [p for p in agents if p.proTeam != "None"]
        dict_list = map(self.espn_to_dict, on_teams)
        return [p for p in dict_list if p]

    def score(self, stats):
        """ Calculate score given stats """
        def dpa(x):
            """ Defense points allowed """
            maps = [(1, 5), (7, 4), (14, 3),
                    (18, 1), (28, 0), (35, -1),
                    (46, -3), (200, -7)]
            for v, s in maps:
                if x < v:
                    return s

        def dya(x):
            """ Defense yards allowed """
            maps = [(100, 5), (200, 3), (300, 2),
                    (350, 0), (400, -1), (450, -3),
                    (500, -5), (550, -6), (1000, -7)]
            for v, s in maps:
                if x < v:
                    return s

        settings = {'passYds': 0.04, 'passTD': 4, 'passInt': -2,
                    'rushYds': 0.1, 'rushTD': 6, 'fumblesLost': -2,
                    'receptions': 1, 'recYds': 0.1, 'recTD': 6,
                    'defInt': 2, 'defFR': 2, 'defSack': 1,
                    'defTD': 6, 'defRetTD': 6, 'defSafety': 2,
                    'defPA': dpa, 'defYdsAllowed': dya,
                    'fg': 4, 'xp': 1}

        s = 0
        for stat in settings:
            if callable(settings[stat]):
                if stats['position'] == 'DEF':
                    s += settings[stat](float(stats[stat]))
            else:
                s += float(stats[stat]) * settings[stat]
        return s

    @cached_property
    def projections(self):
        """ Get projections dictionary """
        proj = dict()
        for p in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            tab = self.nerd('weekly-projections', p, self.week)['Projections']
            for row in tab:
                proj[int(row['playerId'])] = {'week': self.score(row),
                                              'ros': self.score(row)}
            for w in range(self.week + 1, self.total_weeks + 1):
                table = self.nerd('weekly-projections', p, w)['Projections']
                for row in table:
                    mul = self.discount ** (w - self.week)
                    proj[int(row['playerId'])]['ros'] += self.score(row) * mul
        return proj

    def espn_to_dict(self, player):
        """ Convert ESPN Player object to dictionary """
        position = player.position.replace('/', '')
        global_id = self.get_id(player.name,
                                position,
                                player.proTeam)
        nerd_id = self.get_nerd_id(global_id)
        if nerd_id in self.projections:
            return {'name': player.name,
                    'position': position,
                    'team': player.proTeam,
                    'espnId': player.playerId,
                    'nerdId': nerd_id,
                    'weekScore': self.projections[nerd_id]['week'],
                    'seasonScore': self.projections[nerd_id]['ros'],
                    'globalId': global_id}

    @cached_property
    def nerd_players(self):
        """ Returns all Nerd Players """
        players = dict()
        for player in self.nerd('players')['Players']:
            global_id = self.get_id(player['displayName'],
                                    player['position'],
                                    player['team'])
            players[global_id] = int(player['playerId'])
        return players

    def nerd(self, service, *kwargs):
        """ Wrap up common calls for all Nerd APIs """
        base = 'https://www.fantasyfootballnerd.com/service'
        args = '/'.join([str(a) for a in kwargs])
        url = '{}/{}/json/{}/{}'.format(base, service,
                                        self.secret['nerd_api_key'],
                                        args)
        self.log.info('GET: {}'.format(url))
        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.content)

    @staticmethod
    def get_id(name, position, team):
        """ Creates unique ID for a player for look-up purposes """
        position = 'DST' if position == 'DEF' else position
        team_swaps = {'WSH': 'WAS', 'JAX': 'JAC', 'LV': 'OAK'}
        if team in team_swaps:
            team = team_swaps[team]
        # Remove Jr, II, II, IV, etc from name
        name = re.sub(r'(IX|IV|V?I{0,3})$|(Sr\.?)|(Jr\.?)$|(D/?ST)$', '', name)
        # Remove non alphanumeric characters
        name = re.compile(r'[^a-zA-Z0-9\s]').sub('', name).strip()
        position = re.compile(r'[^a-zA-Z]').sub('', position)
        team = re.compile(r'[^a-zA-Z]').sub('', team).lower()
        # Shorten players to first-initial last-name
        split = [n.capitalize() for n in name.split()]
        if position != 'DST':
            name = split[0][0] + split[-1]
        else:
            name = ''
        # Format ID as Team + Position + Name
        return '{}{}{}'.format(team.capitalize(),
                               position.capitalize(),
                               name)

    def get_nerd_id(self, global_id):
        """ Get Nerd ID based on Global ID """
        if global_id in self.nerd_players:
            return self.nerd_players[str(global_id)]
        else:
            self.log.warning('{} not found in Nerd'.format(global_id))


if __name__ == '__main__':
    f = Football(debug=True)
    print(f.roster[0])
