from football import Football


def print_lineup(line_up):
    """ Prints the lineup in a nice fancy way """
    max_len = 0  # Loop through players to get max length
    for pos in line_up:
        if len(line_up[pos].name) > max_len:
            max_len = len(line_up[pos].name)
    # Print fancy box containing line-up
    print('┌──────┬─' + '─' * max_len + '─┬───────┐')
    print('│ POS  │ {:<{}} │ PTS   │'.format('Player', max_len))
    print('├──────┼─' + '─' * max_len + '─┼───────┤')
    for pos in ['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'FLX', 'TE', 'K', 'DST']:
        pts = '{:.2f}'.format(line_up[pos].projection['week']).zfill(5)
        print('│ {:<4} │ {:<{}} │ {} │'.format(pos,
                                               line_up[pos].name,
                                               max_len,
                                               pts))
    print('└──────┴─' + '─' * max_len + '─┴───────┘')


if __name__ == '__main__':

    # Initialize API and roster with trivial positions
    football = Football()
    lineup = {'K': football.roster['K'][0],
              'DST': football.roster['DST'][0]}

    # Fill in QB and TE positions
    qbs = sorted(football.roster['QB'], key=lambda p: p.projection['week'])
    tes = sorted(football.roster['TE'], key=lambda p: p.projection['week'])
    lineup['QB'], lineup['TE'] = qbs.pop(), tes.pop()

    # Fill in RB and WR positions
    rbs = sorted(football.roster['RB'], key=lambda p: p.projection['week'])
    wrs = sorted(football.roster['WR'], key=lambda p: p.projection['week'])
    lineup['RB1'], lineup['RB2'] = rbs.pop(), rbs.pop()
    lineup['WR1'], lineup['WR2'] = wrs.pop(), wrs.pop()

    # Set flex position to WR or RB
    flx_rb, flx_wr = rbs.pop(), wrs.pop()
    if flx_rb.projection['week'] > flx_wr.projection['week']:
        lineup['FLX'] = flx_rb
    else:
        lineup['FLX'] = flx_wr

    print_lineup(lineup)
