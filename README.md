# Fantasy Football Scripts

These scripts execute the most basic weekly fantasy football management strategy possible. For each player we care about two stats: the **week's** projection and the **season's** projection. The table below shows how we allocate the 17 roster slots by both position and week/season.

For QB, RB, and WR we only care about seasonal projections. Because we have so many of them, we should be able to play good players each week. For positions like TE, DS/T, and K, we have a slot for the best player of the given week, since there will likely be good streaming options. For TE and D/ST we also keep a slot for the best seasonal player.

| Pos  | Week | Season |
|------|------|--------|
| QB   | 0    | 4      |
| RB   | 0    | 4      |
| WR   | 0    | 4      |
| TE   | 1    | 1      |
| D/ST | 1    | 1      |
| K    | 1    | 0      |

There are three things we have to do each week.

### Tuesday: Waiver Wires
Trade the worst seasonal player for the best available ones in each position.

```sh
python3 football/waivers.py
```

### Wednesday: Free Agents
Trade the worst seasonal player for the best _of this week_ in each position.
Also, set initial line-up to cover Thursday game.

```sh
python3 football/free_agent.py
python3 football/line_up.py
```

### Saturday: Final Line-Up
Set final line-up before Sunday games.

```sh
python3 football/line_up.py
```
