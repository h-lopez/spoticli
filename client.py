import spotipy
import spotipy.util
import datetime

from spoticli import SpotiCLI
from datetime import datetime

#what if we pass time as parameter into spoticli object
#spoticli checks preloop if current time > creation time + 40
#if it is, exit, and have client re-loop it.
#i don't see a point to this. all it does is start spoticli

if __name__ == '__main__':
	SpotiCLI().cmdloop()