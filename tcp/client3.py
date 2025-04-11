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
    sio.emit("login", input("登录成功，注册用户名："))

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
def action():
    print("到你行动了")



def main():
    sio.connect(SERVER_URL)

    sio.wait()

    sio.disconnect()


if __name__ == '__main__':
    # 尝试连接服务器
    main()
