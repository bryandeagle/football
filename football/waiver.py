from football import Football


class Team:
    def __init__(self, roster):
        self.roster = roster

        # Validate slots can be filled
        self._slots = {'QB': (1, 1), 'RB': (1, 4), 'WR': (1, 4),
                       'TE': (1, 1), 'DST': (1, 0), 'K': (1, 0)}
        self._validate()

        # Put kicker and DST into slots
        self.week = {'DST': roster['DST'], 'K': roster['K']}
        self.season = {'DST': [], 'K': []}

        # Put Running Backs into slots
        for pos in ['RB', 'WR', 'QB', 'TE']:
            players = sorted(self.roster[pos],
                             key=lambda p: p.projection['season'],
                             reverse=True)
            self.season[pos] = players[:self._slots[pos][1]]
            self.week[pos] = players[self._slots[pos][1]:]

    def _validate(self):
        for position in self.roster.keys():
            found = len(self.roster[position])
            need = sum(self._slots[position])
            if found != need:
                raise ValueError('Found {} {}(s). Need {}.'
                                 .format(found, position, need))

    def __repr__(self):
        max_len = 0  # Loop through players to get max length
        for pos in ['QB', 'RB', 'WR', 'TE', 'DST', 'K']:
            for player in self.season[pos] + self.week[pos]:
                if len(player.name) > max_len:
                    max_len = len(player.name)

        string = '┌──────┬────────┬─' + '─' * max_len + '─┬────────┬───────┐' \
                 '\n│ POS  │ SLOT   │ {:<{}} │ SEASON │ WEEK  │\n├──────┼───' \
                 '─────┼──'.format('NAME', max_len) + '─' * max_len + '┼────' \
                 '────┼───────┤\n'
        for pos in ['QB', 'RB', 'WR', 'TE', 'DST']:
            for player in self.season[pos]:
                week = '{:.2f}'.format(player.projection['week']).zfill(5)
                season = '{:.2f}'.format(player.projection['season'])
                string += '│ {:<4} │ Season │ {:<{}} │ {} │ {} │\n'\
                    .format(pos, player.name, max_len, season.zfill(6), week)
            for player in self.week[pos]:
                week = '{:.2f}'.format(player.projection['week']).zfill(5)
                season = '{:.2f}'.format(player.projection['season'])
                string += '│ {:<4} │ Week   │ {:<{}} │ {} │ {} │\n'\
                    .format(pos, player.name, max_len, season.zfill(6), week)
            string += '├──────┼────────┼──' + '─' * \
                      max_len + '┼────────┼───────┤\n'
        week = '{:.2f}'.format(self.week['K'][0].projection['week'])
        season = '{:.2f}'.format(self.week['K'][0].projection['season'])
        string += '│ K    │ Week   │ {:<{}} │ {} | {} |\n' \
                  .format(self.week['K'][0].name, max_len,
                          season.zfill(6), week.zfill(5))
        return string + '└──────┴────────┴─' + '─' * max_len + \
            '─┴────────┴───────┘\n'


class Move:
    def __init__(self, position, drop, add, delta):
        self.position = position
        self.drop = drop
        self.add = add
        self.delta = delta

    def __repr__(self):
        return 'Drop {} {} for {} for +{} pts.'\
            .format(self.position, self.drop, self.add, self.delta)


if __name__ == '__main__':
    football = Football(debug=False)
    team = Team(football.roster)
    print(team)
    
    # Get season moves
    for pos in ['WR', 'RB', 'TE', 'QB', 'DST', 'K']:
        free_agents = football.free_agents(pos)
        for player in team.season[pos]:
            better = [p for p in free_agents
                      if p.projection['season'] >
                      player.projection['season']]
            if better:
                bp = [(p.name, p.projection['season']) for p in better]
                print('Season:{} ({}):{}'.format(player, player.projection['season'], bp))

    # Get weekly moves
    for pos in ['WR', 'RB', 'TE', 'QB', 'DST', 'K']:
        free_agents = football.free_agents(pos)
        for player in team.week[pos]:
            better = [p for p in free_agents
                      if p.projection['week'] >
                      player.projection['week']]
            if better:
                print('Week:{}:{}'.format(player, better))
