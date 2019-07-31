SpotiCLI 1.0

Command line front end for spotify 
REQUIRES spotify premium to use front end as most of the API is locked behind premium :(

Built with Python using Cmd2, Colorama and Spotipy libraries
this project would not exist without these contributions

system compatability:
Win10 - Fully compatible
Linux - mostly working, some bugs to squish
Android - (via termux), mostly working! some bugs to squish. not sure why anyone would want this but it's there
MacOS - untested

requirements:
-python3
-pip
-spotipy
-cmd2
-colorama

install guide:
1. setup spotify dev account and have a client id/secret ready to use 
2. clone repo 
3. run 'python3 client.py' or whatever you need to do to run a .py  
4. authorize yourself

once working you're good

TO DO:
-Implement playing track/artist/playlist/album from search -- DONE! July 2018
-Implement playback transfer -- DONE! August 2018
-Implement colors, not all output is colored. --50% Update: good enough. jul 19 
-Implement queuing, unknown when since we're reliant on spotify API supporting queuing (it doesn't as of jul 2019)
-Implement queuing, unqueuing, saving, removing tracks from history/search
	also pending spotify API
	but we can implement saving/removing from history/search (COMPLETE, Nov 2018)
-Implement viewing previously played songs and next up songs 
	can view last 5 played songs!
	implementing next 5 songs/skipping behavior means more work
	...and requires spotify to implement queuing in their API
	ie. not possible at this time.
-implement automatic token refreshing (currently needs to be done manually/reloading the program). this is unideal. DONE. I fixed this last...feb? march? i forgot to be honest
-implement live timer that shows current song + elapsed time 
	not sure if possible with current implementation, might need to find library that can do this
	ncurses?
	also need to find a way to poll live status from spotify application instead of making a bajillion, constant checks to the API

TO do before any serious public release:
 -Improve the authorization process (harcoding your client id and client secret into the application is a shit solution)
 -relicense under a real license. GPL? MIT?
 -squish bugs / improve 
 -fix the goddamn bugs

Color Scheme:

Red: Errors
Green: prompt

keep is simple amirite

//example preview url
https://p.scdn.co/mp3-preview/d5c742f7e2d651d8f34761e045cfbcdb76f6b077?cid=774b29d4f13844c495f206cafdad9c86

"preview_url" key available from track object (ie. obtainable from search)
//need to implement webview behind the scenes to play the track?
1. user searches track
2. user decides to demo track
3. spoticli saves the preview_url of the selected item
4. spoticli gets current track, timestamp and volume level
5. spoticli checks if playback is active
6. spoticli pauses playback if active
7. spoticli creates web browser object and visits the preview 
8. user will not be able to interact with the preview (since it's occuring OUTSIDE of the player)

review: shit solution

//download and play using local media player
1. user searches track
2. user decides to demo track
3. spoticli saves the preview_url of the selected item
4. spoticli gets current track, timestamp and volume level
5. spoticli checks if playback is active
6. spoticli pauses playback if active
7. spoticli downloads the 30s preview and plays it locally
8. user <i>should</i> be able to interact with it and pause/play 
//wouldn't it require an additional check to determine whether 
//to play the spoticli content or the preview? 
//alternatively you can encapsulate the preview in it's own cli program
//where those commands won't affect the spoticli content
//but at that point this is just ridiculous

review: also shit solution