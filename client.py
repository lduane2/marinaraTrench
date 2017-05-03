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


#these are the imports for pyglet

import pyglet
import pygletreactor
pygletreactor.install()

#these are the imports for cocos

import cocos
from cocos.scene import Scene
from cocos.layer import Layer, ColorLayer
from cocos import layer
from cocos.sprite import Sprite
from cocos.actions import *
from cocos.director import director
from cocos.scenes import FadeTransition
from cocos.text import Label

#these are the imports for pyglet window

from pyglet.window import key
from pyglet.window.key import symbol_string

#these are the imports for twisted

from twisted.protocols import basic
from twisted.internet import reactor, protocol
from twisted.internet.task import LoopingCall




from time import sleep
import math
import sys
import json


#global variable declararions

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

class MoveSubmarine(Move):  # the movement of the subamrine
    global SPRITE_POS

    sprite_data = {}
    def step(self, dt):
        global SPRITE_POS
        global connection
        if keys[key.RIGHT]:  # if the right key is down 
            #print ("RIGHT")
            new_pos = [self.target.position[0] + 3, self.target.position[1]]   # creat new position
            if new_pos[0] < WINDOW_WIDTH:
                self.target.position = tuple(new_pos)  # move to new position if in bounds
            try:
                self.ping()  # send location to servr
            except:
                pass
        if keys[key.LEFT]:
            #print ("LEFT")
            new_pos = [self.target.position[0] - 3, self.target.position[1]] # creat new position
            if new_pos[0] > 0:
                self.target.position = tuple(new_pos)  # move to new position if in bounds
            try:
                self.ping()  # send location to servr
            except:
                pass
	if keys[key.UP]:
            #print ("UP")
            new_pos = [self.target.position[0], self.target.position[1] + 3]   # creat new position
            if new_pos[1] < WINDOW_HEIGHT:
                self.target.position = tuple(new_pos)	 # move to new position if in bounds
            try:
                self.ping()  # send location to servr
            except:
                pass
        if keys[key.DOWN]:
            #print ("DOWN")
            new_pos = [self.target.position[0], self.target.position[1] - 3]   # creat new position
            if new_pos[1] > 0:
                self.target.position = tuple(new_pos)  # move to new position if in bounds
            try:
	        self.ping()  # send location to servr
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

class MoveBubbles(Move):  # moves the bubles
    def step(self, dt):
        if self.target.position[1] > WINDOW_HEIGHT:  # if the bubble is outside the view of the screen
            self.target.position = random.randint(10, WINDOW_WIDTH -1), -20  # move it to a random position beow the screen
        self.target.velocity = (1 , 20 )  #sets the velocity
        super(MoveBubbles, self).step(dt) # makes it do it again

        
class MoveSpaghetti(Move):
    def step(self, dt):  # helps with the movement of the spaghetti
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





        
        self.target.velocity = (0, 0)  # sets the velocity equal to zero
        super(MoveSpaghetti, self).step(dt) 



