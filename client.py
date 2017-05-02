#!/usr/bin/env python

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

from pyglet.window import key
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
color = (52, 152, 219)

SPRITE_POS = '';
keys = ''
score = 0
it_count = 0

act = ''
connection = ''
num_spaghetti = 10

IDENTIFIER = 0

class MoveSubmarine(Move):
    global SPRITE_POS

    def step(self, dt):
        global SPRITE_POS

        super(MoveSubmarine, self).step(dt)
        SPRITE_POS = self.target.position

class MoveSpaghetti(Move):
    def step(self, dt):
        global SPRITE_POS
        global score
        pos = self.target.position
        
        #Collision Detection
        if SPRITE_POS[0] > pos[0] - 10 and SPRITE_POS[0] < pos[0] + 10 and SPRITE_POS[1] > pos[1] - 10 and SPRITE_POS[1] < pos[1] + 10:
            print('COLLISION!')
            score = score + 1
            self.target.position = random.randint(10, WINDOW_WIDTH - 10), random.randint(-500, -20)

        #Off Screen Detection
        if pos[1] >  WINDOW_HEIGHT:
            self.target.position = random.randint(10, WINDOW_WIDTH - 10), -20
        
        self.target.velocity = (1, 20)
        super(MoveSpaghetti, self).step(dt)



class Actions(ColorLayer):
    is_event_handler = True
    sprite_vector = []
    sprite_data = {}

    def __init__(self):
        super(Actions, self).__init__(52, 152, 219, 1000)

        self.sprite = Sprite('sub1.png')
        self.sprite.position = OFFSET, WINDOW_HEIGHT - OFFSET
        self.sprite.velocity = 0, 0
        self.add(self.sprite)
        self.spaghetti = []
        self.make_spaghetti()
        #making the seaweed
        self.seaweed = Sprite('seaweed.png')
        self.seaweed.position = WINDOW_WIDTH / 2 - 15, 0
        self.add(self.seaweed)
        
        self.sprite_vector.append(self.sprite)
        self.sprite_vector.append(self.sprite)

        self.sprite_vector[IDENTIFIER] = self.sprite
    
        self.sprite.do(MoveSubmarine())
        
        
    def on_key_press(self, keyPress, modifiers):
        global SPEED
        global IDENTIFIER
        global connection
        global keys
        self.update_color()
        
        if symbol_string(keyPress) == "D":
            new_pos = [self.sprite.position[0] + 10, self.sprite.position[1]]
            if new_pos[0] < WINDOW_WIDTH:
                self.sprite.position = tuple(new_pos)
            self.ping()
        elif symbol_string(keyPress) == "A":
            new_pos = [self.sprite.position[0] - 10, self.sprite.position[1]]
            if new_pos[0] > 0:
                self.sprite.position = tuple(new_pos)
            self.ping()
        elif symbol_string(keyPress) == "S":
            new_pos = [self.sprite.position[0], self.sprite.position[1] - 10]
            if new_pos[1] > 0:
                self.sprite.position = tuple(new_pos)
            self.ping()
        elif symbol_string(keyPress) == "W":
            new_pos = [self.sprite.position[0], self.sprite.position[1] + 10]
            if new_pos[1] < WINDOW_HEIGHT:
                self.sprite.position = tuple(new_pos)
            self.ping()
    
    def update_color(self):
        '''updates global variable for color and also self.color'''
        global color
        r = color[0] - .333
        g = color[1] - 1
        b = color[2] 
        if r < 0: r = 0
        if g < 0: g = 0
        if b < 0: b = 0
        if r > 255: r = 255
        if g > 255: g = 255
        if b > 255: b = 255
        color = (r, g, b)
        self.color = color
            

    def echo(self):
        print('Hello')

    def make_spaghetti(self):
        print('\ntryna cook up some spaghetti\n')
        for i in range(num_spaghetti):
            random.seed()
            self.new_sprite = Sprite('spaghetti.png')
            self.new_sprite.position = random.randint(10, WINDOW_WIDTH - 10), random.randint(-500, -20)
            self.new_sprite.velocity = random.randint(-30, 30), random.randint(20, 40)
            self.new_sprite.do(MoveSpaghetti())
            self.add(self.new_sprite)
            self.spaghetti.append(self.new_sprite)


    def add_sprite(self, num):
        sprite_add = Sprite('sub2.png')
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
    global keys

    director.init(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    keys = key.KeyStateHandler()
    cocos.director.director.window.push_handlers(keys)
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
