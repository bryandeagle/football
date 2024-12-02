import json

from espn_api.football import League
from espn_api.football.constant import POSITION_MAP


class ESPN:
    def __init__(self, config: dict):
        # Initialize ESPN API with creds in config dict
        settings = ("league_id", "year", "espn_s2", "swid")
        self.league = League(**{k: config[k] for k in settings})
        self.week = self.league.nfl_week

    @property
    def get_team(self):
        team = self.config["team_id"]
        return [t for t in self.league.teams if t.team_id == team][0]

    def all_players(self) -> list:

        pos = [POSITION_MAP[p] for p in {"QB", "RB", "WR", "TE", "D/ST", "K"}]
        filters = {
            "players": {
                "filterSlotIds": {"value": pos},
                "limit": 10000,
                "sortPercOwned": {"sortPriority": 1},
            }
        }

        response = self.league.espn_request.league_get(
            params={"view": "kona_player_info"},
            headers={"x-fantasy-filter": json.dumps(filters)},
        )

        table = [
            {"id": p["id"], "name": p["player"]["fullName"]}
            for p in response["players"]
        ]

        with open("results.json", "wt") as f:
            f.write(json.dumps(table, default=str, indent=2))
        return table
