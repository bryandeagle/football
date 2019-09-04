from football import Football, Email
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

    def render(self):
        t = Template(open('templates/waiver.html', 'r',  encoding='utf-8').read())
        return t.render(moves=self.sorted())

    def __repr__(self):
        return '\n'.join([str(m) for m in self.sorted()])


class Move:
    def __init__(self, position, drop, pickup, delta):
        self.position = position
        self.drop = drop
        self.pickup = pickup
        self.delta = delta

    def __repr__(self):
        return 'Drop {} {} for {} for +{} rank.'.format(self.position,
                                                        self.drop,
                                                        self.pickup,
                                                        self.delta)


def waiver(ranks, avail, position, to_drop):
    """ Returns list of moves for players better than given """
    current_rank = ranks.index(to_drop)
    drops = list()
    for rank, pickup in enumerate(ranks[:current_rank]):
        if pickup in avail:
            drops.append(Move(drop=to_drop, pickup=pickup,
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

        # Send email
        mail.send(subject=config['waiver']['subject'], html=moves.render())

    except Exception as e:
        # Send error email
        mail.send(subject='An Error Occurred', html=str(e))


