import sys
from gpiozero import Button
import spotipy
import spotipy.util as util
import time
import json

Button.was_held = False

button_prev = Button(pin=9,hold_time=0.5,hold_repeat=0.2)
button_playpause = Button(pin=10,hold_time=0.5)
button_next = Button(pin=11,hold_time=0.5,hold_repeat=0.2)

username = ''
password = ''
playlist = ''

spotconnect_device_name = ''

SP_CLIENT_ID = ''
SP_CLIENT_SECRET = ''
SP_REDIRECT_URI = 'http://localhost/'

global token
global playing
global device
global volume
global was_held

token = ''
playing = False
device = ''
scope = 'user-library-read, user-read-playback-state, user-modify-playback-state'

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
        devices = devices['devices']
        print(devices)
        dictionary = {}
        for item in devices:
            dictionary[item['name']] = item['id']
        device = dictionary[spotconnect_device_name]
        print('device resolved as ' + device)
        volume = 20
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
            # if we're already playing, pause
            sp = spotipy.Spotify(auth=token)
            #sp.next_track()
            sp.pause_playback(device_id=device)
            playing = False
            time.sleep(1)
        else:
            # if we're not playing, play the playlist, turn on shuffle and skip to a new (random) track
            print('not playing - trying to start')
            sp = spotipy.Spotify(auth=token)
            #sp.shuffle(False)
            sp.start_playback(device_id=device,context_uri=playlist)
            #sp.next_track()
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

def spotVolumeUp(button_next):
    print('spotVolumeUp called')
    global token
    global playing
    global volume
    button_next.was_held = True

    try:
        sp = spotipy.Spotify(auth=token)
        if not volume == 100:
            volume += 5
            sp.volume(volume, device_id=device)
        #time.sleep(0.2)
    except:
        # empty token
        print('something is not right - emptying token')
        token = ''

def spotVolumeDown():
    print('spotVolumeDown called')
    global token
    global playing
    global volume
    button_prev.was_held = True

    try:
        sp = spotipy.Spotify(auth=token)
        if not volume == 0:
            volume -= 5
            sp.volume(volume, device_id=device)
        #time.sleep(0.2)
    except:
        # empty token
        print('something is not right - emptying token')
        token = ''


'''
def spotStop():
    print('spotStop called')
    global token
    global playing
    try:
        if playing:
            # stop(pause) playing
            print('currently playing - trying to stop')
            sp = spotipy.client.Spotify(auth=token)
            sp.pause_playback()
            playing = False
            time.sleep(1)
        else:
            # if not playing, do nothing
            print('not playing - doing nothing')
            pass
    except:
        # empty token
        print('something is not right - emptying token')
        token = ''
'''

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
        #time.sleep(0.25)

    button_playpause.when_released = spotPlay
    button_prev.when_held = spotVolumeDown
    button_prev.when_released = spotPrev
    button_next.when_held = spotVolumeUp
    button_next.when_released = spotNext

'''
try:
    do_something()
except spotipy.client.SpotifyException:
    # re-authenticate when token expires
    token = ...
    sp = spotipy.Spotify(auth=token)
    do_something()
'''
