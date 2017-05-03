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
from cocos.scenes import FadeTransition
from cocos.text import Label


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
timeLeft = 60
p1_score = 0
p2_score = 0


transition = False



act = ''
connection = ''
num_spaghetti = 10

IDENTIFIER = ''

spaghetti_names = ["spaghetti0", "spaghetti1", "spaghetti2", "spaghetti3", "spaghetti4", "spaghetti5", "spaghetti6", "spaghetti7", "spaghetti8", "spaghetti9"]

class MoveSubmarine(Move):
    global SPRITE_POS

    sprite_data = {}
    def step(self, dt):
        global SPRITE_POS
        global connection
        if keys[key.RIGHT]:
            #print ("RIGHT")
            new_pos = [self.target.position[0] + 3, self.target.position[1]]
            if new_pos[0] < WINDOW_WIDTH:
                self.target.position = tuple(new_pos)
            try:
                self.ping()
            except:
                pass
        if keys[key.LEFT]:
            #print ("LEFT")
            new_pos = [self.target.position[0] - 3, self.target.position[1]]
            if new_pos[0] > 0:
                self.target.position = tuple(new_pos)
            try:
                self.ping()
            except:
                pass
	if keys[key.UP]:
            #print ("UP")
            new_pos = [self.target.position[0], self.target.position[1] + 3]
            if new_pos[1] < WINDOW_HEIGHT:
                self.target.position = tuple(new_pos)	
            try:
                self.ping()
            except:
                pass
        if keys[key.DOWN]:
            #print ("DOWN")
            new_pos = [self.target.position[0], self.target.position[1] - 3]
            if new_pos[1] > 0:
                self.target.position = tuple(new_pos)
            try:
	        self.ping()
            except:
                pass
	#print (self.target.sprite_data)


        super(MoveSubmarine, self).step(dt)
        SPRITE_POS = self.target.position

    def ping(self):
	print ("PINPG")
        global connection
        self.sprite_data["ID"] = IDENTIFIER
        self.sprite_data["position"] = self.target.position
        #print(json.dumps(self.sprite_data))
        connection.transport.write(json.dumps(self.sprite_data) + '\n')

class MoveBubbles(Move):
    def step(self, dt):
        if self.target.position[1] > WINDOW_HEIGHT:
            self.target.position = random.randint(10, WINDOW_WIDTH -1), -20
        self.target.velocity = (1 , 20 )
        super(MoveBubbles, self).step(dt)

        
class MoveSpaghetti(Move):
    def step(self, dt):
        global SPRITE_POS
        global score

        
        #Collision Detection
        '''
        if SPRITE_POS[0] > pos[0] - 10 and SPRITE_POS[0] < pos[0] + 10 and SPRITE_POS[1] > pos[1] - 10 and SPRITE_POS[1] < pos[1] + 10:
            print('COLLISION!')
            score = score + 1
            #self.target.position = random.randint(10, WINDOW_WIDTH - 10), random.randint(-500, -20)
        '''

        #Off Screen Detection
        #if pos[1] >  WINDOW_HEIGHT:
            #self.target.position = random.randint(10, WINDOW_WIDTH - 10), -20





        
        self.target.velocity = (0, 0)
        super(MoveSpaghetti, self).step(dt)



