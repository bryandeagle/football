# Fantasy Football Auto Pilot 🏈
This tool informs me which waivers to choose, and how to set my line-up each week

## Installing
```
if [ ! -d "env" ]; then
        python3 -m venv env
fi
source env/bin/activate
pip install -r requirements.txt
```

## Deploying
Create **secrets.json** with the following format
```
{
  "ffn_api_key": "",
  "swid":  "",
  "espn_s2":  ""
}
```

You can find **ESPN_S2** and **SWID** after logging into your espn fantasy football account on espn's website. Then right click anywhere on the website and click inspect option. From there click Application on the top bar. On the left under Storage section click Cookies then http://fantasy.espn.com. From there you should be able to find your swid and espn_s2 variables and values.

### Running

Run **python lineup.py** or **python waiver.py**

waiver.py should be run every Tuesday at 6:00 AM.  
lineup.py should be run every Wednesday at 6:00 AM.
