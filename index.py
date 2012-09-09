import echonest.audio as audio
import pyechonest.song as song
import pyechonest.artist as artist
import heapq
import math
import random

import pyechonest.config as config

import types

from cgi import parse_qs, escape

# Procedure
# Given: Artist
# - Select random song with track info from artist catalog
# - Compute chroma vector averages (moving average approach)
# - Compute harmonic progression (cosine similarity among chroma vectors)
# - For each chord, search for one sing that:
# - - Is by a similar artist
# - - Has same key and mode as chord (ex: chord = Am -> Key of A minor)

apiKey = "OL6YCWFYQRBPXWNVO"
config.ECHO_NEST_API_KEY = apiKey

catalog = "7digital-US"
catalogId = "id:7digital-US"

keys = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

chords = [ {'name': "C", 'vector' :[1,0,0,0,1,0,0,1,0,0,0,0], 'key': 0, 'mode': 1 },
           {'name': "Cm", 'vector':[1,0,0,1,0,0,0,1,0,0,0,0], 'key': 0, 'mode': 0 },
           {'name': "C#", 'vector' :[0,1,0,0,0,1,0,0,1,0,0,0], 'key': 1, 'mode': 1 },
           {'name': "C#m", 'vector':[0,1,0,0,1,0,0,0,1,0,0,0], 'key': 1, 'mode': 0 },
           {'name': "D", 'vector' :[0,0,1,0,0,0,1,0,0,1,0,0],  'key': 2, 'mode': 1 },
           {'name': "Dm", 'vector':[0,0,1,0,0,1,0,0,0,1,0,0],  'key': 2, 'mode': 0 },
           {'name': "Eb", 'vector' :[0,0,0,1,0,0,0,1,0,0,1,0],  'key': 3, 'mode': 1 },
           {'name': "Ebm", 'vector':[0,0,0,1,0,0,1,0,0,0,1,0],  'key': 3, 'mode': 0 },
           {'name': "E", 'vector' :[0,0,0,0,1,0,0,0,1,0,0,1],  'key': 4, 'mode': 1 },
           {'name': "Em", 'vector':[0,0,0,0,1,0,0,1,0,0,0,1],  'key': 4, 'mode': 0 },
           {'name': "F", 'vector' :[1,0,0,0,0,1,0,0,0,1,0,0],  'key': 5, 'mode': 1 },
           {'name': "Fm", 'vector':[1,0,0,0,0,1,0,0,1,0,0,0],  'key': 5, 'mode': 0 },
           {'name': "F#", 'vector' :[0,1,0,0,0,0,1,0,0,0,1,0],  'key': 6, 'mode': 1 },
           {'name': "F#m", 'vector':[0,1,0,0,0,0,1,0,0,1,0,0],  'key': 6, 'mode': 0 },
           {'name': "G", 'vector' :[0,0,1,0,0,0,0,1,0,0,0,1],  'key': 7, 'mode': 1 },
           {'name': "Gm", 'vector':[0,0,1,0,0,0,0,1,0,0,1,0],  'key': 7, 'mode': 0 },
           {'name': "Ab", 'vector' :[1,0,0,1,0,0,0,0,1,0,0,0],  'key': 8, 'mode': 1 },
           {'name': "Abm", 'vector':[0,0,0,1,0,0,0,0,1,0,0,1],  'key': 8, 'mode': 0 },
           {'name': "A", 'vector' :[0,1,0,0,1,0,0,0,0,1,0,0],  'key': 9, 'mode': 1 },
           {'name': "Am", 'vector':[1,0,0,0,1,0,0,0,0,1,0,0],  'key': 9, 'mode': 0 },
           {'name': "Bb", 'vector' :[0,0,1,0,0,1,0,0,0,0,1,0],  'key': 10, 'mode': 1 },
           {'name': "Bbm", 'vector':[0,1,0,0,0,1,0,0,0,0,1,0],  'key': 10, 'mode': 0 },
           {'name': "B", 'vector' :[0,0,0,1,0,0,1,0,0,0,0,1],  'key': 11, 'mode': 1 },
           {'name': "Bm", 'vector':[0,0,1,0,0,0,1,0,0,0,0,1],  'key': 11, 'mode': 0 }
          ]

