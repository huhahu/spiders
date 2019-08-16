# coding=utf-8

import paramiko
import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler, Application

from proxy.adslproxy.config import *


class MainHandler(RequestHandler):

    def get(self):
        download_file()
        with open(LOCAL) as f:
            data = f.readline()
            self.write(data)


def download_file():
    sf = paramiko.Transport("%s:%s" % (SFTP_HOST, SFTP_PORT))
    sf.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(sf)
    sftp.get(REMOTE, LOCAL)
    sf.close()


def server(port=API_PORT, address=''):
    application = Application([
        (r'/', MainHandler),
        (r'/(.*)', MainHandler),
    ])
    application.listen(port, address=address)
    print('ADSL API Listening on', port)
    tornado.ioloop.IOLoop.instance().start()
