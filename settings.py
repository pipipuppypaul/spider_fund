
import Agents
import random
import paramiko #用来执行远程shell

comment_url = 'https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol={symbol}&hl=0&source=all&sort=time&page={page}&q='
headers = {
    'User-Agent': random.choice(Agents.agents)
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#ssh.connect('IP address',22,'username', 'password') 自己添加
#ssh.connect('127.0.0.1',22) #或者链接本地
#以上设置是远程写入文件的设置

# PSQL database
PSQL_DATABASE = 'DBname'
# PSQL username
PSQL_USERNAME = 'username'
# PSQL password
PSQL_PASSWORD = 'password'
# PSQL host
PSQL_HOST = 'IP address'
# PSQL port
PSQL_PORT = 'port'

#上面这些配置都要自己修改，但如果不用psql就不用设置了