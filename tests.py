from templater import lcs


def test_lcs():
    a = [1, 2, 3, 4]
    b = [2, 3, 4, 5]
    assert lcs(a, b) == []
