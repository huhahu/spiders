# coding=utf-8
import time
# import schedule
import paramiko
from rediscluster import StrictRedisCluster

from .config import *


class PullProxy(object):
    startup_nodes = [
        {"host": "192.168.50.144", "port": 6003},
        {"host": "192.168.50.144", "port": 6004},
        {"host": "192.168.50.181", "port": 6003},
        {"host": "192.168.50.181", "port": 6004},
        {"host": "192.168.50.200", "port": 6003},
        {"host": "192.168.50.200", "port": 6004},
    ]

    def __init__(self):
        self.key = 'sdg_spider_proxy'
        self.rc = StrictRedisCluster(startup_nodes=self.startup_nodes, decode_responses=True)

    @property
    def proxy(self):
        return self.rc.get(self.key)

    @proxy.setter
    def proxy(self, value):
        self.rc.set(self.key, value)
        print('end pull!')

    def pull(self):
        while True:
            try:
                print('start pull!')
                sf = paramiko.Transport("%s:%s" % (SFTP_HOST, SFTP_PORT))
                sf.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
                sftp = paramiko.SFTPClient.from_transport(sf)
                sftp.get(REMOTE, LOCAL)
                sf.close()
                with open(LOCAL) as f:
                    value = f.readline()
                    self.proxy = value
                    print('proxy server: ', value)
                time.sleep(1)
            except Exception as e:
                print(e)


def run():
    pp = PullProxy()
    pp.pull()


if __name__ == '__main__':
    # schedule.every(1).seconds().do(run)
    run()
