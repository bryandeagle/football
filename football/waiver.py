from football import Football


def pretty_print(moves):
    """ Prints the bench in a nice fancy way """
    dmax, amax = 0, 0
    for m in moves:  # Get max name lengths
        if len(m['drop']['name']) > dmax:
            dmax = len(m['drop']['name'])
        m = max([len(p['name']) for p in m['add']])
        if m > amax:
            amax = m

    print('┌──────┬─{l:─^{n}}─┬─{l:─^{m}}─┬───────┐\n'
          '│ POS  │ {d: <{n}} │ {a: <{m}} | DELTA │\n'
          '├──────┼─{l:─^{n}}─┼─{l:─^{m}}─┼───────┤'
          .format(l='─', n=dmax, m=amax, d='DROP', a='ADD'))

    for m in moves:  # Print each move
        for a in m['add']:
            pts = '{:.2f}'.format(a['score'] - m['drop']['score'])
            print('│ {p:<4} │ {d:<{n}} │ {a:<{m}} │ {e} │'
                  .format(p=m['drop']['position'],
                          d=m['drop']['name'],
                          e=pts.zfill(5),
                          a=a['name'],
                          n=dmax,
                          m=amax))
    print('└──────┴─{l:─^{n}}─┴─{l:─^{m}}─┴───────┘'
          .format(l='─', n=dmax, m=amax))


if __name__ == '__main__':
    football = Football()

    for pos in football.slots.keys():
        fas = football.free_agents_by_pos(pos)
        team = football.roster_by_pos(pos, sort=True)
        lowest = team[football.slots[pos]-1]
        total = sorted(fas + team[:football.slots[pos]],
                       key=lambda x: x['score'],
                       reverse=True)
        better = [a for a in total if a['score'] >= lowest['score']]
        if len(better) > football.slots[pos]:
            max_len = max([len(p['name']) for p in better])
            print('┌──────┬────┬─{l:─^{n}}─┬───────┐\n'
                  '│ POS  │ FA │ {t: <{n}} │ PTS   │\n'
                  '├──────┼────┼─{l:─^{n}}─┼───────┤'
                  .format(l='─', n=max_len, t='TITLE'))
            for p in better:
                fa = 'N' if p in team else 'Y'
                pts = '{:.2f}'.format(p['score']).zfill(5)
                print('│ {:<4} │ {}  | {:<{}} │ {} │'
                      .format(p['position'], fa, p['name'], max_len, pts))
            print('└──────┴────┴─{:─^{}}─┴───────┘'.format('─', max_len))

    moves = list()
    for pos in football.slots.keys():
        fas = football.free_agents_by_pos(pos, sort=True)
        team = football.roster_by_pos(pos, sort=True)
        for p in team[:football.slots[pos]]:
            better = [fa for fa in fas if fa['score'] > p['score']]
            if better:
                moves.append({'drop': team.pop(), 'add': better})
                fas.pop(0)
    print('\n  MOVES TO MAKE:')
    pretty_print(moves)
