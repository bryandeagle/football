"""
Trade our worst seasonal player in each position for the best
"""

from common import League


if __name__ == "__main__":
    # Find top three seasonal free agents by position
    league, moves = League(), list()
    for pos in ("QB", "RB", "WR", "TE", "D/ST"):
        drop = sorted(league.roster(pos), key=lambda p: p.season)[0]
        players = sorted(league.free_agents(pos), key=lambda p: p.season, reverse=True)
        take = [p for p in players[:3] if p.season > drop.season]
        moves.extend([{"drop": drop, "take": t} for t in take])

    # Display moves
    print("\nWaiver Wire Selections\n======================\n")
    for i, move in enumerate(moves):
        bonus = move["take"].season - move["drop"].season
        print(f"{i+1}. Drop {move['drop']} take {move['take']} for {bonus:+.0f} pts")
