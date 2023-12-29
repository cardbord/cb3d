import requests
from pathlib import Path
from os import walk
from guizero import error

def pull_gh(path:str):
    r = requests.get(f"https://raw.githubusercontent.com{path}",stream=True)
    if r.status_code in range(200,299):
        return r.text
    
def pull_version():
    return pull_gh("/cardbord/cb3d/main/_globals.cblog")

def pull_update() -> bool: #return bool for result of success/failure
    fulfilled_update = False
    module_path = Path(__file__).parent
    md_walk = walk(module_path)
    try:
        for (dirpath, _, filename) in md_walk: #dirname isn't required
            if not "__pycache__" in dirpath and not ".CBmodel" in filename:
                path_formatted = dirpath[dirpath.find("main"):].replace("\\","/")
                
                for file in filename:
                    if not ".CBmodel" in file and not "auto_updater" in file:
                        
                        path = "/cardbord/cb3d/main/"+path_formatted+f"/{file}"
                        pulled_file = pull_gh(path)

                        #we have to check how pulled_file compares to our current file.
                        #if no changes, no update.
                        #this ensures that fulfilled_update functions as intended.

                        if pulled_file:
                            openable_path = dirpath.replace("\\","/") + "/"+file
                            must_overwrite=False

                            with open(openable_path,'r') as readable_for_changes:
                                content = readable_for_changes.read()
                                if content!=pulled_file:
                                    must_overwrite=True
                                else:
                                    pass
                                readable_for_changes.close()

                            if must_overwrite:
                                with open(openable_path,'w') as overwritable:
                                    overwritable.write(pulled_file) 
                                    overwritable.close()
                                    fulfilled_update=True #an update has been completed successfully, so we use this bool to guarantee that _globals gets the latest version
                        else:
                            pass # file was not pulled properly due to non-existence/request error, so we pass it
    except Exception as e: #failsafe
        print(f"Caught error {e}")
        return False #actually, since main haldles this now, we don't need to notify the in the event of an error, we just cancel the update


    if fulfilled_update:
        with open("_globals.cblog", 'w') as module_globals:
            module_globals.write(pull_version())
        return True
    else:
        return False