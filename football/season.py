import psycopg2
from psycopg2.extras import execute_batch

from common.constants import EXPERTS
from common.fpros import FantasyPros
from common.utils import config, log

YEAR = 2024


if __name__ == "__main__":
    fantasy = FantasyPros()
    database = psycopg2.connect(**config["database"])

    with database.cursor() as cursor:

        # Get all known rankings from database
        query = "select distinct expert,year,week,slot from weekly;"
        cursor.execute(query)
        known_rankings = cursor.fetchall()

        # Loop through experts weeks and years
        for expert in EXPERTS:
            for slot in {"QB", "RB", "WR", "TE", "DST", "K"}:
                if (expert, YEAR, week, slot) not in known_rankings:
                    ranks = fantasy.rank(
                        expert=expert,
                        slot=slot,
                        period="ros",
                        year=YEAR,
                    )

                    # Build rankings as list-of-dictionaries
                    d = {"expert": expert, "year": YEAR, "week": None, "slot": slot}
                    ranks = [d | {"rank": r[0], "player": r[1]} for r in ranks]

                    # Insert data into database
                    columns = ",".join([f"%({c})s" for c in ranks[0].keys()])
                    query = f"insert into weekly values ({columns})"
                    execute_batch(cursor, query, ranks)
                    database.commit()

                    # Log status
                    log.info(f"{expert} ({slot})")

    database.close()  # Close database connection
