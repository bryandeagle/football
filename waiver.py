from football import Football
from datetime import datetime
from jinja2 import Template
import os

THIS_DIR = os.path.dirname(os.path.realpath(__file__))


class Moves:
    def __init__(self):
        self.season_moves = list()
        self.weekly_moves = list()

    def sorted(self):
        return sorted(self.season_moves, key=lambda m: m.drop.playerId, reverse=True) + \
               sorted(self.weekly_moves, key=lambda m: m.drop.playerId, reverse=True)

    def add_season(self, movelist):
        self.season_moves += movelist

    def add_weekly(self, movelist):
        self.weekly_moves += movelist

    def render(self, league_id, year, team_id):
        t = Template(open(os.path.join(THIS_DIR, 'templates/waiver.html'), 'r',  encoding='utf-8').read())
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


def _waiver_moves(ranks, avail, position, to_drop):
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


def waiver(directory):
    # Initialize API and move list
    football = Football()
    moves = Moves()

    # Waiver RBs and WRs
    for pos in ['RB', 'WR']:
        available = football.get_espn_players(pos)
        rankings = football.get_fpros_rankings(pos, 'season')
        for player in football.get_espn_roster(pos):
            moves.add_season(_waiver_moves(rankings, available, pos, player))

    # Stream Players
    for pos in ['QB', 'TE', 'K', 'DST']:
        player = football.get_espn_roster(pos)[0]
        available = football.get_espn_players(pos)
        rankings = football.get_fpros_rankings(pos, 'week')
        moves.add_weekly(_waiver_moves(rankings, available, pos, player)[:football.league_size])

    # Render email
    rendered = moves.render(league_id=football.league_id,
                            year=datetime.today().year,
                            team_id=football.team_id)
    with open(os.path.join(directory, 'result.html'), 'wt', encoding='utf-8') as f:
        f.write(rendered)
    print('done')


if __name__ == '__main__':
    waiver(THIS_DIR)
