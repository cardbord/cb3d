import requests
from pathlib import Path
from os import walk

def pull_gh(path:str):
    r = requests.get(f"https://raw.githubusercontent.com{path}",stream=True)
    if r.status_code in range(200,299):
        return r.text
    
def pull_version():
    return pull_gh("/cardbord/cb3d/main/_globals.py")

def pull_update():
    
    module_path = Path(__file__).parent
    md_walk = walk(module_path)
    for (dirpath, dirname, filename) in md_walk:
        print(dirpath,dirname,filename)

pull_update()