import os
import pty
import re
import subprocess
import time
from datetime import datetime

import yaml
from manager import gnuscreen_reader as screen

with open('settings.yml', 'r', encoding="utf-8") as fs:
    settings = yaml.load(fs, Loader=yaml.SafeLoader)
    Pass = settings['password']

master = {}
slave = {}
console = {}
players_online = {}

for i in settings['server'].keys():
    master[i], slave[i] = pty.openpty()
    console[i] = ""

env = dict(os.environ)
env["TERM"] = "vt100"

socketio_status = 'disconnect'


def start_server(server):
    """
    サーバーを起動させる
    """
    global console

    # ディレクトリを指定
    dir = settings['server'][server]['directory']
    p = subprocess.Popen(
        f'screen -S {settings["server"][server]["screen-id"]} {settings["server"][server]["command"]}',
        stdin=slave[server], stdout=slave[server], stderr=slave[server], close_fds=True, shell=True, cwd=dir, env=env
    )

    # コンソールを取得する
    console[server] = ''
    for chunk in screen.read(master[server]):

        # 最初の謎の文字を削除
        if chunk == b'\x1b[?1h\x1b=\x1b[0m\x1b(B\x1b[1;24r' or chunk == b'\x1b[H\x1b[J\x1b[H\x1b[J':
            continue

        """
        # コマンド実行時の文字かぶりを削除
        if re.match(rb'\x1b\[31m.*\x1b\[0m', chunk):
            continue

        if re.match(rb'.*\x08.*\x1b\[K.*', chunk):
            chunk = b'WEB >>>>  ' + chunk
        """

        # 変数に出力を追加
        console[server] += chunk.decode('utf-8')

        # サーバー終了を検知
        if '[screen is terminating]' in chunk.decode('utf-8'):
            with open('manager/status.yml', 'r') as s:
                status = yaml.load(s, Loader=yaml.SafeLoader)
            status[server] = 'stop'
            with open('manager/status.yml', 'w') as f:
                yaml.dump(status, f, default_flow_style=False)
            break

        # サーバー起動完了を検知しstatusに保存
        if settings['server'][server]['type'] == 'proxy':
            if 'Listening on' in chunk.decode('utf-8'):
                with open('manager/status.yml', 'r') as s:
                    status = yaml.load(s, Loader=yaml.SafeLoader)
                status['proxy'] = 'run'
                with open('manager/status.yml', 'w') as f:
                    yaml.dump(status, f, default_flow_style=False)
        else:
            if 'Done' in chunk.decode('utf-8'):
                with open('manager/status.yml', 'r') as s:
                    status = yaml.load(s, Loader=yaml.SafeLoader)
                status[server] = 'run'
                with open('manager/status.yml', 'w') as f:
                    yaml.dump(status, f, default_flow_style=False)


def stop_server(server):
    """
    サーバーを停止させる
    """
    if settings['server'][server]['type'] == 'proxy':
        subprocess.run("screen -S " + settings['server'][server]['screen-id'] + " -X stuff end^M", shell=True)
    else:
        subprocess.run("screen -S " + settings['server'][server]['screen-id'] + " -X stuff stop^M", shell=True)


def restart_server(server):
    """
    サーバーを再起動させる（停止->起動）
    """
    stop_server(server)
    if server == 'proxy':
        while True:
            with open('manager/status.yml', 'r') as s:
                status = yaml.load(s, Loader=yaml.SafeLoader)
            if status['proxy'] == "stop":
                break
            time.sleep(0.1)
    elif server == 'lobby':
        while True:
            with open('manager/status.yml', 'r') as s:
                status = yaml.load(s, Loader=yaml.SafeLoader)
            if status['lobby'] == "stop":
                break
            time.sleep(0.1)
    elif server == 'main':
        while True:
            with open('manager/status.yml', 'r') as s:
                status = yaml.load(s, Loader=yaml.SafeLoader)
            if status['main'] == "stop":
                break
            time.sleep(0.1)
    start_server(server)


def exe_command(server, command):
    """
    コマンドを実行する
    """
    if server == 'proxy':
        cmd = "screen -S mc-Proxy -X stuff"
        cmd = cmd.split()
        cmd.append(command + "^M")
        subprocess.run(cmd)
    elif server == 'lobby':
        cmd = "screen -S mc-Lobby -X stuff"
        cmd = cmd.split()
        cmd.append(command + "^M")
        subprocess.run(cmd)
    elif server == 'main':
        cmd = "screen -S mc-Main -X stuff"
        cmd = cmd.split()
        cmd.append(command + "^M")
        subprocess.run(cmd)


def detect_player():
    global players_online
    while True:
        with open('manager/status.yml', 'r') as s:
            status = yaml.load(s, Loader=yaml.SafeLoader)
        # typeがproxyであるものを探す
        for key in settings['server'].keys():
            if settings['server'][key].get('type') == 'proxy':
                if status[key] == 'run':
                    subprocess.run(f"screen -S {settings['server'][key]['screen-id']} -X stuff glist^M", shell=True)
                    for chunk in screen.read(master[key]):
                        if re.findall(r'\d+', chunk.decode('utf-8')):
                            if re.findall(r'\d+', chunk.decode('utf-8')):
                                po = int(re.findall(r'\d+', chunk.decode('utf-8'))[-1])
                                players_online[f'{datetime.hour}:{datetime.minute}'] = po
        time.sleep(60 * 5)
