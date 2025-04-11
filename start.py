from tkinter.font import names

from players import Table, ServerPlayer, HumanPlayer
from pypokerengine.api.game import setup_config, start_poker


def start_game(con):

    config = setup_config(**con)

    #注册桌子
    table = Table(con["player_amount"], con["initial_stack"])
    # 注册玩家
    for i in range(con["player_amount"]):
        name = con["username"][i]
        player_i = ServerPlayer(table, name)
        player_i.sid=con["user_sid_map"][name]
        player_i.socketio=con["socketio"]
        table.player.append(player_i)
        table.names.append(name)
        config.register_player(name=name, algorithm=player_i)
    print(len(table.player))

    # 开始游戏
    game_result = start_poker(config, verbose=1)

if __name__ == "__main__":
    pass
