"""
Trade our worst seasonal player in each position for the best
"""

from os import getenv
import common


if __name__ == "__main__":
    # Find top three seasonal free agents by position
    config = common.get_config()
    league, moves = common.League(config), list()
    for pos in ("QB", "RB", "WR", "TE", "D/ST"):
        drop = sorted(league.roster(pos), key=lambda p: p.season)[0]
        free_agents = league.free_agents(pos)
        players = sorted(free_agents, key=lambda p: p.season, reverse=True)
        take = [p for p in players[:3] if p.season > drop.season]
        moves.extend([{"drop": drop, "take": t} for t in take])

    # Build results text
    text = "Waiver Wire Selections\n======================\n"
    for i, move in enumerate(moves):
        bonus = move["take"].season - move["drop"].season
        text += f"{i+1}. Drop {move['drop']} take {move['take']}"
        text += f" for {bonus:+.0f} pts\n"

    # Email or print moves
    if getenv("WM_WORKSPACE", None):
        common.send_mail(config, "Waiver Wire Selections", text)
    else:
        print("\n" + text)