def mark(data, n):
    top = heapq.nlargest(n, ((value, index) for index, value in enumerate(data)))
    indexes = set(value[1] for value in top)
    return [[value, index in indexes] for index, value in enumerate(data)]

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

def getSong(searchArtist):
    
     # Artist search 
    songResult = song.search(artist=searchArtist, buckets=["tracks",catalogId], limit="true")

    # Select a random track within the collection
    randIndex = random.randint(0, len(songResult) - 1)
       
    return songResult[randIndex]

def getSong2(searchArtist, searchTitle):
    songResult = song.search(artist=searchArtist, title=searchTitle, buckets=["tracks",catalogId], limit="true")
    
    return songResult[0]

def getChordProgression(track):
    trackId = track['id']

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
            
            # normalize chroma vector - divide each by binSize
            for j in range(12):
                avgChroma[j] /= binSize;
                       
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
                            
            if prevChord != maxChordName:
                prevChord = maxChordName;
                chordProgression.append({'name' : maxChordName, 'mode':maxChordMode, 'key': maxChordKey, 'sim': round(maxChordSim, 2) })                
        else:
            continue
        
    return chordProgression

def makePlaylist(searchArtist, chordProgression):
    # Create the playlist
    playlist = []
    
    # Choose from similar artists
    similarArtists = artist.similar(names=searchArtist);
    
    for i in range(len(chordProgression)):
        randArtist = random.randint(0, len(similarArtists) - 1)
        
        artistName = similarArtists[randArtist].name

        # Search for a song by the chosen artist in the specified key or mode
        playSongs = song.search(artist=artistName, key=chordProgression[i]['key'], mode=chordProgression[i]['mode'],  buckets=["tracks",catalogId], limit="true")
    
        if len(playSongs) > 0:
            playTrack = playSongs[0].get_tracks(catalog)

            if len(playSongs) > 0 and len(playTrack) > 0 :
    
                playlist.append({'chord' : chordProgression[i]['name'], 
                                 'artist' : artistName, 
                                 'title' : playSongs[0].title,
                                 'key' : chordProgression[i]['key'],
                                 'mode' : chordProgression[i]['mode'],
                                 'mp3' : playTrack[0]['preview_url'],
                                 'image' : playTrack[0]['release_image']  })
            elif len(playSongs) > 0  :
                playlist.append({'chord' : chordProgression[i]['name'],
                                'artist' : artistName, 
                                'title' : playSongs[0].title,
                                'key' : chordProgression[i]['key'],
                                'mode' : chordProgression[i]['mode'],
                                'mp3' : "NOT FOUND",
                                'image' : "NOT FOUND"})

    return playlist

