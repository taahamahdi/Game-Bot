from game_bot import game_search


def test_game_search():
    # maybe these test aren't the best but we just want to make sure it works
    # these appids are unlikely to change, and we're using very specific names
    assert(game_search("Portal 2", "us") == "620")
    assert(game_search("DOOM", "ca") == "782330")
    assert(game_search("csgo") == "730")
    assert(game_search("grand theft auto iv") == "901583")
    print("Passed!")


test_game_search()
