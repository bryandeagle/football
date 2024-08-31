from espn_api.football.player import Player as EspnPlayer
from espn_api.football import League as EspnLeague
from os import path
import yaml
import json


class League:
    def __init__(self):
        # Load configuration from YAML file
        base = path.dirname(path.abspath(__file__))
        with open(path.join(base, "..", "..", "config.yml"), "rt") as f:
            config = yaml.safe_load(f)

        # Initialize ESPN API with creds in config.yml
        settings = ("league_id", "year", "espn_s2", "swid")
        self.league = EspnLeague(**{k: config[k] for k in settings})
        self.team = [t for t in self.league.teams if t.team_id == config["team_id"]][0]

    @property
    def week(self) -> int:
        """Get Football week number"""
        return 1  # TODO: Implement

    def roster(self, position: str) -> dict:
        """Get team roster for given position"""
        return [
            Player(p, self.week) for p in self.team.roster if p.position == position
        ]

    def free_agents(self, position: str) -> list:
        """Get free agents for given position"""
        players = list()  # Make projections less cumbersome
        for player in self.league.free_agents(size=1000, position=position):
            players.append(Player(player, self.week))
        return players


class Player(EspnPlayer):
    """An extension of the default Player class with
    some convenciences added, like easier access to
    projectsions and pretty printing"""

    def __init__(self, player, week):
        self.player, self.no = player, week

        # Convient way to access projections
        self.season = player.stats[0]["projected_points"]
        self.weekly = player.stats[week]["projected_points"]
        self.team = player.proTeam

    def puke(self):
        return json.dumps(self.player.__dict__, indent=4, default=str)

    def __getattr__(self, attribute):
        """Get ESPN attribute"""
        return getattr(self.player, attribute)

    def __repr__(self):
        """Pretty printing"""
        if self.position == "D/ST":
            return self.name
        return f"{self.name} ({self.position}/{self.team})"
