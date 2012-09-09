import echonest.audio as audio
import pyechonest.song as song
import pyechonest.artist as artist
import pyechonest.track as track
import heapq
import math
import random

import pyechonest.config as config

from mod_python import util

import types

def cosineSimilarity(a, b):
    dotProduct = 0
    aMagnitude = 0
    bMagnitude = 0
    for i in range(len(a)):
        dotProduct += (a[i] * b[i])
        aMagnitude += math.pow(a[i], 2)
        bMagnitude += math.pow(b[i], 2)
        
    aMagnitude = math.sqrt(aMagnitude)
    bMagnitude = math.sqrt(bMagnitude)
    
    return dotProduct / (aMagnitude * bMagnitude)

def getChordProgression(trackId):
    #trackId = track['id']
    #a = audio.AudioAnalysis('TRYFEYU12FCBF2409B')
    a = audio.AudioAnalysis(str(trackId))
    segmentLength = len(a.segments)
    
    binSize = 10
    prevChord = ""
    chordProgression = []
    
    for segmentIndex in range(segmentLength):
        
        avgChroma = []
        
        if segmentIndex % binSize == 0:
            for i in range(binSize):
                for chroma in range(12):
                    if len(avgChroma) < 12:
                        avgChroma.append(0)
                    
                    if segmentIndex + i < segmentLength: # Don't overflow
                        avgChroma[chroma] = avgChroma[chroma] + a.segments[segmentIndex + i].pitches[chroma]
                        #print segmentIndex, i, a.segments[segmentIndex + i].pitches[chroma]
            
            # normalize chroma vector - divide each by binSize
            for j in range(12):
                avgChroma[j] /= binSize;
            
            #print avgChroma
            
            # compute cosine similarity between average chroma vector and each chord in dictionary
            maxChordSim = 0
            maxChordName = ""
            maxChordMode = 0
            maxChordKey = 0
            for chordIndex in range(len(chords)):
                similarity = cosineSimilarity(avgChroma, chords[chordIndex]['vector'])
                
                if similarity > maxChordSim:
                    maxChordSim = similarity
                    maxChordName = chords[chordIndex]['name']
                    maxChordMode = chords[chordIndex]['mode']
                    maxChordKey = chords[chordIndex]['key']
                
                #print chords[chordIndex]['name'], similarity
            
            #print "CHORD: ", maxChordName, maxChordSim
            
            if prevChord != maxChordName:
                prevChord = maxChordName;
                chordProgression.append({'name' : maxChordName, 'mode':maxChordMode, 'key': maxChordKey, 'sim': round(maxChordSim, 2) })
            
            #print mark(avgChroma, 3)
            #print "---------"
        else:
            continue
        
    return chordProgression

apiKey = "OL6YCWFYQRBPXWNVO"
config.ECHO_NEST_API_KEY = apiKey