class Actions(ColorLayer):
    is_event_handler = True
    sprite_vector = {}
    sprite_data = {}

    def step(self, dt):
	print ("pease")

    def __init__(self):
        super(Actions, self).__init__(52, 152, 219, 1000)

	beatlesMusic = pyglet.media.load('yelloSub.wav', streaming=False)
	beatlesMusic.play()
        self.sprite = Sprite('sub1.png')
        self.sprite.position = OFFSET, WINDOW_HEIGHT - OFFSET
        self.sprite.velocity = 0, 0
        self.add(self.sprite)
        self.spaghetti = {}
        self.make_spaghetti()
        self.bubbles = {}
        self.make_bubbles()
        #making the seaweed
        self.seaweed = Sprite('seaweed.png')
        self.seaweed.position = WINDOW_WIDTH / 2 - 15, 0
        self.add(self.seaweed)
        
        self.sprite_vector["client0"] = self.sprite
        self.sprite_vector["client1"] = self.sprite
        self.sprite.do(MoveSubmarine())

        #create time and update color/time
        self.label = cocos.text.Label('Time Remaining: {} s'.format(int(timeLeft)), font_name='Comic Sans', font_size=12, anchor_x='center', anchor_y='center')
        self.label.position = WINDOW_WIDTH - 100, WINDOW_HEIGHT - 20
        self.add(self.label)

        #Score labels
        self.scores = cocos.text.Label('P1: {}    P2: {}'.format(p1_score, p2_score),font_name='Comic Sans', font_size=12, anchor_x='center', anchor_y='center')
        self.scores.position = 50, WINDOW_HEIGHT - 20
        self.add(self.scores)

        self.updateLoop = LoopingCall(self.update_client)
        self.updateLoop.start(1.0)


    def on_key_press(self, keyPress, modifiers):
        global SPEED
        global IDENTIFIER
        global connection
        global keys

        while keys[key.RIGHT]:
            print ("key is down")
            new_pos = [self.sprite.position[0] + 10, self.sprite.position[1]]
            if new_pos[0] < WINDOW_WIDTH:
                self.sprite.position = tuple(new_pos)
            self.ping()
            break

    
    def update_client(self):
        '''updates global variables'''
        global color, timeLeft, p1_score, p2_score
        #updates color
        r = color[0] - .666
        g = color[1] - 2
        b = color[2] 
        if r < 0: r = 0
        if g < 0: g = 0
        if b < 0: b = 0
        if r > 255: r = 255
        if g > 255: g = 255
        if b > 255: b = 255
        color = (r, g, b)
        self.color = color
        #updates time remaingin
        self.remove(self.label)
        self.label = cocos.text.Label('Time Remaining: {} s'.format(int(timeLeft)), font_name='Comic Sans', font_size=12, anchor_x='center', anchor_y='center')
        self.label.position = WINDOW_WIDTH - 100, WINDOW_HEIGHT - 20
        self.add(self.label)
        #updates scores
        self.remove(self.scores)
        self.scores = cocos.text.Label('P1: {}\tP2: {}'.format(p1_score, p2_score),font_name='Comic Sans', font_size=12, anchor_x='center', anchor_y='center')
        self.scores.position = 50, WINDOW_HEIGHT - 20
        self.add(self.scores)
    

    def echo(self):
        print('Hello')

    def make_spaghetti(self):
        global spaghetti_names

        #print('\ntryna cook up some spaghetti\n')
        for i in spaghetti_names:
            #print(self.spaghetti)
            random.seed()
            self.new_sprite = Sprite('spaghetti.png')
            #self.new_sprite.position = random.randint(10, WINDOW_WIDTH - 10), random.randint(-500, -20)
            self.new_sprite.position = -100, -100
            #self.new_sprite.velocity = random.randint(-30, 30), random.randint(20, 40)
            self.new_sprite.do(MoveSpaghetti())
            self.add(self.new_sprite)
            self.spaghetti[i] = self.new_sprite

    def make_bubbles(self):
	bubbleCount = 10
        for i in range(bubbleCount):
            random.seed()
            self.new_sprite = Sprite('bubb.png')
            self.new_sprite.position = random.randint(10, WINDOW_WIDTH - 10), random.randint(-500, -20)
            #self.new_sprite.position = -100, -100
            self.new_sprite.velocity = random.randint(-30, 30), 1
            self.new_sprite.do(MoveBubbles())
            self.add(self.new_sprite)
            self.bubbles[i] = self.new_sprite

    def add_sprite(self, num):
        sprite_add = Sprite('sub2.png')
        sprite_add.position = -100, -100
        self.add(sprite_add)
        self.sprite_vector[num] = sprite_add

    def increment_sprites(self, packet):
        global transition
        global spaghetti_names
        global IDENTIFIER
        global timeLeft
        global p1_score, p2_score

        #print("ID", IDENTIFIER)

        self.packet_dict = json.loads(packet)
        timeLeft = self.packet_dict['time']
        p1_score = self.packet_dict['p1_score']
        p2_score = self.packet_dict['p2_score']
        if int(timeLeft) == 0 and not transition:
            #print ("Negative")
            transition = True
            timeLeft = -1            
            #self.updateLoop.stop()
            director.replace(FadeTransition(Scene(endLayer())))
            #reactor.stop()
        if int(timeLeft) < 0:
            return        
#self.updateLoop.end()
        #print(self.packet_dict)   
        for el in self.packet_dict:
            if el != IDENTIFIER and el in ["client0", "client1"]:
                #print(el)
                self.sprite_vector[el].position = tuple(self.packet_dict[el]['position'])
            if el in spaghetti_names:
                self.spaghetti[el].position = tuple(self.packet_dict[el]['position'])
        
    def ping(self):
        #print("PING")
        self.sprite_data["ID"] = IDENTIFIER
        self.sprite_data["position"] = self.sprite.position
        #print(json.dumps(self.sprite_data))
        connection.transport.write(json.dumps(self.sprite_data) + '\n')


# a client protocol
class MarinaraClient(basic.LineReceiver):
    global act
    global IDENTIFIER
    m_INIT = True
    num_clients = 11;

    """Once connected, send a message, then print the result."""
    def connectionMade(self):
        global connection

        self.delimiter = '\n'
        connection = self

        print('Connection Made')

    def lineReceived(self, data):
        global IDENTIFIER

        if self.m_INIT:
            #print("ID", str(data).rstrip())
            IDENTIFIER = str(data).rstrip()

            self.m_INIT = False
        else:
            self.add_client(data)

    def add_client(self, data):
        global IDENTIFIER

        packet = str(data).rstrip()
        packet_dict = json.loads(packet)
        if len(packet_dict) > self.num_clients:
            for el in packet_dict:
                if el != IDENTIFIER and el in ["client0", "client1"]:
                    act.add_sprite(el)
                    self.num_clients += 1
                    #print("ADD", el)
                    #print("ID ADD", IDENTIFIER)
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


class endLayer(ColorLayer):
    is_event_handler =True
    
    def __init__(self):
        global p2_score
        global p1_score
        super(endLayer, self).__init__(52, 152, 219, 1000)    
        #text = Label("You Won!")
        print (IDENTIFIER)
        score = 0        
        opScore = -1
        if IDENTIFIER == "client1":
            score = p2_score
            opScore = p1_score
	else:
            score = p1_score
	    opScore = p2_score
        message = "You Lost.  Try Again Next Time!"
        if score > opScore:
            message = "You Won, Congrats!"
        
        
        #print ("we did it patrick, we saved the city")
        text = Label(message)
	text2 = Label("Your Score: " +str(score) + " Opponent Score: " + str(opScore) )

        text2.position = director._window_virtual_width / 4, (director._window_virtual_height / 2) -30

        text.position = director._window_virtual_width / 4, director._window_virtual_height / 2

        self.add(text)
        self.add(text2)





# this connects the protocol to a server runing on port 8000
def main():
    global act
    global keys
    if len(sys.argv) != 3:
        print("usage: python client.py <server address> <port>")
        exit(1)
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
    reactor.connectTCP(sys.argv[1], int(sys.argv[2]), f)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
