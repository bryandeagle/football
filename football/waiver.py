from ffn import Football


class Team:
    def __init__(self, qb, rb, wr, te, k, dst):
        self.roster = {'QB': qb, 'TE': te,
                       'RB': rb, 'WR': wr,
                       'K': k, 'DST': dst}

        # Validate slots can be filled
        self.structure = {'QB': 2, 'RB': 5, 'WR': 5,
                          'TE': 2, 'DST': 1, 'K': 1}

        # Put kicker and DST into slots
        self.slots = {'DST': dst, 'K': k}

        # Put Running Backs into slots
        self.slots['RB'] = self.sort(rb)[:self.structure['RB']]
        self.slots['WR'] = self.sort(wr)[:self.structure['WR']]
        self.slots['QB'] = self.sort(qb)[:self.structure['QB']]
        self.slots['TE'] = self.sort(te)[:self.structure['TE']]

    @staticmethod
    def sort(players):
        return sorted(players, key=lambda p: p['seasonScore'], reverse=True)

    def __repr__(self):
        max_len = 0  # Loop through players to get max length
        for pos in ['QB', 'RB', 'WR', 'TE', 'DST', 'K']:
            for player in self.slots[pos]:
                if len(player['name']) > max_len:
                    max_len = len(player['name'])

        string = '┌──────┬─' + '─' * max_len + '─┬────────┬───────┐' \
                 '\n│ POS  │ {:<{}} │ SEASON │ WEEK  │\n├──────' \
                 '┼──'.format('NAME', max_len) + '─' * max_len + '┼────' \
                 '────┼───────┤\n'
        for pos in ['QB', 'RB', 'WR', 'TE', 'DST']:
            for player in self.slots[pos]:
                week = '{:.2f}'.format(player['weekScore']).zfill(5)
                season = '{:.2f}'.format(player['seasonScore']).zfill(6)
                string += '│ {:<4} │ {:<{}} │ {} │ {} │\n'\
                    .format(pos, player['name'], max_len, season, week)
            string += '├──────┼──' + '─' * \
                      max_len + '┼────────┼───────┤\n'
        week = '{:.2f}'.format(self.slots['K'][0]['weekScore'])
        season = '{:.2f}'.format(self.slots['K'][0]['seasonScore'])
        string += '│ K    │ {:<{}} │ {} | {} |\n' \
                  .format(self.slots['K'][0]['name'], max_len,
                          season.zfill(6), week.zfill(5))
        return string + '└──────┴─' + '─' * max_len + \
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
    team = Team(qb=football.roster_by_pos('QB'),
                rb=football.roster_by_pos('RB'),
                wr=football.roster_by_pos('WR'),
                te=football.roster_by_pos('TE'),
                k=football.roster_by_pos('K'),
                dst=football.roster_by_pos('DST'))

    print(team)
    quit()

    # Get season moves
    for pos in ['WR', 'RB', 'TE', 'QB', 'DST', 'K']:
        free_agents = football.free_agents(pos)
        for player in team.slots[pos]:
            better = [p for p in free_agents
                      if p['seasonScore'] >
                      player['seasonScore']]
            if better:
                print('{}:{}'.format(player, better))
