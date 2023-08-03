from users.models import User
from colt.models import Game


def player_list_message(game: Game) -> str:

    players = game.players.all()
    section = game.current_section
    current_players = game.current_section.all_players if section is not None else game.players.all()

    res = "Players List:\n"
    for i, p in enumerate(players):
        res += f'  {i+1}. {p.tg_str} : {"Dead" if (p not in current_players) or (game.winner is not None and game.winner != p)  else "Lived"}\n'

    if game.winner is not None:
        res += f"\nWinner:\n  {game.winner.tg_str}"
        return res

    if section is None:
        return res

    res += f"\n\nPlayers Order:\n"
    for i, p in enumerate(current_players):
        res += f'  {i+1}. {p.tg_str}\n'

    _, user = section.player_turn
    res += f"\n\nPlayer Turn:\n  {user.tg_str}"

    return res
