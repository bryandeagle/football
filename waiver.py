from football import Football

CONFIG_FILE = 'config.yaml'


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

    # Initialize API and move list
    football = Football(CONFIG_FILE)
    season_moves, weekly_moves = list(), list()

    # Waiver RBs and WRs
    for pos in ['RB', 'WR']:
        available = football.get_espn_players(pos)
        rankings = football.get_fpros_rankings(pos, 'season')
        for player in football.get_espn_roster(pos):
            season_moves += waiver(rankings, available, pos, player)

    # Stream Players
    for pos in ['QB', 'TE', 'K', 'DST']:
        player = football.get_espn_roster(pos)[0]
        available = football.get_espn_players(pos)
        rankings = football.get_fpros_rankings(pos, 'week')
        weekly_moves += waiver(rankings, available, pos, player)

    # Print resulting moves
    season_moves_sorted = sorted(season_moves, key=lambda m: m.delta)
    weekly_moves_sorted = sorted(weekly_moves, key=lambda m: m.delta)
    [print(m) for m in season_moves_sorted + weekly_moves_sorted]
