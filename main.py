import math
import random
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.players import BasePokerPlayer
from tcp.server import ask_action


# ------------------------------------------------------------------------------
# 定义一个人类玩家，通过命令行输入决策
# ------------------------------------------------------------------------------
class HumanPlayer(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        """
        人类玩家决策接口，展示当前底牌和操作选项，通过命令行输入选择操作。

        参数说明:
            valid_actions: 当前可执行的操作列表，每项为字典形式。
            hole_card: 当前玩家手中的两张底牌。
            round_state: 当前回合状态（包含公共牌、历史动作等）。

        返回:
            (action, amount)：玩家的选择以及下注金额（若操作为 raise）。
        """
        # 显示玩家当前底牌
        print("\n你的底牌:", [self.convert_card(card) for card in hole_card])
        # 显示可行操作
        print("当前可选操作:")
        for idx, action_info in enumerate(valid_actions):
            action = action_info['action']
            if action == "raise":
                amount_info = action_info.get('amount', {})
                print(f"  [{idx}] {action} (下注金额范围: {amount_info.get('min')} - {amount_info.get('max')})")
            else:
                print(f"  [{idx}] {action}, 下注金额: {action_info['amount']}")
        # 循环等待玩家输入有效选项
        while True:
            try:
                choice = int(input("请输入操作对应的序号: "))
                if 0 <= choice < len(valid_actions):
                    chosen_action = valid_actions[choice]
                    break
                else:
                    print("输入错误，请输入有效序号。")
            except ValueError:
                print("输入无效，请输入数字。")
        action_name = chosen_action['action']
        amount = chosen_action['amount']
        # 如果选择了加注，提示输入下注金额，并验证范围
        if action_name == "raise":
            min_amount = chosen_action['amount']['min']
            max_amount = chosen_action['amount']['max']
            while True:
                try:
                    amount = int(input(f"请输入下注金额（范围 {min_amount} ~ {max_amount}): "))
                    if min_amount <= amount <= max_amount:
                        break
                    else:
                        print("下注金额不在允许范围内，请重新输入。")
                except ValueError:
                    print("输入无效，请输入数字。")
        return action_name, amount

    def receive_game_start_message(self, game_info):
        # 可以在游戏开始时显示相关配置信息
        print("游戏开始，配置信息：", game_info)

    def receive_round_start_message(self, round_count, hole_card, seats):
        if round_count > self.table.round:
            self.table.dealer += 1
            self.table.round += 1

    def receive_street_start_message(self, street, round_state):

        pass

    def receive_game_update_message(self, action, round_state):
        """
        使用命令行打印游戏信息，格式如下：

                       pot:xxx
           bet1      bet2     bet3    ...（投注金额，居中显示）
        player1   player2   player3    ...（玩家名称，居中显示）
           stack1    stack2   stack3   ...（玩家剩余筹码，居中显示）

        参数:
            action: 当前触发的操作信息（此处不直接使用）。
            round_state: dict，必须包含以下字段：
                "seats": list，每个元素为字典，包含键：
                    "name": str, 玩家姓名；
                    "bet": int, 当前局玩家已投入的筹码；
                    "stack": int, 玩家剩余筹码数；
                "pot": int, 当前底池的筹码总量。
        """
        # 从 round_state 中提取玩家列表和底池金额
        seats = round_state.get("seats", [])
        pot = round_state.get("pot", 0)

        if not seats:
            return

        # 设定每个玩家输出信息的固定列宽
        col_width = 12  # 可根据需要调整宽度
        num_players = len(seats)
        total_width = num_players * col_width

        # 打印底池信息，居中显示在总宽度中
        pot_line = f"pot:{pot}"
        print(pot_line.center(total_width))

        # 打印每个玩家投入的筹码（bet）
        bet_line_parts = []
        for seat in seats:
            bet = seat.get("bet", 0)
            # 转换为字符串并居中对齐
            bet_str = f"{bet}".center(col_width)
            bet_line_parts.append(bet_str)
        print("".join(bet_line_parts))

        # 打印玩家名称，居中对齐
        name_line_parts = []
        for seat in seats:
            name = seat.get("name", "?")
            name_str = f"{name}".center(col_width)
            name_line_parts.append(name_str)
        print("".join(name_line_parts))

        # 打印玩家剩余的筹码（stack）
        stack_line_parts = []
        for seat in seats:
            stack = seat.get("stack", 0)
            stack_str = f"{stack}".center(col_width)
            stack_line_parts.append(stack_str)
        print("".join(stack_line_parts))

    def receive_round_result_message(self, winners, hand_info, round_state):
        # 回合结束后显示胜利者信息
        print("\n回合结束。胜利者：", winners)
        print("本局详细信息：", hand_info)

class ServerPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        return ask_action(self.name,valid_actions)

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


class Table:
    def __init__(self, player_amount, init):
        self.player = []
        self.names = []
        self.dealer = 0
        self.round = 0
        self.status = ["in"] * player_amount
        self.bet = [0] * player_amount
        self.chips = [init] * player_amount
        self.cards = [None] * player_amount
        self.community_cards = []

    def someone_action(self, my_name, action, amount):
        pos = int(my_name[-1])
        self.status[pos] = action
        self.bet[pos] += amount
        self.chips[pos] -= amount


def start_game(con):

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