def application(environ, start_response):
    
    s = ""

    s += "<!DOCTYPE html>"
    
    s += "<html>"
    s += "<head>"
    s += "<title>Harmony Generated Playlist</title>"
    s += "<script type='text/javascript' src='jwplayer.js'></script>"
    s += "<script src='https://ajax.googleapis.com/ajax/libs/swfobject/2.2/swfobject.js'></script>"
    s += "<link rel='stylesheet' type='text/css' href='main.css'>"
    s += "</head>"
    s += "<body>"
    
    s += "<div id='header'>"
    s += "<h1>Harmony Generated Playlist</h1>"
    s += "<a href='http://the.echonest.com'><img src='en-powered.gif' alt='Powered by the Echo Nest' /></a><br />"
    s += "</div>"
    
    queryParams = parse_qs(environ['QUERY_STRING'])
    artist = escape(queryParams.get('artist', [''])[0])
    sim = escape(queryParams.get('sim', [''])[0])

    if sim == "":
        sim = "0"
    
    if artist == "":
        artist = "Weezer"       
        song = getSong(artist)

    songTitle = escape(queryParams.get('song', [''])[0])

    if isinstance(artist, types.StringType):
        song = getSong2(artist, songTitle)
        
    track = song.get_tracks("7digital-US")[0]
    
    s += "<div id='info-container'>"
    s += "<div id='info-left'>"
    s += "ARTIST: " + song.artist_name + "<br />"
    s += "SONG TITLE: " + song.title + "<br /><br />"
    
    # Album Art
    s += "<img src='" + track['release_image'] + "' />"
    
    # MP3 player for seed song
    s += "<div id='mediaspace'>This text will be replaced</div>"
    s += """<script type='text/javascript'>
          jwplayer('mediaspace').setup({
            'flashplayer': 'player.swf',
            'file': '""" + track['preview_url'] + """',
            'controlbar': 'bottom',
            'width': '470',
            'height': '24'
          });
        </script>"""

    s += "</div><!-- /#info-left -->"

    s += "<div id='info-right'>"
    s += "<h2>How It Works</h2>"
    s += "<ul>"
    s += "<li>Get seed artist from ?artist param (default Weezer)</li>"
    s += "<li>Select random song from catalog (or from ?song)</li>"
    s += "<li>Get audio analysis from Echo Nest</li>"
    s += "<li>Get chroma vectors</li>"
    s += "<li>Compare chroma vectors to chord dictionary</li>"
    s += "<li>Use cosine similarity - choose closest</li>"
    s += "<li>For each chord, select a song in that key</li>"
    s += "<li>If chord = D maj, song key = D major</li>"
    s += "<li>Select songs from similar artists only</li>"
    s += "<li>Compile playlist</li>"
    s += "</ul>"
    s += "</div><!-- /#info-right -->"

    
    s += "</div><!-- /#info-container -->"
    
    # Print chord progression
    s += "<br />"
    s += "Chord Progression: "
    
    chordProgression = getChordProgression(track)
    s += "<div id='chord-progression'>"
    
    for i in range(len(chordProgression)):
        s += chordProgression[i]['name']
        
        if sim == "1":
            s += "<small>(" + str(chordProgression[i]['sim'] * 100) + "% )</small>"
        
        
        if i != len(chordProgression) - 1:
            s += " - "
    
    s += "</div>"
   
    # Playlist
    playlist = makePlaylist(artist, chordProgression)
    
    s += "<br />"
    
    for i in range(len(playlist)):
        s += "<div class='playlist-item'>"
        
        if playlist[i]['image'] != "NOT FOUND":
            s += "<div class='image'>"
            s += "<img src='" + playlist[i]['image'] + "' />"
            s += "</div>"
        else :
            s += "<div class='image'>"
            s += "&nbsp;"
            s += "</div>"
        
        s += "<div class='info'>"
        s += "Artist: " + playlist[i]['artist'] + "<br />"
        s += "Title: " + playlist[i]['title'] + "<br />"
        s += "Key: " + keys[playlist[i]['key']]
        
        if playlist[i]['mode'] == 1:
            s += " major"
        else:
            s += " minor"
        
        s += "<br />"
        
        if playlist[i]['mp3'] != "NOT FOUND":
            s += "<div id='player_" + str(i) + "'>This text will be replaced</div>"
            s += """<script type='text/javascript'>
              jwplayer('player_""" + str(i) +  """').setup({
                'flashplayer': 'player.swf',
                'file': '""" + playlist[i]['mp3'] + """',
                'controlbar': 'bottom',
                'width': '470',
                'height': '24'
              });
            </script>"""
            
            
        s += "</div><!-- /.info -->"
        s += "</div><!-- /.playlist-item -->"
   
    s += "</body>"
    s += "</html>"

    response_body = s
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)
    return [bytes(response_body)]