import requests
from pathlib import Path
from os import walk

def pull_gh(path:str):
    r = requests.get(f"https://raw.githubusercontent.com{path}",stream=True)
    if r.status_code in range(200,299):
        return r.text
    
def pull_version():
    return pull_gh("/cardbord/cb3d/main/_globals.cblog")

def pull_update():

    module_path = Path(__file__).parent
    md_walk = walk(module_path)
    for (dirpath, dirname, filename) in md_walk:
        if not "__pycache__" in dirpath and not ".CBmodel" in filename:
            path_formatted = dirpath[dirpath.find("main"):].replace("\\","/")
            
            for file in filename:
                if not ".CBmodel" in file and not "auto_updater" in file:
                    
                    path = "/cardbord/cb3d/main/"+path_formatted+f"/{file}"
                    pulled_file = pull_gh(path)

                    if pulled_file:
                        openable_path = dirpath.replace("\\","/") + "/"+file
                        
                        with open(openable_path,'w') as overwritable:
                            overwritable.write(pulled_file) 
                            overwritable.close()
                    else:
                        pass # file was not pulled properly due to non-existence/request error, so we pass it,    
            