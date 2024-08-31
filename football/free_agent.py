"""
Trade our worst seasonal player in each position for the best weekly
"""

from common import League


if __name__ == "__main__":
    print("Free Agent Selections\n=====================\n")
    threshold = 2  # Number of points to be worth picking up

    # For each position find better weekly player
    league, moves = League(), list()
    for pos in ("TE", "D/ST", "K"):
        drop = sorted(league.roster(pos), key=lambda p: p.season)[0]
        players = sorted(league.free_agents(pos), key=lambda p: p.weekly, reverse=True)
        take = [p for p in players[:3] if p.weekly - drop.weekly > threshold]
        moves.extend([{"drop": drop, "take": t} for t in take])

    # Display moves
    for i, move in enumerate(moves):
        bonus = move["take"].weekly - move["drop"].weekly
        print(f"{i+1}. Drop {move['drop']} take {move['take']} for {bonus:+.0f} pts")
