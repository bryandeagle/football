from ffn import Football
import json


if __name__ == '__main__':
    football = Football()

    to_add = list()
    to_drop = dict()

    for pos in football.slots.keys():
        fa = football.free_agents_by_pos(pos)
        team = football.roster_by_pos(pos, sort=True)
        starters = team[0:football.slots[pos]]
        better = [p for p in fa if p['score'] > starters[-1]['score']]
        to_drop[pos] = min(len(better), football.slots[pos])
        to_add += better

    for x in to_add:
        print(x)
