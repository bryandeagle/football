from football import Football, _create_id

football = Football()


def test_create_id():
    player_id = _create_id('Bryan Deagle', 'QB')
    assert player_id == 'qbbdeagle'


def test_get_week():
    assert football._get_week('2020-09-07') == 1
