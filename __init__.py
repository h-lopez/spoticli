from cli import SpotiCLI

if __name__ == '__main__':
    ### auth user
    ### pass along auth token to spoticli
    ### spoticli will handle auth user and periodically refresh token as needed
    SpotiCLI().cmdloop()