class Actions(ColorLayer):  # represents the actions taht can take place on the main layer
    is_event_handler = True
    sprite_vector = {}
    sprite_data = {}

    def step(self, dt):   #testing the step fnciton
	print ("pease")

    def __init__(self): # initialze
        super(Actions, self).__init__(52, 152, 219, 1000)

	beatlesMusic = pyglet.media.load('yelloSub.wav', streaming=False)
	beatlesMusic.play()  # load and play the music
        self.sprite = Sprite('sub1.png')  # load and establish the sprite
        self.sprite.position = OFFSET, WINDOW_HEIGHT - OFFSET
        self.sprite.velocity = 0, 0
        self.add(self.sprite)
        self.spaghetti = {} 
        self.make_spaghetti() # make the spagetti
        self.bubbles = {}
        self.make_bubbles()  # make the bubbles
        #making the seaweed
        self.seaweed = Sprite('seaweed.png')
        self.seaweed.position = WINDOW_WIDTH / 2 - 15, 0
        self.add(self.seaweed)
        
        #set up the subs
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

        #set the update loop
        self.updateLoop = LoopingCall(self.update_client)
        self.updateLoop.start(1.0)


    def on_key_press(self, keyPress, modifiers):  # when input is recieved from the keyboard
        global SPEED
        global IDENTIFIER
        global connection
        global keys

        while keys[key.RIGHT]:   #this ia how we used to program the movement of the sub, but the updated movement is now above
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
    

    def echo(self): # another test function
        print('Hello')

    def make_spaghetti(self):  # initializes the spagett
        global spaghetti_names

        #print('\ntryna cook up some spaghetti\n')
        for i in spaghetti_names:  # place all of the spagetti
            #print(self.spaghetti)
            random.seed()
            self.new_sprite = Sprite('spaghetti.png')
            #self.new_sprite.position = random.randint(10, WINDOW_WIDTH - 10), random.randint(-500, -20)
            self.new_sprite.position = -100, -100
            #self.new_sprite.velocity = random.randint(-30, 30), random.randint(20, 40)
            self.new_sprite.do(MoveSpaghetti())  # move the spagetti
            self.add(self.new_sprite)
            self.spaghetti[i] = self.new_sprite # add the spagetti to the array of sprites

    def make_bubbles(self):  # makes bubbles
	bubbleCount = 10
        for i in range(bubbleCount): # make a specific amount of bubbles
            random.seed()
            self.new_sprite = Sprite('bubb.png')
            self.new_sprite.position = random.randint(10, WINDOW_WIDTH - 10), random.randint(-500, -20) #  set position
            #self.new_sprite.position = -100, -100
            self.new_sprite.velocity = random.randint(-30, 30), 1  # set velocity of the bubbles
            self.new_sprite.do(MoveBubbles())
            self.add(self.new_sprite)
            self.bubbles[i] = self.new_sprite  # add them to the array

    def add_sprite(self, num):  # add the oponent sub
        sprite_add = Sprite('sub2.png') # 
        sprite_add.position = -100, -100 # set its positions
        self.add(sprite_add)
        self.sprite_vector[num] = sprite_add  # add the sprite to the array 

    def increment_sprites(self, packet):  # changes the position of the sprites
        global transition
        global spaghetti_names
        global IDENTIFIER
        global timeLeft
        global p1_score, p2_score

        #print("ID", IDENTIFIER)

        self.packet_dict = json.loads(packet)  # receieve the json from the server
        timeLeft = self.packet_dict['time']   #unpack it and edit the global gamestate
        p1_score = self.packet_dict['p1_score']
        p2_score = self.packet_dict['p2_score']
        if int(timeLeft) == 0 and not transition:  #  if the game is over
            #print ("Negative")
            transition = True
            timeLeft = -1            
            #self.updateLoop.stop()
            director.replace(FadeTransition(Scene(endLayer())))  # transition to the game over screen 
            #reactor.stop()
        if int(timeLeft) < 0:  # stop looping if the time is negative
            return        
#self.updateLoop.end()
        #print(self.packet_dict)   
        for el in self.packet_dict:  # use the information from the server to update the position of the spagetti
            if el != IDENTIFIER and el in ["client0", "client1"]:
                #print(el)
                self.sprite_vector[el].position = tuple(self.packet_dict[el]['position'])
            if el in spaghetti_names:
                self.spaghetti[el].position = tuple(self.packet_dict[el]['position'])
        
    def ping(self):  # send data to the server
        #print("PING")
        self.sprite_data["ID"] = IDENTIFIER  # send which player you are
        self.sprite_data["position"] = self.sprite.position  # send your position
        #print(json.dumps(self.sprite_data))
        try:
            connection.transport.write(json.dumps(self.sprite_data) + '\n') # send it across the web
        except:
            pass


