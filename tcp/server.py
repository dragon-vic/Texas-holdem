from flask import Flask, request
from flask_socketio import SocketIO, send,emit

app = Flask(__name__)
# 创建 SocketIO 对象，默认为异步模式
socketio = SocketIO(app)
user_sid_map={}

@socketio.on('connect')
def handle_connect():
    sid = request.sid  # 获取当前连接的唯一会话ID
    print(f"新的连接：{sid}")
    send("请先登录", room=sid)

@socketio.on('login')
def handle_login(data):
    """
    客户端登录时需要发送username
    """
    print("11111",socketio)
    username = data
    sid = request.sid
    if username and username not in user_sid_map:
        user_sid_map[username] = sid
        print(f"用户名 {username} 对应的会话ID是 {sid}")
        send(f"登录成功，欢迎 {username}！", room=sid)
    else:
        send("换个名字", room=sid)
    # 如果达到3个客户端且未开始，则广播开始消息
    if len(user_sid_map) >= game_config['player_amount']:
        game_config['username'] = list(user_sid_map.keys())
        game_config['user_sid_map'] = user_sid_map
        game_config["socketio"] = socketio
        from start import start_game
        start_game(game_config)

@socketio.on('message')
def handle_message(msg):
    print("收到消息：", msg)


if __name__ == '__main__':

    game_config={"max_round":10, "initial_stack":100, "small_blind_amount":0.5,"player_amount":2}
    # 监听所有网络接口上的5000端口
    socketio.run(app, host='0.0.0.0', port=5000)
