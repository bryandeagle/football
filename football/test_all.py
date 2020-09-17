from football import Football, _create_id
from datetime import datetime

football = Football()


def test_secrets():
    assert football.secret


def test_create_id():
    player_id = _create_id('Bryan Deagle', 'QB', 'ATX')
    print(player_id)
    assert player_id == 'AtxQbBDeagle'


def test_roster():
    num = 0
    for k in football.roster.keys():
        num += len(football.roster[k])
    assert num == 16


def test_stats():
    stats = football._stats('TE', 'week')
    print(*stats, sep='\n')


if __name__ == '__main__':
    test_create_id()
