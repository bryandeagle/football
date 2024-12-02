import requests
from bs4 import BeautifulSoup as bs

from .constants import EXPERTS


class FantasyPros:
    POSITIONS = {"QB", "RB", "WR", "TE", "K", "DST"}
    PERIODS = {"weekly", "ros"}
    SCORING = "PPR"

    def __init__(self):
        self.session = requests.Session()

    def rank(self, expert: str, slot: str, period: str, week: int, year: int):
        # Validate Inputs
        for input in (
            (slot, self.POSITIONS),
            (expert, EXPERTS),
            (period, self.PERIODS),
        ):
            if input[0] not in input[1]:
                raise ValueError(f"{input[0]} invalid")

        # Query fantasypros.com
        response = self.session.get(
            url=f"https://www.fantasypros.com/nfl/rankings/{expert}.php",
            params={
                "type": period,
                "scoring": self.SCORING,
                "week": week,
                "year": year,
                "position": slot,
            },
        )

        # Verify okay status code
        if response.status_code != 200:
            raise RuntimeError(f"{response.status_code} from {response.url}")

        # Find table and loop through it
        soup = bs(response.content, "html.parser")
        table = soup.find("table", {"id": "data"})
        if table is None:
            return [(None, None)]

        # Return if rankings are not available
        if "not available" in table.find("td").text:
            return [(None, None)]

        # Build rankings table
        rankings = []
        for row in table.find("tbody").find_all("tr"):
            columns = row.find_all("td")
            rankings.append((int(columns[0].text), columns[1].text.strip()))
        return rankings
