
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


"""
An example client. Run simpleserv.py first before running this.
"""
from __future__ import print_function

import string
import time
import random

import urllib

import pyglet
import pygletreactor
pygletreactor.install()

import cocos
from cocos.scene import Scene
from cocos.layer import Layer, ColorLayer
from cocos import layer
from cocos.sprite import Sprite
from cocos.actions import *
from cocos.director import director

from pyglet.window.key import symbol_string

from twisted.protocols import basic
from twisted.internet import reactor, protocol
from twisted.internet.task import LoopingCall

from time import sleep
import math
import sys
import json

WINDOW_WIDTH = 700;
WINDOW_HEIGHT = 500;
OFFSET = 60
SPEED = 200

SPRITE_POS = '';

act = ''
connection = ''

IDENTIFIER = 0

class MoveGrossini(Move):
    global SPRITE_POS

    def step(self, dt):
        global SPRITE_POS

        super(MoveGrossini, self).step(dt)
        SPRITE_POS = self.target.position

class Actions(ColorLayer):
    is_event_handler = True
    sprite_vector = []
    sprite_data = {}

    def __init__(self):
        super(Actions, self).__init__(52, 152, 219, 1000)

        self.sprite = Sprite('grossini.png')
        self.sprite.position = OFFSET, WINDOW_HEIGHT - OFFSET
        self.sprite.velocity = 0, 0
        self.add(self.sprite)
        
        self.sprite_vector.append(self.sprite)
        self.sprite_vector.append(self.sprite)

        self.sprite_vector[IDENTIFIER] = self.sprite
    
        self.sprite.do(MoveGrossini())

    def on_key_press(self, key, modifiers):
        global SPEED
        global IDENTIFIER
        global connection

        if symbol_string(key) == "EQUAL":
            new_pos = [self.sprite.position[0] + 10, self.sprite.position[1]]
            self.sprite.position = tuple(new_pos)
            self.ping()
        elif symbol_string(key) == "MINUS":
            new_pos = [self.sprite.position[0] - 10, self.sprite.position[1]]
            self.sprite.position = tuple(new_pos)
            self.ping()
            

    def echo(self):
        print('Hello')

    def add_sprite(self, num):
        sprite_add = Sprite('grossini.png')
        sprite_add.position = 100, 100
        self.add(sprite_add)
        self.sprite_vector[num] = sprite_add

    def increment_sprites(self, packet):
        global IDENTIFIER

        print("ID", IDENTIFIER)

        self.packet_dict = json.loads(packet)
        print(self.packet_dict)   
        for el in self.packet_dict:
            if int(el) is not IDENTIFIER: 
                #print(int(el))
                self.sprite_vector[int(el)].position = tuple(self.packet_dict[el]['position'])

    def ping(self):
        print("PING")
        self.sprite_data["ID"] = IDENTIFIER
        self.sprite_data["position"] = self.sprite.position
        print(json.dumps(self.sprite_data))
        connection.transport.write(json.dumps(self.sprite_data) + '\n')


# a client protocol
class MarinaraClient(basic.LineReceiver):
    global act
    global IDENTIFIER
    m_INIT = True
    num_clients = 1;

    """Once connected, send a message, then print the result."""
    def connectionMade(self):
        global connection

        self.delimiter = '\n'
        connection = self

        print('Connection Made')

    def lineReceived(self, data):
        global IDENTIFIER

        if self.m_INIT:
            print("ID", str(data).rstrip())
            IDENTIFIER = int(str(data).rstrip())

            self.m_INIT = False
        else:
            self.add_client(data)

    def add_client(self, data):
        global IDENTIFIER

        packet = str(data).rstrip()
        packet_dict = json.loads(packet)
        if len(packet_dict) > self.num_clients:
            for el in packet_dict:
                if int(el) is not IDENTIFIER:
                    act.add_sprite(int(el))
                    self.num_clients += 1
                    print("ADD", el)
                    print("ID ADD", IDENTIFIER)
        else:
            act.increment_sprites(packet)

    def connectionLost(self, reason):
        print("connection lost")

 
class EchoFactory(protocol.ClientFactory):
    protocol = MarinaraClient

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        reactor.stop()


# this connects the protocol to a server runing on port 8000
def main():
    global act

    director.init(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    act = Actions()
    main_scene = cocos.scene.Scene(act)

    @director.window.event
    def on_close():
        reactor.stop()

    director.scene_stack.append(director.scene)
    director._set_scene(main_scene)   

    f = EchoFactory()
    reactor.connectTCP("localhost", 1025, f)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
