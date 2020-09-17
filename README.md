# SpotiCLI

### About
Command line front end for Spotify  
This program still requires that the Spotify client be installed locally  
Please note this REQUIRES Spotify Premium to use as most of the APIs are locked behind premium

[![asciicast](https://asciinema.org/a/345797.svg)](https://asciinema.org/a/345797)

### Features
* play/pause
* play next/previous track
* seek in current track
* search and play album, artists and tracks
* queueing (only for tracks)
* repeat/shuffle toggle
* volume control
* playback transfer (ie. move playback to a new spotify connect endpoint)
* save/unsave tracks to liked songs 
* view/play your followed/saved playlists

### Compatibility
* Win10 - Fully compatible
* Linux - Fully compatible
* MacOS - utterly untested, probably works(?)

### Requirements
* python 3.7 or higher
* [tekore](https://github.com/felix-hilden/tekore)
* [cmd2](https://github.com/python-cmd2/cmd2/)
* [colorama](https://github.com/tartley/colorama)

### Installation
1. install above requirements
1. setup a spotify [dev account](https://developer.spotify.com/) and have a client id/secret ready to use
1. clone repo
1. run 'python3 \_\_init\_\_.py' from the command line
1. complete authorization process
1. play music

