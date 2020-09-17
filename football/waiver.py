from football import Football


class Team:
    def __init__(self, roster):
        self.roster = roster

        # Capture team slots. Format: (week, season)
        self.slots = {'QB': (1, 1), 'RB': (1, 4), 'WR': (1, 4),
                      'TE': (1, 1), 'DST': (1, 0), 'K': (1, 0)}

        # Validate slots can be filled
        self._validate()

        # Put kicker and DST into slots
        self.week = {'DST': roster['DST'], 'K': roster['K']}
        self.season = {'DST': [], 'K': []}

        # Put Running Backs into slots
        for pos in ['RB', 'WR', 'QB', 'TE']:
            players = sorted(self.roster[pos],
                             key=lambda p: p.projection['season'],
                             reverse=True)
            self.season[pos] = players[:self.slots[pos][1]]
            self.week[pos] = players[self.slots[pos][1]:]

    def _validate(self):
        for position in self.roster.keys():
            found = len(self.roster[position])
            need = sum(self.slots[position])
            if found != need:
                raise ValueError('Found {} {}(s). Need {}.'
                                 .format(found, position, need))

    def __repr__(self):
        max_len = 0  # Loop through players to get max length
        for pos in ['QB', 'RB', 'WR', 'TE', 'DST', 'K']:
            for player in self.season[pos] + self.week[pos]:
                if len(player.name) > max_len:
                    max_len = len(player.name)

        string = '┌──────┬────────┬─' + '─' * max_len + '─┬────────┬───────┐\n' \
                 '│ POS  │ SLOT   │ {:<{}} │ SEASON │ WEEK  │\n'.format('NAME', max_len)
        string += '├──────┼────────┼──' + '─' * max_len + '┼────────┼───────┤\n'
        for pos in ['QB', 'RB', 'WR', 'TE', 'DST']:
            for player in self.season[pos]:
                week = '{:.2f}'.format(player.projection['week'])
                season = '{:.2f}'.format(player.projection['season'])
                string += '│ {:<4} │ Season │ {:<{}} │ {} │ {} │\n'\
                    .format(pos, player.name, max_len, season.zfill(6), week.zfill(5))
            for player in self.week[pos]:
                week = '{:.2f}'.format(player.projection['week'])
                season = '{:.2f}'.format(player.projection['season'])
                string += '│ {:<4} │ Week   │ {:<{}} │ {} │ {} │\n'\
                    .format(pos, player.name, max_len, season.zfill(6), week.zfill(5))
            string += '├──────┼────────┼──' + '─' * max_len + '┼────────┼───────┤\n'
        week = '{:.2f}'.format(self.week['K'][0].projection['week']).zfill(5)
        season = '{:.2f}'.format(self.week['K'][0].projection['season']).zfill(6)
        string += '│ K    │ Week   │ {:<{}} │ {} | {} |\n'.format(self.week['K'][0].name, max_len, season, week)
        return string + '└──────┴────────┴─' + '─' * max_len + '─┴────────┴───────┘\n'


class Move:
    def __init__(self, position, drop, add, delta):
        self.position = position
        self.drop = drop
        self.add = add
        self.delta = delta

    def __repr__(self):
        return 'Drop {} {} for {} for +{} pts.'\
            .format(self.position, self.drop, self.add, self.delta)


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


if __name__ == '__main__':
    football = Football()
    team = Team(football.roster)
    free_agents = football.free_agents('DST')

    #for time in team.season:
    #    for pos in ['WR', 'RB', 'QB', 'TE', 'DST', 'K']:
    #        free_agents = football.free_agents(pos)
    #        for player in team.season[pos]:
    #            fa_better = [p for p in free_agents if p.projection[time] > player.projection[time]]
    #            print('{}:{}'.format(player, fa_better))
