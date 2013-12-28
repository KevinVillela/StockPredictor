'''
Created on Dec 18, 2013

@author: KevinVillela
'''
import threading
import socket
import urllib.request, urllib.error, urllib.parse
import sys # for sys.exit()
from subprocess import call
import os
import signal
import subprocess

class TorThread(threading.Thread):
    def __init__(self, parent):
        super(TorThread, self).__init__()
        self.parent = parent
        self.p = None
    def run(self):
        self.startTor()
    def stop(self):
        print("Tor stopping...")
        #os.kill(os.getpid(), signal.SIGUSR1)
        os.kill(self.p.pid,signal.SIGKILL)
        #sys.exit()
        return
    def startTor(self):
        #call(["/usr/local/bin/tor"])
        cmd = "~/usr/local/bin/tor"
        self.p = subprocess.Popen(args = cmd, shell=True, universal_newlines = True,preexec_fn=os.setsid)