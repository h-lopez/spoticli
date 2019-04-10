import cmd2
#from cmd2 import Cmd, with_argparser

class ReplWithExitCode(cmd2.Cmd):
	""" Example cmd2 application where we can specify an exit code when existing."""

	def __init__(self):
		super().__init__()

	@cmd2.with_argument_list
	def do_exit(self, arg_list) -> bool:
		"""Exit the application with an optional exit code.
Usage:  exit [exit_code]
	Where:
		* exit_code - integer exit code to return to the shell
"""
		# If an argument was provided
		if arg_list:
			try:
				self.exit_code = int(arg_list[0])
			except ValueError:
				self.perror("{} isn't a valid integer exit code".format(arg_list[0]))
				self.exit_code = -1

		self._should_quit = True
		return self._STOP_AND_EXIT

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
	active = ReplWithExitCode().cmdloop()
	print(active)