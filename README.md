# Harmony Generated Playlist
## Created at Music Hack Day San Francisco 2011

Generate a playlist of related songs based on the chord structure of a seed song.

Create a concept album on the fly!

## How it works

* Get seed artist from ?artist param (default Weezer)
* Select random song from catalog (or from ?song)
* Get audio analysis from Echo Nest
* Get chroma vectors
* Compare chroma vectors to chord dictionary
* Use cosine similarity - choose closest
* For each chord, select a song in that key
* If chord = D maj, song key = D major
* Select songs from similar artists only
* Compile playlist

Uses Echo Nest API for artist, song, and chroma data. Chord estimation using cosine similarity method.