from football import Football
from datetime import datetime
import toml
import os

# Grab config
this_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(this_dir, 'config.toml')) as f:
    config = toml.loads(f.read())


f = Football()

#week_one = datetime.strptime('2020-09-07', '%Y-%m-%d')
#today = datetime.strptime('2020-09-15', '%Y-%m-%d')

# _week = today.isocalendar()[1] - week_one.isocalendar()[1]
#_week = int(today.strftime('%W')) - int(week_one.strftime('%W')) + 1
#print('week={}'.format(_week))
