"""
使用 Python-SocketIO 构建简单客户端
只需填写服务端 IP 和端口，即可与服务端建立连接，并能接收和发送消息
"""
import time
import socketio

from pypokerengine.api.game import setup_config

# 修改为你服务端的实际 IP 和端口，例如公网 IP '189.1.222.66'
SERVER_IP = '189.1.222.66'
SERVER_PORT = 5000
SERVER_URL = f'http://{SERVER_IP}:{SERVER_PORT}'

# 创建 SocketIO 客户端对象
sio = socketio.Client()

@sio.event
def connect():
    sio.emit("login", 1)

@sio.event
def message(data):
    print("收到消息：", data)

@sio.event
def disconnect():
    print("与服务器断开连接")

@sio.event
def reconnect():
    print("成功重新连接到服务器")

@sio.event
def action(valid_actions):
    print("需要操作")
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
    print("输入成功")
    return action_name, amount



def main():
    sio.connect(SERVER_URL)

    sio.wait()

    sio.disconnect()


if __name__ == '__main__':
    # 尝试连接服务器
    main()
