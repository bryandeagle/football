import logging
import sys
from os import getenv, path

import requests
import wmill
import yaml
from espn_api.football import League as EspnLeague
from espn_api.football.player import Player as EspnPlayer

# Configure logging
logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format="%(levelname)s:%(message)s"
)
logger = logging.getLogger(__name__)


def get_config():
    """Load configuration"""
    if getenv("WM_WORKSPACE", None):
        # Get configuration from Windmill
        logger.info("Loading config from windmill variable")
        return yaml.safe_load(wmill.get_variable("u/admin/config"))
    else:
        # Load configuration from YAML file
        logger.info("Loading config from file")
        base = path.dirname(path.abspath(__file__))
        with open(path.join(base, "..", "..", "config.yml"), "rt") as f:
            return yaml.safe_load(f)


def send_mail(config: dict, subject: str, text: str) -> None:
    """Send email with mailgun"""
    requests.post(
        "https://api.mailgun.net/v3/mg.dea.gl/messages",
        auth=("api", config["mailgun"]),
        data={
            "from": "Fantasy AutoPilot <autopilot@mg.dea.gl>",
            "to": "bryan@dea.gl",
            "subject": subject,
            "text": text,
        },
    )
    logger.info(f"Sent {subject} email")


class League:
    def __init__(self, config: dict):
        # Initialize ESPN API with creds in config.yml
        settings = ("league_id", "year", "espn_s2", "swid")
        self.league = EspnLeague(**{k: config[k] for k in settings})
        team = config["team_id"]  # Get team ID from config
        self.team = [t for t in self.league.teams if t.team_id == team][0]
        logger.info(f"Team is {self.team.team_name}")
        self.week = self.league.nfl_week
        logger.info(f"Determined week number {self.week}")

    def roster(self, pos: str) -> dict:
        """Get team roster for given position"""
        roster = self.team.roster
        return [Player(p, self.week) for p in roster if p.position == pos]

    def free_agents(self, position: str) -> list:
        """Get free agents for given position"""
        players = self.league.free_agents(size=1000, position=position)
        return [Player(p, self.week) for p in players]


class Player(EspnPlayer):
    """An extension of the default Player class with
    some convenciences added, like easier access to
    projectsions and pretty printing"""

    def __init__(self, player, week):
        self.season = player.projected_total_points
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
