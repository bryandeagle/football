"""
Trade our worst seasonal player in each position for the best weekly
"""

from os import getenv
import common

if __name__ == "__main__":
    threshold = 2  # Number of points to be worth picking up

    # For each position find better weekly player
    config = common.get_config()
    league, moves = common.League(config), list()
    for pos in ("TE", "D/ST", "K"):
        drop = sorted(league.roster(pos), key=lambda p: p.season)[0]
        agents = league.free_agents(pos)
        players = sorted(agents, key=lambda p: p.weekly, reverse=True)
        take = [p for p in players[:3] if p.weekly - drop.weekly > threshold]
        moves.extend([{"drop": drop, "take": t} for t in take])

    # Build results text
    text = "Free Agent Selections\n=====================\n"
    for i, move in enumerate(moves):
        bonus = move["take"].weekly - move["drop"].weekly
        text += f"{i+1}. Drop {move['drop']} take {move['take']} "
        text += f"for {bonus:+.0f} pts\n"

    # Email or print moves
    if getenv("WM_WORKSPACE", None):
        common.send_mail(config, "Free Agent Selections", text)
    else:
        print("\n" + text)
