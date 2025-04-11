from players import Table, ServerPlayer, HumanPlayer
from pypokerengine.api.game import setup_config, start_poker


def start_game(config):



    #注册桌子
    table = Table(config["player_amount"], config["initial_stack"])
    # 注册玩家
    for i in range(config["player_amount"]):
        name = config["username"][i]
        player_i = ServerPlayer(table, name)
        table.player.append(player_i)
        table.names.append(name)
        setup_config(**config).register_player(name=name, algorithm=player_i)

    # 开始游戏
    game_result = start_poker(config, verbose=1)

if __name__ == "__main__":

    config = setup_config(**con)

    #注册桌子
    table = Table(player_amount, initial_stack)
    # 注册玩家
    for i in range(player_amount):
        name = f"player_{i}"
        if i == 0:
            player_i = HumanPlayer(table, name)
        else:
            player_i = ServerPlayer(table, name)
        table.player.append(player_i)
        table.names.append(name)
        config.register_player(name=name, algorithm=player_i)

    # 开始游戏
    game_result = start_poker(config, verbose=1)

    print("\n游戏结束，最终结果：")
    for player in game_result['players']:
        print(f"{player['name']}: 剩余筹码 {player['stack']}")

    winner = max(game_result['players'], key=lambda x: x['stack'])
    print(f"\n获胜者是 {winner['name']}，剩余筹码 {winner['stack']}")