# a client protocol
class MarinaraClient(basic.LineReceiver):  # inherent the client from the basic line receiver class
    global act
    global IDENTIFIER
    m_INIT = True
    num_clients = 11;

    """Once connected, send a message, then print the result."""
    def connectionMade(self):  # if the connection is successful
        global connection

        self.delimiter = '\n'
        connection = self

        print('Connection Made')  # let the user know the connection was successful

    def lineReceived(self, data):  # when you recieve a line formt he server
        global IDENTIFIER

        if self.m_INIT: 
            #print("ID", str(data).rstrip())
            IDENTIFIER = str(data).rstrip()  # initialize yourself

            self.m_INIT = False
        else:
            self.add_client(data) # otherwise add the second client data

    def add_client(self, data): # add the second client 
        global IDENTIFIER

        packet = str(data).rstrip()
        packet_dict = json.loads(packet) # load the pack from the server
        if len(packet_dict) > self.num_clients:
            for el in packet_dict:  # unpack the information form the server
                if el != IDENTIFIER and el in ["client0", "client1"]:
                    act.add_sprite(el)
                    self.num_clients += 1
                    #print("ADD", el)
                    #print("ID ADD", IDENTIFIER)
        else:
            act.increment_sprites(packet)

    def connectionLost(self, reason):  # report errors to command line
        print("connection lost")

 
class EchoFactory(protocol.ClientFactory):  # the echo factory client 
    protocol = MarinaraClient

    def clientConnectionFailed(self, connector, reason):  # if the connection fails
        print("Connection failed - goodbye!")     # print an error message and end the program 
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason): # if the connection is lost
        print("Connection lost - goodbye!")   # print an error message and stop the program


        reactor.stop()


class endLayer(ColorLayer):   # the layer for the end of game screen 
    is_event_handler =True
    
    def __init__(self):
        global p2_score # accesses the score for both players to display it in the final message
        global p1_score
        super(endLayer, self).__init__(52, 152, 219, 1000)    # initialize this layer with the same conditions as the previous one
        #text = Label("You Won!")
        print (IDENTIFIER)  #print diagnostic info so we know which player this is
        score = 0        
        opScore = -1
        if IDENTIFIER == "client1": # if you are the first, assign the score appropraitely 
            score = p2_score
            opScore = p1_score
	else:  # otherwise, flip flop the score values
            score = p1_score
	    opScore = p2_score
        message = "You Lost.  Try Again Next Time!"  # set the losing message
        if score > opScore:
            message = "You Won, Congrats!"  # but overwrite it if your score was better
        
        
        #print ("we did it patrick, we saved the city")
        text = Label(message) # create a label with your victory / loss message
	text2 = Label("Your Score: " +str(score) + " Opponent Score: " + str(opScore) ) # create another label with the player scores

        text2.position = director._window_virtual_width / 4, (director._window_virtual_height / 2) -30 #place the two different text labels

        text.position = director._window_virtual_width / 4, director._window_virtual_height / 2

        self.add(text) # add the text to the scenen
        self.add(text2)





# this connects the protocol to a server runing on port 8000
def main():
    global act
    global keys
    if len(sys.argv) != 3: # parses the arguments 
        print("usage: python client.py <server address> <port>")
        exit(1)
    director.init(width=WINDOW_WIDTH, height=WINDOW_HEIGHT) # initialoize the director
    keys = key.KeyStateHandler() # store the keyboard state to allow movment 
    cocos.director.director.window.push_handlers(keys) # let the window understand the keystate
    act = Actions() 
    main_scene = cocos.scene.Scene(act) # initialize and push the scene 

    @director.window.event
    def on_close(): #stop the reactor when the window closes
        reactor.stop()

    director.scene_stack.append(director.scene) # set up the first scene
    director._set_scene(main_scene)   

    f = EchoFactory() # set up the networking
    reactor.connectTCP(sys.argv[1], int(sys.argv[2]), f)
    reactor.run()  # begin the reacotr

# this only runs if the module was *not* imported
if __name__ == '__main__': # starts the client
    main()
