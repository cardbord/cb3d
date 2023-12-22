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


def chcekver_update():
    current_ver = auto_updater.pull_version()
    with open(f"{globalpath}/_globals.cblog") as module_globals:
        lines = module_globals.readlines()
        __version__ = lines[0]
        module_globals.close()
    if __version__ != current_ver:
        print("updating...")
        auto_updater.pull_update()


def main():
    if update_on_launch:
        chcekver_update()

    import run_3d #this is a terrible implementation, don't worry it's temporary

    #main script here

if __name__ == "__main__":
    main()