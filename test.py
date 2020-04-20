from cmd2 import Cmd, with_argparser

class Tester(Cmd):
    def __init__(self):
        super().__init__()

        app_name = 'SpotiCLI'
        version = '1.20.0420.dev'
        
        ###define app parameters
        self.app_info = f'\n{app_name} {version}'
        self.intro = self.app_info + '\n'
        self.prompt = 'spoticli ~$ '

        #hide built-in cmd2 functions. this will leave them available for use but will be hidden from tab completion (and docs)
        self.hidden_commands.append('alias')
        self.hidden_commands.append('unalias')
        self.hidden_commands.append('set')
        self.hidden_commands.append('edit')
        self.hidden_commands.append('history')
        self.hidden_commands.append('load')
        self.hidden_commands.append('macro')
        self.hidden_commands.append('py')
        self.hidden_commands.append('pyscript')
        self.hidden_commands.append('shell')
        self.hidden_commands.append('shortcuts')
        self.hidden_commands.append('_relative_load')
        self.hidden_commands.append('run_pyscript')
        self.hidden_commands.append('run_script')
        
        self.input_test = ''

    def do_input(self, line):
        self.input_test = input('insert input\n')

    def do_prompt(self, line):
        print(self)

    def do_output(self, line):
        print(self.input_test)


if __name__ == '__main__':
    Tester().cmdloop()