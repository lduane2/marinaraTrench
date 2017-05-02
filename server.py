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
timeLeft = 60
p1_score = 0
p2_score = 0

identifier = 0
FPS = 10.0

PORT = 8000

client_names = ["client0", "client1"]
spaghetti_names = ["spaghetti0", "spaghetti1", "spaghetti2", "spaghetti3", "spaghetti4", "spaghetti5", "spaghetti6", "spaghetti7", "spaghetti8", "spaghetti9"] 

class ChatClient(basic.LineReceiver):
    client_dict = {}
    #spaghetti0 spaghetti1 spaghetti2 ... spaghettiN in the dictionary
    

    def init(self):
        global spaghetti_names

        for spa in spaghetti_names:
            self.client_dict[spa] = {"position": [random.randint(10, WINDOW_WIDTH - 10), random.randint(-500, -20)]}

        self.client_dict['time'] = timeLeft
        self.client_dict['p1_score'] = p1_score
        self.client_dict['p2_score'] = p2_score

        self.lc = LoopingCall(self.send)
        self.lc.start(1.0 / FPS)

    def connectionMade(self):
        global identifier
        print("Got new client!")
        self.delimiter = '\n'
        self.factory.clients.append(self)

        if identifier < 2:
            id_message = client_names[identifier]
            self.message(id_message)
            self.client_dict[client_names[identifier]] = {"position": [60,440]}
            identifier += 1

        if identifier is 1:
            self.init()

    def connectionLost(self, reason):
        print("Lost a client!")
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        json_receive = json.loads(line.rstrip())
        self.client_dict[json_receive["ID"]] = {"position": json_receive["position"]}
        #print self.client_dict

    def send(self):
        global timeLeft, p1_score, p2_score
        #collision detection
        if 'client0' in self.client_dict.keys() and 'client1' in self.client_dict.keys():
            p1_pos = self.client_dict['client0']['position']
            p2_pos = self.client_dict['client1']['position']
            for spa in spaghetti_names:
                spa_pos = self.client_dict[spa]['position']
                if p1_pos[0] > spa_pos[0] - 31 and p1_pos[0] < spa_pos[0] + 31 and p1_pos[1] > spa_pos[1] - 31 and p1_pos[1] < spa_pos[1] + 31: 
                    p1_score += 1
                    self.client_dict[spa] = {"position": [random.randint(10, WINDOW_WIDTH - 10), random.randint(-500, -20)]}
                if p2_pos[0] > spa_pos[0] - 31 and p2_pos[0] < spa_pos[0] + 31 and p2_pos[1] > spa_pos[1] - 31 and p2_pos[1] < spa_pos[1] + 31: 
                    p2_score += 1
                    self.client_dict[spa] = {"position": [random.randint(10, WINDOW_WIDTH - 10), random.randint(-500, -20)]}
                if spa_pos[1] > WINDOW_HEIGHT:
                    self.client_dict[spa] = {"position": [random.randint(10, WINDOW_WIDTH - 10), random.randint(-500, -20)]}
            try:
                self.client_dict['p1_score'] = p1_score
                self.client_dict['p2_score'] = p2_score
            except:
                pass
       
        #update spaghetti positions
        for spa in spaghetti_names:
            self.client_dict[spa] = {"position": [self.client_dict[spa]['position'][0] + .2, self.client_dict[spa]['position'][1] + 2]}
        timeLeft = timeLeft - (FPS/ 100)
        #update time
        self.client_dict['time'] = timeLeft
        #send off
        for c in self.factory.clients:
            c.message(json.dumps(self.client_dict))


    def message(self, message):
        self.transport.write(message + '\n')

def main():
    f = Factory()
    f.protocol = ChatClient
    f.clients = []
    print('Listening on 8000...')
    reactor.listenTCP(8000, f)
    reactor.run()

if __name__ == '__main__':
    main()
