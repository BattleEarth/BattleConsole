# BattleConsole
💻Minecraftサーバーを管理するWebアプリケーション<br />
[Sample](http://dev.mydd.jp:5000)

## 使い方(flaskの場合)
```
git clone git@github.com:BattleEarth/BattleConsole.git
cd BattleConsole
export FLASK_APP=manager
flask run
```
また、必要に応じてライブラリを追加してください。

## settings.ymlの設定
settings.yml
```
password: Webで使用するパスワード

root-directory: File Managerでのルートパス(最下層)

server:
  サーバー名(PythonのサーバーIDとして使用されます):
    name: Web上で表示されるサーバー名
    directory: jarファイルがあるディレクトリ
    command: サーバーを起動するコマンド
    screen-id: GNU screenで使用されるセッション名
    type: サーバータイプ（proxy または minecraft）

