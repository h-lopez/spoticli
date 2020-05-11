'''
SpotiCLI
Copyright 2020, Hugo A Lopez

released under the MIT license

fsop.py - File System OPerations 

fsop is used to define/delete user login sessions/config files from user's home directory
'''
import os
from os import path
from os.path import expanduser

class fsop():

    ### move to user home directory   
    os.chdir(expanduser('~'))
    if(path.exists('.config/spoticli')):
        os.chdir('.config/spoticli')
    else:
        try:
            os.makedirs('.config/spoticli')
            os.chdir('.config/spoticli')
        except:
            ('failed to create directory, do you have write access?')
            exit()

    def create_conf(self):
        pass

    def delete_conf(self):
        if(path.exists('auth.spoticli')):
            try:
                os.remove('auth.spoticli')
                os.remove('conf.spoticli')
                return True
            except:
                return False