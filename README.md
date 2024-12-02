# Fantasy Football System

| Pos  | Week | Season |
|------|------|--------|
| QB   | 0    | 3      |
| RB   | 0    | 4      |
| WR   | 0    | 4      |
| TE   | 1    | 0      |
| DST  | 1    | 0      |
| K    | 1    | 0      |

## Database Tables

### Weekly Rankings
```sql
create table weekly_rank (
	expert varchar(50),
	year smallint,
	week smallint,
	slot varchar(3),
	rank smallint,
	player varchar(50),
	unique(expert, year, week, slot, rank)
)
```

### Rest-of-Season Rankings
```sql
create table season_rank (
	expert varchar(50),
	date date,
	slot varchar(3),
	rank smallint,
	player varchar(50),
	unique(expert, date, slot, rank)
)
```
