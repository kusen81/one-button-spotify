import sys
from gpiozero import Button
import spotipy
import spotipy.util as util
import time
import json
import subprocess
import os

Button.was_held = False

button_prev = Button(pin=9,hold_time=0.5,hold_repeat=0.2)
button_playpause = Button(pin=10,hold_time=0.5)
button_next = Button(pin=11,hold_time=0.5,hold_repeat=0.2)
button_visual = Button(pin=5,hold_time=0.5,hold_repeat=0.2)
button_volume = Button(pin=6,hold_time=0.5,hold_repeat=0.2)

username = 'xxxYourUserNamexxx'
password = 'xxxYourPasswordxxx'
playlist = 'xxxYourPlayListURIfromSpotifyxxx'
spotconnect_device_name = 'xxxYourTargetSpotifyConnectDeviceNamexxx'

SP_CLIENT_ID = 'xxxClientIDofYourAppxxx'
SP_CLIENT_SECRET = 'xxxClientSecretofYourAppxxx'
SP_REDIRECT_URI = 'http://localhost/'

global token
global playing
global device
global volume
global was_held
global pro
global visual_type
global visual_type_num

token = ''
playing = False
device = ''
scope = 'user-library-read, user-read-playback-state, user-modify-playback-state'
visual_type = ['scroll', 'energy', 'spectrum']
visual_type_num = 0

def spotStart():
    print('spotStart called')
    global token
    token = util.prompt_for_user_token(username, scope,client_id=SP_CLIENT_ID,client_secret=SP_CLIENT_SECRET,redirect_uri=SP_REDIRECT_URI)
    print('token created as ' + token)

def spotDevices():
    print('spotDevices called')
    global token
    global volume
    try:
        global device
        sp = spotipy.Spotify(auth=token)
        devices = sp.devices()
        print("devices:")
        print(devices)
        devices = devices['devices']
        print(devices)
        dictionary = {}
        for item in devices:
            dictionary[item['name']] = item['id']
        device = dictionary[spotconnect_device_name]
        print('device resolved as ' + device)
        volume = 50
        sp.volume(volume, device_id=device) # Set init volume
    except:
        # empty token
        print('something is not right - emptying token')
        token = ''
        spotStart()

def spotPlay():
    print('spotPlay called')
    global token
    global playing
    try:
        if playing:
            print('already playing - pause')
            sp = spotipy.Spotify(auth=token)
            sp.pause_playback(device_id=device)
            playing = False
            time.sleep(1)
        else:
            print('not playing - trying to start')
            sp = spotipy.Spotify(auth=token)
            sp.start_playback(device_id=device,context_uri=playlist)
            playing = True
            time.sleep(1)
    except:
        # empty token
        print('something is not right - emptying token')
        token = ''

def spotNext(button_next):
    print('spotNext called')
    global token
    global playing
    try:
        if not button_next.was_held:
            sp = spotipy.Spotify(auth=token)
            sp.next_track(device_id=device)
            playing = True
            time.sleep(1)
        button_next.was_held = False
    except Exception as e:
        # empty token
        print('something is not right - emptying token')
        print(e)
        token = ''

def spotPrev(button_prev):
    print('spotPrev called')
    global token
    global playing
    try:
        if not button_prev.was_held:
            sp = spotipy.Spotify(auth=token)
            sp.previous_track(device_id=device)
            playing = True
            time.sleep(1)
        button_prev.was_held = False
    except Exception as e:
        # empty token
        print('something is not right - emptying token')
        print(e)
        token = ''

def spotVisual(button_visual):
    print('spotVisual called')
    global pro
    global visual_type
    global visual_type_num

    os.system("sudo pkill -9 -P " + str(pro.pid))

    if visual_type_num == len(visual_type) - 1:
        visual_type_num = 0
    else:
        visual_type_num = visual_type_num + 1
    print("visual_type_num " + str(visual_type_num))
    pro = subprocess.Popen(['sudo', '/usr/bin/python3', '/home/pi/dancyPi-audio-reactive-led/python/visualization.py', visual_type[visual_type_num]], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    time.sleep(1)

def spotVolumeUp(button_volume):
    print('spotVolumeUp called')
    global token
    global playing
    global volume

    try:
        sp = spotipy.Spotify(auth=token)
        if volume == 100:
            volume = 5
        else:
            volume += 5

        sp.volume(volume, device_id=device)
    except:
        # empty token
        print('something is not right - emptying token')
        token = ''

pro = subprocess.Popen(['sudo', '/usr/bin/python3', '/home/pi/dancyPi-audio-reactive-led/python/visualization.py', visual_type[visual_type_num]], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
idle = 0

while True:
    if not token:
        spotStart()
        spotDevices()
    if idle == 14400: # roughly every hour (14400*0.25secs = 60 mins) empty token
        idle = 0
        token = ''
    else:
        idle += 1
        time.sleep(0.25)

    button_playpause.when_released = spotPlay
    button_prev.when_released = spotPrev
    button_volume.when_released = spotVolumeUp
    button_next.when_released = spotNext
    button_visual.when_released = spotVisual
