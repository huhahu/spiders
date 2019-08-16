## 拨号主机设置

### 拨号上网

根据云主机拨号教程拨号上网，示例命令：

```
adsl-stop     # 停止拨号
adsl-start    # 开始拨号
```
#### 定时拨号

```
nohup python -u run.py > adsl.log 2>&1 &
```

## gost代理设置
### 代理配置
gost 是以go 语言编写的高性能代理服务器

以Centos上部署 Gost为例:
```
wget https://github.com/ginuerzh/gost/releases/download/v2.7.2/gost_2.7.2_linux_amd64.tar.gz
tar zxvf gost_2.7.2_linux_amd64.tar.gz
```

#### 启动代理服务
```
cd gost_2.7.2_linux_amd64
nohup ./gost -L http://user:passwd@0.0.0.0:2222 >gost.log 2>&1 &
# gost 代理会以后台进程方式执行，日志写入了gost.log
# 这里配置了账户密码，保证代理安全性
```

#### 测试

```
# 参考模式
curl -x usr:passwd@ip:port www.baidu.com
```

#### 防火墙
```
iptables -I INPUT -p tcp --dport 2222 -j ACCEPT
```
## 提取代理

### sftp下载代理
代理存入到vps proxy.txt文件中，远程服务器通过sftp从vps拉代理

#### 提供rest api
用Tornado 搭建了http server, 以写rest api的方式提取代理
#### 启动server
```
nohup python -u api.py >proxy.log 2>&1 &
```
已经部署在了测试服务器地址如下

http://192.168.50.144:8000/

#### 测试
```
python proxy_test.py
```
### 代理存入redis
pull.py
为了提高读写效率，决定把代理定时写入redis, 更新周期目前是1秒
爬虫直接从redis取代理


