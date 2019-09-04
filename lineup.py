from football import Football, Email
from jinja2 import Template
import yaml

CONFIG_FILE = 'config.yaml'


class Lineup:
    def __init__(self):
        self.RB1 = None
        self.RB2 = None
        self.WR1 = None
        self.WR2 = None
        self.FLX = None
        self.TE = None
        self.K = None
        self.DST = None

    def render(self):
        t = Template(open('templates/lineup.html', 'r').read())
        return t.render(lineup=self)

    def __repr__(self):
        return 'Optimal Line-Up:\n  RB1: {}\n  RB2: {}\n  WR1: {}\n' \
               '  WR2: {}\n  FlX: {}\n  TE:  {}\n  K:   {}\n  DST: {}'\
            .format(self.RB1, self.RB2, self.WR1, self.WR2, self.FLX,
                    self.TE, self.K, self.DST)


if __name__ == '__main__':

    # Initialize API and lineup list
    config = yaml.load(open(CONFIG_FILE, 'r'))
    mail = Email(config['email'])

    try:
        football = Football(config['football'])
        lineup = Lineup()

        # Get flex rankings from fantasy pros
        rankings = football.get_fpros_rankings('FLEX', 'week')

        # Fill in simple positions
        lineup.TE = football.get_espn_roster('TE')[0]
        lineup.K = football.get_espn_roster('K')[0]
        lineup.DST = football.get_espn_roster('DST')[0]

        # Get my roster
        rbs = football.get_espn_roster('RB')
        wrs = football.get_espn_roster('WR')

        # Build list of dictionaries to include rank
        rbs_ranked = [{'player': p, 'rank': rankings.index(p)} for p in rbs]
        wrs_ranked = [{'player': p, 'rank': rankings.index(p)} for p in wrs]

        # Sort list of dictionaries by rank
        rbs_sorted = sorted(rbs_ranked, key=lambda p: p['rank'])
        wrs_sorted = sorted(wrs_ranked, key=lambda p: p['rank'])

        # Set lineup for RB and WR positions
        lineup.RB1, lineup.RB2 = rbs_sorted[0]['player'], rbs_sorted[1]['player']
        lineup.WR1, lineup.WR2 = wrs_sorted[0]['player'], wrs_sorted[1]['player']

        # Set lineup for flex position
        flex_ranked = rbs_sorted[2:] + wrs_sorted[2:]
        flex_sorted = sorted(flex_ranked, key=lambda p: p['rank'])
        lineup.FLX = flex_sorted[0]['player']

        # Send email
        mail.send(subject=config['lineup']['subject'], html=lineup.render())

    except Exception as e:
        # Send error email
        mail.send(subject='An Error Occurred', html=str(e))
