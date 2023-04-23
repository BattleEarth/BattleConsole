import re

console = "aa [10:53:07 INFO]: Total players online: 0"
if re.findall(r'\d+', console):
    if re.findall(r'\d+', console):
        players_online = int(re.findall(r'\d+', console)[-1])
        print(players_online)
