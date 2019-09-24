# deaglefootball
Fantasy Football Auto Pilot

## Installing
Simply run 
```
setup.py
```
or run
```
pip install -e .
```

## Deploying

### Configuration
This is the structure of the required config.yaml file
```
email:
  mg_url: 'https://api.mailgun.net/v3/mg.dea.gl/messages'
  api_key: ''
  to: 'bryan@dea.gl'
  from: 'football@mg.dea.gl'
football:
  team_id: 4
  league_id: 1752514
  espn_s2: ''
  swid: ''
lineup:
  subject: 'Action Required: Set Your Line-Up'
waiver:
  subject: 'Action Required: Waiver Claims'
```

You can find your **api_key** [here](https://app.mailgun.com/app/account/security/api_keys).

You can find **espn_2** and **swid** after logging into your espn fantasy football account on espn's website. Then right click anywhere on the website and click inspect option. From there click Application on the top bar. On the left under Storage section click Cookies then http://fantasy.espn.com. From there you should be able to find your swid and espn_s2 variables and values.

### Automated Running
waiver.py should be run every Tuesday at 6:00 AM.

lineup.py should be run every Wednesday at 6:00 AM.