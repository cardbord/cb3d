#run auto-updater
#force new file creation, or open file
#give suggestions of previous files
#give option to start/join classroom service
import auto_updater
import guizero
from pathlib import Path

globalpath = str(Path(__file__).parent.parent).replace('\\','/')
print(globalpath)
def main():
    current_ver = auto_updater.pull_version()
    with open(f"{globalpath}/_globals.cblog") as module_globals:
        lines = module_globals.readlines()
        __version__ = lines[0]
        module_globals.close()
    if __version__ != current_ver:
        print("updating...")
        auto_updater.pull_update()

if __name__ == "__main__":
    main()