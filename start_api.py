r'''
this is a bridge program so I can provide command line arguments (eg a room code) to the API's startup method
which seems very difficult if I were to try and run it by uvicorn in the terminal
'''

import uvicorn
from main.api import host        
        
uvicorn.run(host.host_service, host='0.0.0.0',port=8000)