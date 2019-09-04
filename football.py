from ff_espn_api import League
from datetime import datetime
from fantasy import Fantasy
import yaml

CONFIG_FILE = 'config.yaml'


def sanitize(name):
    return name.replace('.', '').lower().strip()


def fix_pos(position):
    if position == 'DST':
        return 'D/ST'
    else:
        return position


class Football:
    def __init__(self, config_file):
        # Load configuration file
        config = yaml.load(open(config_file, 'r'))

        # Initialize league
        self.team_id = config['team_id']
        self.league = League(league_id=config['league_id'],
                             year=datetime.today().year,
                             espn_s2=config['espn_s2'],
                             swid=config['swid'])

    def get_roster(self, position):
        players = self.league.get_team_data(self.team_id).roster
        if position == 'DST':
            return [p.name.replace(' D/ST', '') for p in players if p.position == 'D/ST']
        else:
            return [p.name for p in players if p.position == position]

    def available_players(self, position):
        if position == 'DST':
            return [x.name.replace(' D/ST', '') for x in self.league.free_agents(week=None, size=1000, position='D/ST')]
        else:
            return [x.name for x in self.league.free_agents(week=None, size=1000, position=position)]


if __name__ == '__main__':

    # Initialize APIs
    espn = Football(CONFIG_FILE)
    pros = Fantasy()

    # Initialize moves
    moves = list()

    # Stream Players
    for position in ['QB', 'TE', 'K', 'DST']:

        # Get available players
        available = espn.available_players(position)
        sanitized_available = [sanitize(p) for p in available]

        # Get week rankings
        week_rankings = pros.week_rankings(position)
        sanitized_rankings = [sanitize(p) for p in week_rankings]

        # Get current player
        current = espn.get_roster(position)[0]
        current_rank = sanitized_rankings.index(sanitize(current))

        for rank, player in enumerate(week_rankings):
            if rank >= current_rank:
                break
            if sanitize(player) in sanitized_available:
                moves.append({'position': position, 'drop': current, 'pickup': player})
                break

    for move in moves:
        print('For {} drop {} for {}'.format(move['position'], move['drop'], move['pickup']))
