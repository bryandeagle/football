from espn_api.football.player import Player as EspnPlayer
from espn_api.football import League as EspnLeague
from os import path, getenv
import logging
import wmill
import yaml
import sys


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(levelname)s:%(message)s"
)
logger = logging.getLogger(__name__)


class League:
    CONFIG = "config.yml"

    def __init__(self):
        windmill = getenv("WM_WORKSPACE", None)
        if getenv("WM_WORKSPACE", None):
            # Get configuration from Windmill
            logger.info("Loading config from windmill variable")
            config = yaml.safe_load(wmill.get_variable("u/admin/config"))
        else:
            # Load configuration from YAML file
            logger.info(f"Loading config from {self.CONFIG}")
            base = path.dirname(path.abspath(__file__))
            with open(path.join(base, "..", "..", self.CONFIG), "rt") as f:
                config = yaml.safe_load(f)

        # Initialize ESPN API with creds in config.yml
        settings = ("league_id", "year", "espn_s2", "swid")
        self.league = EspnLeague(**{k: config[k] for k in settings})
        self.team = [t for t in self.league.teams if t.team_id == config["team_id"]][0]
        logger.info(f"Team is {self.team.team_name}")
        self.week = self.league.nfl_week
        logger.info(f"Determined week number {self.week}")

    def roster(self, pos: str) -> dict:
        """Get team roster for given position"""
        return [Player(p, self.week) for p in self.team.roster if p.position == pos]

    def free_agents(self, position: str) -> list:
        """Get free agents for given position"""
        players = self.league.free_agents(size=1000, position=position)
        return [Player(p, self.week) for p in players]


class Player(EspnPlayer):
    """An extension of the default Player class with
    some convenciences added, like easier access to
    projectsions and pretty printing"""

    def __init__(self, player, week):
        self.season = player.stats[0]["projected_points"]
        self.weekly = player.stats[week]["projected_points"]
        self.team = player.proTeam
        self.player = player

    def __getattr__(self, attribute):
        """Get ESPN attribute"""
        return getattr(self.player, attribute)

    def __repr__(self):
        """Pretty printing"""
        if self.position == "D/ST":
            return self.name
        return f"{self.name} ({self.position}/{self.team})"
