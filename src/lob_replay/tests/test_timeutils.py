from src.lob_replay.timeutils import parse_hhmmssmmm

def test_parse_hhmmssmmm():
    assert parse_hhmmssmmm(84501000) == (8, 45, 1, 0)
    assert parse_hhmmssmmm("084501123") == (8, 45, 1, 123)