chords = [ {'name': "C", 'vector' :[1,0,0,0,1,0,0,1,0,0,0,0], 'key': 0, 'mode': 1 },
           #{'name': "C7", 'vector': [1,0,0,0,1,0,0,1,0,0,1,0], 'key': 0, 'mode': 1 },
           {'name': "Cm", 'vector':[1,0,0,1,0,0,0,1,0,0,0,0], 'key': 0, 'mode': 0 },
           {'name': "C#", 'vector' :[0,1,0,0,0,1,0,0,1,0,0,0], 'key': 1, 'mode': 1 },
           #{'name': "C#7", 'vector' :[0,1,0,0,0,1,0,0,1,0,0,1], 'key': 1, 'mode': 1 },
           {'name': "C#m", 'vector':[0,1,0,0,1,0,0,0,1,0,0,0], 'key': 1, 'mode': 0 },
           {'name': "D", 'vector' :[0,0,1,0,0,0,1,0,0,1,0,0],  'key': 2, 'mode': 1 },
           #{'name': "D7", 'vector' :[1,0,1,0,0,0,1,0,0,1,0,0],  'key': 2, 'mode': 1 },
           {'name': "Dm", 'vector':[0,0,1,0,0,1,0,0,0,1,0,0],  'key': 2, 'mode': 0 },
           {'name': "Eb", 'vector' :[0,0,0,1,0,0,0,1,0,0,1,0],  'key': 3, 'mode': 1 },
           #{'name': "Eb7", 'vector' :[0,1,0,1,0,0,0,1,0,0,1,0],  'key': 3, 'mode': 1 },
           {'name': "Ebm", 'vector':[0,0,0,1,0,0,1,0,0,0,1,0],  'key': 3, 'mode': 0 },
           {'name': "E", 'vector' :[0,0,0,0,1,0,0,0,1,0,0,1],  'key': 4, 'mode': 1 },
           #{'name': "E7", 'vector' :[0,0,1,0,1,0,0,0,1,0,0,1],  'key': 4, 'mode': 1 },
           {'name': "Em", 'vector':[0,0,0,0,1,0,0,1,0,0,0,1],  'key': 4, 'mode': 0 },
           {'name': "F", 'vector' :[1,0,0,0,0,1,0,0,0,1,0,0],  'key': 5, 'mode': 1 },
           #{'name': "F7", 'vector' :[1,0,0,1,0,1,0,0,0,1,0,0],  'key': 5, 'mode': 1 },
           {'name': "Fm", 'vector':[1,0,0,0,0,1,0,0,1,0,0,0],  'key': 5, 'mode': 0 },
           {'name': "F#", 'vector' :[0,1,0,0,0,0,1,0,0,0,1,0],  'key': 6, 'mode': 1 },
           #{'name': "F#7", 'vector' :[0,1,0,0,1,0,1,0,0,0,1,0],  'key': 6, 'mode': 1 },
           {'name': "F#m", 'vector':[0,1,0,0,0,0,1,0,0,1,0,0],  'key': 6, 'mode': 0 },
           {'name': "G", 'vector' :[0,0,1,0,0,0,0,1,0,0,0,1],  'key': 7, 'mode': 1 },
           #{'name': "G7", 'vector' :[0,0,1,0,0,1,0,1,0,0,0,1],  'key': 7, 'mode': 1 },
           {'name': "Gm", 'vector':[0,0,1,0,0,0,0,1,0,0,1,0],  'key': 7, 'mode': 0 },
           {'name': "Ab", 'vector' :[1,0,0,1,0,0,0,0,1,0,0,0],  'key': 8, 'mode': 1 },
           #{'name': "Ab7", 'vector' :[1,0,0,1,0,0,1,0,1,0,0,0],  'key': 8, 'mode': 1 },
           {'name': "Abm", 'vector':[0,0,0,1,0,0,0,0,1,0,0,1],  'key': 8, 'mode': 0 },
           {'name': "A", 'vector' :[0,1,0,0,1,0,0,0,0,1,0,0],  'key': 9, 'mode': 1 },
           #{'name': "A7", 'vector' :[0,1,0,0,1,0,0,1,0,1,0,0],  'key': 9, 'mode': 1 },
           {'name': "Am", 'vector':[1,0,0,0,1,0,0,0,0,1,0,0],  'key': 9, 'mode': 0 },
           {'name': "Bb", 'vector' :[0,0,1,0,0,1,0,0,0,0,1,0],  'key': 10, 'mode': 1 },
           #{'name': "Bb7", 'vector' :[0,0,1,0,0,1,0,0,1,0,1,0],  'key': 10, 'mode': 1 },
           {'name': "Bbm", 'vector':[0,1,0,0,0,1,0,0,0,0,1,0],  'key': 10, 'mode': 0 },
           {'name': "B", 'vector' :[0,0,0,1,0,0,1,0,0,0,0,1],  'key': 11, 'mode': 1 },
           #{'name': "B7", 'vector' :[0,0,0,1,0,0,1,0,0,1,0,1],  'key': 11, 'mode': 1 },
           {'name': "Bm", 'vector':[0,0,1,0,0,0,1,0,0,0,0,1],  'key': 11, 'mode': 0 }
          ]

def index(req):
    
    s = ""
    
    s += "<!DOCTYPE html>"
    
    s += "<html>"
    s += "<head>"
    s += "<title>Harmony Generated Playlist</title>"
    s += "<link rel='stylesheet' type='text/css' href='main.css'>"
    s += "</head>"
    s += "<body>"
    
    s += "<div id='header'>"
    s += "<h1>Chord Progression Estimator</h1>"
    s += "<a href='http://the.echonest.com'><img src='en-powered.gif' alt='Powered by the Echo Nest' /></a><br />"
    s += "</div>"
        
    form = util.FieldStorage(req, keep_blank_values=1)
    trackId = form.getfirst("trackid")
    
    # User can pass in either trackid or artist and song
    
    if isinstance(trackId, types.NoneType):
        trackId = "TRWQINA128F9339E57"
        
    artist = form.getfirst("artist")
    songTitle = form.getfirst("song")
    
    sim = form.getfirst("sim") # display similarity output
    if isinstance(sim, types.NoneType):
        sim = "0"
    
    if isinstance(artist, types.StringType):
        songResult = song.search(artist=artist, title=songTitle, buckets=["tracks","id:7digital"], limit="true")
        
        # Get first match
        trackId = songResult[0].get_tracks("7digital")[0]['id']
    
    #s += artist + "<br />"
    #s += songTitle + "<br />"
    # Get track info
    t = track._profile({'id' : trackId});

    s += t.title + " by " + t.artist + "<br />"
    
    # Print chord progression
    s += "<br />"
    s += "Chord Progression: "
    
    chordProgression = getChordProgression(trackId)
    s += "<div id='chord-progression'>"
    
    for i in range(len(chordProgression)):
        s += chordProgression[i]['name']
        
        if sim == "1":
            s += "<small>(" + str(chordProgression[i]['sim'] * 100) + "% )</small>"
        
        if i != len(chordProgression) - 1:
            s += " - "
    
    s += "</div>"
   
    s += "</body>"
    s += "</html>"
    return s
