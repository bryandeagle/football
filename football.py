from ff_espn_api import League
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import toml
import os
import re


def _create_id(name, team, position, custom_ids=None):
    if custom_ids and name.replace(' ', '_') in custom_ids:
        return custom_ids[name.replace(' ', '_')]
    name = re.sub(r'(\sI{2,})|(Jr\.?)|(D/?ST)$', '', name)
    pid = '{}{}{}'.format(team.lower(), position.lower(), name.lower())
    return re.compile('[^a-z]').sub('', pid)


class Player:
    def __init__(self, espn_player):
        self.name = espn_player.name
        self.espn_id = espn_player.playerId
        self.position = re.compile('[^A-Z]').sub('', espn_player.position)
        self.team = espn_player.proTeam
        self.projection = {'week': 0, 'season': 0}
        self.id = _create_id(self.name, self.team, self.position)

    def __repr__(self):
        return self.name


class Football:
    def __init__(self):
        # Read config.toml file
        this_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(this_dir, 'config.toml')) as f:
            self.config = toml.loads(f.read())

        # Get required ESPN environment variables
        swid, espn_s2 = os.getenv('SWID'), os.getenv('ESPN_S2')
        if not swid:
            raise ValueError('SWID environment variable not set')
        elif not espn_s2:
            raise ValueError('ESPN_S2 environment variable not set')

        # Get the current week number
        week_one = datetime.strptime(self.config['general']['start_week'], '%Y-%m-%d')
        self._week = int(datetime.today().strftime('%W')) - int(week_one.strftime('%W')) + 1

        # Initiatlize ESPN league API
        self.league = League(league_id=self.config['general']['league_id'],
                             year=datetime.today().year,
                             espn_s2=espn_s2,
                             swid=swid)
        # Get my team ID
        for team in self.league.standings():
            if team.owner == self.config['general']['owner']:
                self._team_id = team.team_id
                break

        # Get stats from fantasy pros
        self.stats = {'week': {}, 'season': {}}
        for time in ['week', 'season']:
            for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']:
                self.stats[time] = {**self.stats[time], **self.get_stats(pos, self._week)}

        # Calculate projections from ESPN settings
        self.projections = {'week': {}, 'season': {}}
        for time in ['week', 'season']:
            for player in self.stats[time]:
                self.projections[time][player] = self.calc_score(player, time)

        # Get team roster
        self.roster = {'QB': [], 'RB': [], 'WR': [], 'TE': [], 'K': [], 'DST': []}
        for p in self.league.get_team_data(self._team_id).roster:
            player = Player(p)
            player.projection['week'] = self.calc_score(player.id, 'week')
            player.projection['season'] = self.calc_score(player.id, 'season')
            self.roster[player.position].append(player)

    def get_stats(self, position, week):
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
                    stat[col] = float(cell.contents[0])
            stats[_create_id(name, team, position, self.config['custom_ids'])] = stat
        return stats

    def calc_score(self, player, time):
        if player not in self.stats[time]:
            raise ValueError('Unknown Player: {}'.format(player))
        score = 0
        for item in self.stats[time][player]:
            if item in self.config['espn_scoring']:
                score += self.stats[time][player][item] * self.config['espn_scoring'][item]
            elif item in ['points_allowed', 'yards_allowed']:
                for v in self.config[item]:
                    if self.stats[time][player][item] < int(v):
                        score += self.config[item][v]
                        break
            else:
                raise ValueError('Unknown stat: {}'.format(item))
        return score

    def free_agents(self, position):
        agents = []
        for p in self.league.free_agents(week=None, size=1000, position=position):
            player = Player(p)
            player.projection['week'] = self.calc_score(player.id, 'week')
            player.projection['season'] = self.calc_score(player.id, 'season')
            agents.append(player)
        return agents
