#run auto-updater
#force new file creation, or open file
#give suggestions of previous files
#give option to start/join classroom service

r'''
Main script for cb3d.

As of version 0.0.3, The auto-updater launches before any other script.
If this functionality is undesirable/non-working for any user, please change the following variable to

::update_on_launch = False::

To disable version checking. Toggle back to True to reverse these changes.
'''

update_on_launch = True


import auto_updater
import guizero
from pathlib import Path

globalpath = str(Path(__file__).parent.parent).replace('\\','/') #base all path operations under a relative path obtained through pathlib


def chcekver_update(): #method to update the module, using our version pulls and file replacement in auto_updater.py
    current_ver = auto_updater.pull_version()
    if current_ver is None: 
        return False #return False if no version pulled, as there is a problem with repo/internet connection
    else:
        with open(f"{globalpath}/_globals.cblog") as module_globals:
            lines = module_globals.readlines()
            global __version__ #establish global version so it does not need to be fetched again
            __version__ = lines[0] 
            module_globals.close()
        if __version__ != current_ver:
            print("updating...")
            return auto_updater.pull_update()
        else:
            return True

def main():
    if update_on_launch:
        successful = chcekver_update() #this works as long as main.py is not changed. in any other case, a restart is required.
        if not successful:
            try_again = guizero.yesno("cb3d update failed","Try again?")
            if try_again:
                main() #call main recursively, to reattempt the update
            else:
                guizero.info("cb3d notice","Launching in offline mode, community features will be disabled")

    import run_3d #this is a terrible implementation, don't worry it's temporary

    #main script here

if __name__ == "__main__":
    main()