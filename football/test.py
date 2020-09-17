from football import Football


f = Football(debug=True)

for qb in f.free_agents('RB'):
    print('Name: {}, Team: {}, Pos: {}'.format(qb.name, qb.team, qb.position))
