#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.protocols import basic
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import random

from twisted.internet.task import LoopingCall

import json

import time

### Protocol Implementation
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500

identifier = 0
FPS = 10.0

client_names = ["client0", "client1"]
spaghetti_names = ["spaghetti0", "spaghetti1", "spaghetti2", "spaghetti3", "spaghetti4", "spaghetti5", "spaghetti6", "spaghetti7", "spaghetti8", "spaghetti9"] 

class ChatClient(basic.LineReceiver):
    client_dict = {}
    #spaghetti0 spaghetti1 spaghetti2 ... spaghettiN in the dictionary
    #

    def init(self):
        global spaghetti_names

        self.lc = LoopingCall(self.send)
        self.lc.start(1.0 / FPS)

        for spa in spaghetti_names:
            self.client_dict[spa] = {"position": [random.randint(10, WINDOW_WIDTH - 10), random.randint(100, 200)]}

    def connectionMade(self):
        global identifier
        print("Got new client!")
        self.delimiter = '\n'
        self.factory.clients.append(self)

        if identifier < 2:
            id_message = client_names[identifier]
            self.message(id_message)
            self.client_dict[client_names[identifier]] = {"position": [100,100]}
            identifier += 1

        if identifier is 1:
            self.init()

    def connectionLost(self, reason):
        print("Lost a client!")
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        json_receive = json.loads(line.rstrip())
        self.client_dict[json_receive["ID"]] = {"position": json_receive["position"]}
        print self.client_dict

    def send(self):
        for c in self.factory.clients:
            c.message(json.dumps(self.client_dict))

    def message(self, message):
        self.transport.write(message + '\n')

def main():
    f = Factory()
    f.protocol = ChatClient
    f.clients = []
    print('Listening on 1025...')
    reactor.listenTCP(1025, f)
    reactor.run()

if __name__ == '__main__':
    main()
