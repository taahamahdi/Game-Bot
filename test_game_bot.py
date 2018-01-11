from game_bot import game_search


def test_game_search():
    # maybe these test aren't the best but we just want to make sure it works
    # these appids are unlikely to change, and we're using very specific names
    assert(game_search("Portal 2") == "620")
    assert(game_search("DOOM") == "379720")
