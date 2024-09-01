"""
Determine ideal team line-up based on this week's projections
"""

from common import League


if __name__ == "__main__":
    # For each position find better weekly player
    league, lineup = League(), dict()
    
    # QB/OP
    qbs = sorted(league.roster("QB"), key=lambda p: p.weekly, reverse=True)
    lineup["QB"], lineup["OP"] = qbs.pop(0), qbs.pop(0)

    # WR / RB
    rbs = sorted(league.roster("RB"), key=lambda p: p.weekly, reverse=True)
    wrs = sorted(league.roster("WR"), key=lambda p: p.weekly, reverse=True)
    lineup["RB1"], lineup["RB2"] = rbs.pop(0), rbs.pop(0)
    lineup["WR1"], lineup["WR2"] = wrs.pop(0), wrs.pop(0)

    # Flex
    rb, wr = rbs.pop(0), wrs.pop(0)
    lineup["FLX"] = rb if rb.weekly > wr.weekly else wr

    # TE / K / DST
    for pos in ("TE", "D/ST", "K"):
        lineup[pos] = sorted(league.roster(pos), key=lambda p: p.weekly, reverse=True)[0]

    # Display line-up
    print("\nTeam Line-Up\n============\n")
    for position in lineup:
        print(f"{position}: {lineup[position]} ({lineup[position].weekly:.0f} pts)")

