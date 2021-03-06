from football import Football


def pretty_print(players, max_len, title):
    """ Prints the bench in a nice fancy way """
    print('┌──────┬─{l:─^{n}}─┬───────┐\n'
          '│ POS  │ {t: <{n}} │ PTS   │\n'
          '├──────┼─{l:─^{n}}─┼───────┤'
          .format(l='─', n=max_len, t=title))
    for player in players:
        pts = '{:.2f}'.format(player['score']).zfill(5)
        print('│ {:<4} │ {:<{}} │ {} │'
              .format(player['position'], player['name'], max_len, pts))
    print('└──────┴─{:─^{}}─┴───────┘'.format('─', max_len))


if __name__ == '__main__':
    # Initialize API and bench and line-up
    football, lineup, bench = Football(), list(), list()

    # Go through each position picking line-up
    for pos in football.slots.keys():
        team = football.roster_by_pos(pos, sort=True)
        lineup += team[0:football.slots[pos]]
        bench += team[football.slots[pos]:]

    # Print line-up and bench
    max_len = max([len(p['name']) for p in football.roster])
    pretty_print(lineup, max_len, 'LINE-UP')
    pretty_print(bench, max_len, 'BENCH')
