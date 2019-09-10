from football import Football, Email
from datetime import datetime
from jinja2 import Template
import yaml

CONFIG_FILE = 'config.yaml'


class Moves:
    def __init__(self):
        self.season_moves = list()
        self.weekly_moves = list()

    def sorted(self):
        return sorted(self.season_moves, key=lambda m: m.delta, reverse=True) + \
               sorted(self.weekly_moves, key=lambda m: m.delta, reverse=True)

    def add_season(self, movelist):
        self.season_moves += movelist

    def add_weekly(self, movelist):
        self.weekly_moves += movelist

    def render(self, league_id, year, team_id):
        t = Template(open('templates/waiver.html', 'r',  encoding='utf-8').read())
        return t.render(moves=self.sorted(), league_id=league_id, year=year, team_id=team_id)

    def __repr__(self):
        return '\n'.join([str(m) for m in self.sorted()])


class Move:
    def __init__(self, position, drop, add, delta):
        self.position = position
        self.drop = drop
        self.add = add
        self.delta = delta

    def __repr__(self):
        return 'Drop {} {} for {} for +{} rank.'.format(self.position,
                                                        self.drop,
                                                        self.add,
                                                        self.delta)


def waiver(ranks, avail, position, to_drop):
    """ Returns list of moves for players better than given """
    if to_drop.name in ranks:
        current_rank = ranks.index(to_drop.name)
    else:
        current_rank = 200
    avail_names = [p.name for p in avail]
    drops = list()
    for rank, add in enumerate(ranks[:current_rank]):
        if add in avail_names:
            add_player = avail[avail_names.index(add)]
            drops.append(Move(drop=to_drop, add=add_player,
                              position=position, delta=current_rank - rank))
    return drops


if __name__ == '__main__':
    # Initial configuration
    config = yaml.load(open(CONFIG_FILE, 'r'))
    mail = Email(config['email'])

    try:
        # Initialize API and move list
        football = Football(config['football'])
        moves = Moves()

        # Waiver RBs and WRs
        for pos in ['RB', 'WR']:
            available = football.get_espn_players(pos)
            rankings = football.get_fpros_rankings(pos, 'season')
            for player in football.get_espn_roster(pos):
                moves.add_season(waiver(rankings, available, pos, player))

        # Stream Players
        for pos in ['QB', 'TE', 'K', 'DST']:
            player = football.get_espn_roster(pos)[0]
            available = football.get_espn_players(pos)
            rankings = football.get_fpros_rankings(pos, 'week')
            moves.add_weekly(waiver(rankings, available, pos, player))

        # Send action email
        rendered = moves.render(league_id=config['football']['league_id'],
                                year=datetime.today().year,
                                team_id=config['football']['team_id'])
        mail.send(subject=config['waiver']['subject'], html=rendered)

    except Exception as e:
        # Send error email
        mail.send(subject='An Error Occurred', html=str(e))
        raise e
