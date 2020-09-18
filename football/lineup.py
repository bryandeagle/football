from ffn import Football


def print_lineup(line_up):
    """ Prints the lineup in a nice fancy way """
    max_len = 0  # Loop through players to get max length
    for pos in line_up:
        if len(line_up[pos]['name']) > max_len:
            max_len = len(line_up[pos]['name'])
    # Print fancy box containing line-up
    print('┌──────┬─' + '─' * max_len + '─┬───────┐')
    print('│ POS  │ {:<{}} │ PTS   │'.format('Player', max_len))
    print('├──────┼─' + '─' * max_len + '─┼───────┤')
    for pos in ['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'FLX', 'TE', 'K', 'DST']:
        pts = '{:.2f}'.format(line_up[pos]['weekScore']).zfill(5)
        print('│ {:<4} │ {:<{}} │ {} │'.format(pos,
                                               line_up[pos]['name'],
                                               max_len,
                                               pts))
    print('└──────┴─' + '─' * max_len + '─┴───────┘')


if __name__ == '__main__':

    # Initialize API and roster with trivial positions
    football = Football()
    lineup = {'K': football.roster_by_pos('K')[0],
              'DST': football.roster_by_pos('DST')[0]}

    # Fill in QB and TE positions
    qbs = sorted(football.roster_by_pos('QB'), key=lambda p: p['weekScore'])
    tes = sorted(football.roster_by_pos('TE'), key=lambda p: p['weekScore'])
    lineup['QB'], lineup['TE'] = qbs.pop(), tes.pop()

    # Fill in RB and WR positions
    rbs = sorted(football.roster_by_pos('RB'), key=lambda p: p['weekScore'])
    wrs = sorted(football.roster_by_pos('WR'), key=lambda p: p['weekScore'])
    lineup['RB1'], lineup['RB2'] = rbs.pop(), rbs.pop()
    lineup['WR1'], lineup['WR2'] = wrs.pop(), wrs.pop()

    # Set flex position to WR or RB
    flx_rb, flx_wr = rbs.pop(), wrs.pop()
    if flx_rb['weekScore'] > flx_wr['weekScore']:
        lineup['FLX'] = flx_rb
    else:
        lineup['FLX'] = flx_wr

    print_lineup(lineup)
