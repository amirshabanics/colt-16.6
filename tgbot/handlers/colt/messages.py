from users.models import User


def player_list_message(players: list[User]) -> str:
    res = f"""
        Players List:

    """
    for i, p in enumerate(players):
        res += f"{i+1}. {p.tg_str}\n"

    return res
