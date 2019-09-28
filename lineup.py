from football import Football
from jinja2 import Template
import os

THIS_DIR = os.path.dirname(os.path.realpath(__file__))


class Lineup:
    def __init__(self):
        self.QB = None
        self.RB1 = None
        self.RB2 = None
        self.WR1 = None
        self.WR2 = None
        self.FLX = None
        self.TE = None
        self.K = None
        self.DST = None

    def render(self, team_id, league_id):
        """ Renders the appropriate Jinja2 template for HTML email """
        t = Template(open(os.path.join(THIS_DIR, 'templates/lineup.html'), 'r').read())
        return t.render(lineup=self, team_id=team_id, league_id=league_id)

    def __repr__(self):
        """ Prints line-up for debugging purposes """
        return 'Optimal Line-Up:\n  RB1: {}\n  RB2: {}\n  WR1: {}\n' \
               '  WR2: {}\n  FlX: {}\n  TE:  {}\n  K:   {}\n  DST: {}'\
            .format(self.RB1, self.RB2, self.WR1, self.WR2, self.FLX,
                    self.TE, self.K, self.DST)


def lineup(directory):
    # Initialize API
    football = Football()
    line_up = Lineup()

    # Get flex rankings from fantasy pros
    rankings = football.get_fpros_rankings('FLEX', 'week')

    # Fill in simple positions
    line_up.QB = football.get_espn_roster('QB')[0].name
    line_up.TE = football.get_espn_roster('TE')[0].name
    line_up.K = football.get_espn_roster('K')[0].name
    line_up.DST = football.get_espn_roster('DST')[0].name

    # Get my roster
    rbs = [p.name for p in football.get_espn_roster('RB') if p.name in rankings]
    wrs = [p.name for p in football.get_espn_roster('WR') if p.name in rankings]

    # Get the ranks for my roster
    rbs_ranked = [{'player': p, 'rank': rankings.index(p)} for p in rbs]
    wrs_ranked = [{'player': p, 'rank': rankings.index(p)} for p in wrs]

    # Sort list of dictionaries by rank
    rbs_sorted = sorted(rbs_ranked, key=lambda p: p['rank'])
    wrs_sorted = sorted(wrs_ranked, key=lambda p: p['rank'])

    # Set lineup for RB and WR positions
    line_up.RB1, line_up.RB2 = rbs_sorted[0]['player'], rbs_sorted[1]['player']
    line_up.WR1, line_up.WR2 = wrs_sorted[0]['player'], wrs_sorted[1]['player']

    # Set lineup for flex position
    flex_ranked = rbs_sorted[2:] + wrs_sorted[2:]
    flex_sorted = sorted(flex_ranked, key=lambda p: p['rank'])
    line_up.FLX = flex_sorted[0]['player']

    # Render email
    rendered = line_up.render(football.team_id, football.league_id)
    with open(os.path.join(directory, 'result.html'), 'wt', encoding='utf-8') as f:
        f.write(rendered)
    print('done')


if __name__ == '__main__':
    lineup(THIS_DIR)
