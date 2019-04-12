import cmd2
#from cmd2 import Cmd, with_argparser
from datetime import datetime, timedelta

class ReplWithExitCode(cmd2.Cmd):
	""" Example cmd2 application where we can specify an exit code when existing."""

	def __init__(self, current_time):
		self.creation_time = current_time
		self.expiration_time = current_time + timedelta(seconds=10)
		
		super().__init__()

	def do_exit(self, exit_att):
		"""Exit the application with an optional exit code.
Usage:  exit [exit_code]
	Where:
		* exit_code - integer exit code to return to the shell
"""
		# If an argument was provided
		if exit_att:
			try:
				self.exit_code = exit_att
			except:
				print('invalid code')
				self.exit_code = -1
		self.exit_code = 2

		self._should_quit = True
		return self._STOP_AND_EXIT
	
	def precmd(self, line):
		if(datetime.now() > self.expiration_time):
			print('exit condition reached')
			self.do_exit(line)
		return line
	
	def do_creation(self, line):
		print(self.creation_time)
		
	def do_expiration(self, line):
		print(self.expiration_time)
	
	def postloop(self):
		"""Hook method executed once when the cmdloop() method is about to return."""
		code = self.exit_code if self.exit_code is not None else 0
		self.poutput('exiting with code: {}'.format(code))
		print(code)
		return code

if __name__ == '__main__':
	#declare spotipy object
	#create spotipy object and pass along to spoticli object
	#while(True):
		#sp = spotipy.Spotify(initialize_env())
		#active = SpotiCLI(sp, current_time).cmdloop()
	while(True):
		current_time = datetime.now()
		active = ReplWithExitCode(current_time).cmdloop()
		if active is None:
			print('re-iterate!')
			continue
		else: 
			break