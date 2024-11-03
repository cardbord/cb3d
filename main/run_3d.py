#NECESSARY IMPORTS
import pygame, guizero, subprocess, requests, os, socket, json


###DISPLAY SETUP
pygame.init()
winsize = pygame.display.get_desktop_sizes()[0]
dis = pygame.display.set_mode((winsize[0],winsize[1]))
pygame.display.set_caption('cb3d','CBmodel engine')
clock = pygame.time.Clock()

#PARTIAL IMPORTS
from pathlib import Path
from cb3d_disgrid import display_3Dgrid
from model import Point, CBModel, Plane, catalogue
from pygame import gfxdraw
from utils.plane_sorter import quicksort, binary_search, transform
from utils.pgui import Text, TextType, Anchor, Button, TextInput, Dropdown, menu, Drawing, DisplayColumns, DisplayRows, Image, Handler, GUIobj, scale_to_window
from webbrowser import open_new_tab
from random import choice


#TEXTURE INIT
__glass = catalogue.textures['glass']

tRows = []
for texture in catalogue.textures:
    
    _row = DisplayColumns([
        DisplayRows([
            Image([0,0],catalogue.textures[texture].texture_map),
        ]),
        Text([0,0],texture),
    ])
    tRows.append(_row)

###GLOBALS

debug = False #SET FALSE WHEN NOT TESTING (can be toggled through F9)
start_menu_shown = True
since_last_moved = 0
curr_static_image = None
show_static_image = False

global cbmod

path = Path(__file__).parent #just in case python refuses to locate model files, this is a slight problem since older versions of pygame are pretty fussy
cbmod, successful_load = CBModel.from_cblog() #return a new CBModel, or a pre-existing one from a previous cb3d runtime

image_preview = None
if successful_load: #if saved normally, there should be a preview for it
    image_preview = pygame.image.load(str(path)+'/_preview.jpg').convert()
    aspect_ratio = image_preview.get_size()
    image_preview = image_preview.subsurface(pygame.Rect(aspect_ratio[0]/4,0,aspect_ratio[1],aspect_ratio[1]))
    
global api_token
api_token = None

global api_username
api_username = None

global localnetworkIP
localnetworkIP = None

try:
    if os.path.exists('_hostname.cblog'):
        with open('_hostname.cblog','r') as hostname:
            localnetworkIP=hostname.read()
            localnetworkIP = socket.gethostbyname(localnetworkIP)
            if localnetworkIP == socket.gethostbyname(socket.gethostname()):
                localnetworkIP='127.0.0.1'
            print(localnetworkIP)
except: #user is not on the network
    localnetworkIP=None


with open(str(path.parent)+'\\_globals.cblog','r') as version_doc:
    __VERSION = version_doc.read().replace("'","")
    version_doc.close()
    

with open(str(path)+'\\title_messages.json','r') as title_messages:
    text = title_messages.read()
    messages = json.loads(text)
    splashtext = choice(messages['messages'])
    

###BUTTON CALLBACKS

def open_saved():
    pass

def load_file():
    global cbmod
    savename = guizero.select_file("Open cbmodel",filetypes=[["CBmodels","*.CBmodel"]])
                            
    if savename == "":
        pass #user has closed the file opener, so pass

    else:

        cbmod = CBModel.load(savename)
        cbmod.filename_modified = savename
        
        return True
    
def createKeyMenu():
    ttype = TextType.h3
    ftype = 'Segoe UI'
    content = DisplayRows([
        Text([0,0],'c: clear current model',type=ttype,font=ftype).anchor(Anchor.LEFT),
        Text([0,0],'k: load model',type=ttype,font=ftype).anchor(Anchor.LEFT),
        Text([0,0],'j: save current model',type=ttype,font=ftype).anchor(Anchor.LEFT),
        Text([0,0],'m: place demo box',type=ttype,font=ftype).anchor(Anchor.LEFT),
        Text([0,0],'h: centre model',type=ttype,font=ftype).anchor(Anchor.LEFT),
        Text([0,0],'g: toggle grid lines',type=ttype,font=ftype).anchor(Anchor.LEFT),
        Text([0,0],'s: show points',type=ttype,font=ftype).anchor(Anchor.LEFT)
    ])

    key_menu = GUIobj([0,0],[700,600],"keybinds")
    key_menu.add_content(content)

    return key_menu

    
    
def save_file():
    global cbmod
    savename = guizero.select_file("Save CBmodel",save=True,filetypes=[["CBmodel","*.CBmodel"]])
    print(savename)
    if savename == "":
        pass
    else:
        cbmod.save(savename)
        cbmod.filename_modified = savename

def new_file():
    global cbmod
    cbmod = CBModel()
    
    return save_file()

def open_help():
    open_new_tab('https://boxo.ovh/') #make page soonish
    
def my_github():
    open_new_tab('https://github.com/cardbord/cb3d') #link to github issues


def show_instructions(): #i need something for the __name__checker to look at
    pass

def childClientJoinAPI():
    input_options = handler.collate_textinput_inputs()
    
    _room_id = input_options.get('Room ID')
    _username = input_options.get('Username')
    _password = input_options.get('Password')

    json = {
        'username':_username,
        'password':_password,
        'roomid':_room_id
    }
    try:
        r = requests.post(f"http://{localnetworkIP}:8000/register/",json=json)
        if r.status_code in range(200,299):
            guizero.info(f'hi, {_username}!','You are registered')
        else:
            guizero.warn("Something isn't right...",'Check your room ID carefully, and try again')
    except:
        guizero.warn("Host is not running",'Please ask your host to start the server!')    

def childRegister():
    obj = GUIobj([0,0],[900,700], 'Network')
    obj.add_content(
        DisplayRows([
            TextInput([0,0],'Room ID'),
            TextInput([0,0],'Username'),
            TextInput([0,0],'Password'),
            Button([0,0],'Join',[170,60],None,childClientJoinAPI).anchor(Anchor.BOTTOMRIGHT)
        ])
    )
    handler.add(obj)
    
def childApplyForToken():
    input_options = handler.collate_textinput_inputs()
    _username = input_options.get('Username')
    _password = input_options.get('Password')
    

    if _username != '' and _password != '':
        
        json = {
            'username':_username,
            'password':_password,
        }
        
        r = requests.post(f"http://{localnetworkIP}:8000/login/",data=json,headers={'content-type':'application/x-www-form-urlencoded'})
        if r.status_code in range(200,299):
            global api_token
            api_token = r.json()['access_token']
            global api_username
            api_username = _username

            guizero.info(f'welcome, {_username}!','You can now access community features')
        else:
            guizero.warn('Invalid details','Please enter a valid username or password, or register')
            
    else:
        guizero.warn('No details entered','Please fill out the username and password sections')
        
    

    
def childLogin():
    obj = GUIobj([0,0],[650,300], 'Login')
    obj.add_content(
        DisplayRows([
            TextInput([0,0],'Username'),
            TextInput([0,0],'Password'),
            Button([0,0],'Login',[210,60],None,childApplyForToken).anchor(Anchor.BOTTOMRIGHT)
        ])
    )
    handler.add(obj)


def childNetworkBuildAPI():
    input_options = handler.collate_textinput_inputs()
    
    if input_options.get('roomID')!=None:
        subprocess.Popen(['python', str(path.parent)+'/start_api.py', 'code'+input_options['roomID']])
    else:
        subprocess.Popen(['python', 'start_api.py'])
    
    
    guizero.info('Creating network...','Please find your network details in the terminal.')

def childNetworkCreate():
    
    obj = GUIobj([0,0],[900,700],'Network')
    obj.add_content(
        DisplayRows([
            Text([0,0],"Networks require a unique room ID for privacy.",TextType.h2),
            DisplayColumns([
                DisplayRows([
                    Text([0,0],'Please enter a room ID',TextType.h2).anchor(Anchor.LEFT),
                    TextInput([0,0],'',textInputID='roomID').anchor(Anchor.CENTER),
                    None
                ]),
                None
            ]),
            DisplayRows([
                Text([0,0],'Users will need to login to access your database.',TextType.h3),
                Text([0,0],'Anybody can create an account.', TextType.h3),
            ]),
            
            Button([0,0],'Confirm',[210,60], None, childNetworkBuildAPI).anchor(Anchor.BOTTOMRIGHT)
        ])
    )
    
    handler.add(obj)


def checkAuthBuild(funct):
    if api_token != None: #SET != NONE WHEN NOT TESTING
        match funct.__name__:
            case 'childBuildFileViewer':

                r = requests.get(f"http://{localnetworkIP}:8000/models/",headers={
          "Authorization":f'Bearer {api_token}'
          })
                if r.status_code in range(200,299):
                    print(r.json())
                    

                    childBuildFileViewer(r.json(), 0)


            case 'childBuildFileUploader':
                
                childBuildFileUploader()
                
                            
                
    else:
        guizero.warn('No login!','Please log in before accessing community features')    
    

def childDownloadModel(modeldata):
    savename = guizero.select_file("Save CBmodel",save=True,filetypes=[["CBmodels","*.CBmodel"]])
    print(savename)
    if savename == "":
        pass
    with open(savename+'.CBmodel','w') as writable:
        writable.write(modeldata)
    

def changeUploaderPage(directory,pageNum):
    pos = handler.GUIobjs_array[0].pos
    handler.GUIobjs_array.pop(0)
    childBuildFileViewer(directory,pageNum)
    l = len(handler.GUIobjs_array)
    if l>1:
        temp = handler.GUIobjs_array[0]
        handler.GUIobjs_array[0] = handler.GUIobjs_array[l-1]
        handler.GUIobjs_array[l-1] = temp
    handler.GUIobjs_array[0].move_window(pos)
    handler.GUIobjs_array[0].content[0].parent_pos=pos
    handler.GUIobjs_array[0].content[0]._calc_obj_rel_pos(handler.GUIobjs_array[0].clickableborder_pos[1])


def calcFileSizeFromString(string): #assuming a byte is used per character
    size_in_kb = round(len(string)/1000,3)
    if size_in_kb > 10:
        return 'large', size_in_kb
    elif size_in_kb > 1:
        return 'average', size_in_kb
    else:
        return 'small', size_in_kb


def childBuildFileViewer(directory, pageNum:int=0):
    if len(directory) > 3:
        start = pageNum*3
        end = start+2
        if len(directory) <= end:
            end = len(directory)-1

        viewable = directory[start:end+1]
    else:
        pageNum=0
        viewable=directory
    print(directory)
    obj = GUIobj([0,0],[1200,800],'Community models')
    
    modelarray = []
    

    if len(viewable) > 0:
        model = viewable[0]
        modelsize = calcFileSizeFromString(model['modeldata'])
        modelarray.append(
            DisplayColumns([
                DisplayRows([
                    Text([0,0],model['modelname'].replace('.CBmodel',''),TextType.h2,colour=(50, 35, 117),font='Segoe UI'),
                    Text([0,0],'- by '+model['username'],TextType.h3,colour=(52, 42, 97),font='Segoe UI'),
                    None
                ]),
                DisplayRows([
                    None,
                    Text([0,0],f'Relatively {modelsize[0]} ~ {modelsize[1]} kilobytes',TextType.h3,font='Segoe UI',colour=(153, 38, 143)),
                    Text([0,0],'Shape',TextType.h3) if model['modeldata'].startswith('[]\n[]\n') else Text([0,0],'Wireframe model',TextType.h3),
                    #Text([0,0],model['modeldata'][:50]+'...'  if len(model['modeldata']) > 50 else model['modeldata'],TextType.h3,colour=(77, 76, 76)),
                ]),
                
                Button([0,0],'Download',[245,60],None,lambda:(childDownloadModel(model['modeldata'])))
            ])
        )
    if len(viewable) > 1:
        model2 = viewable[1]
        modelsize = calcFileSizeFromString(model2['modeldata'])
        modelarray.append(
            DisplayColumns([
                DisplayRows([
                    Text([0,0],model2['modelname'].replace('.CBmodel',''),TextType.h2,colour=(50, 35, 117),font='Segoe UI'),
                    Text([0,0],'- by '+model2['username'],TextType.h3,colour=(52, 42, 97),font='Segoe UI'),
                    None
                ]),
                DisplayRows([
                    None,
                    Text([0,0],f'Relatively {modelsize[0]} ~ {modelsize[1]} kilobytes',TextType.h3,font='Segoe UI',colour=(153, 38, 143)),
                    Text([0,0],'Shape',TextType.h3) if model2['modeldata'].startswith('[]\n[]\n') else Text([0,0],'Wireframe model',TextType.h3),
                    #Text([0,0],model2['modeldata'][:50]+'...'  if len(model2['modeldata']) > 50 else model2['modeldata'],TextType.h3,colour=(77, 76, 76)),
                ]),
                
                Button([0,0],'Download',[245,60],None,lambda:(childDownloadModel(model2['modeldata'])))
            ])
        )
    if len(viewable) > 2:
        model3 = viewable[2]
        modelsize = calcFileSizeFromString(model3['modeldata'])
        modelarray.append(
            DisplayColumns([
                DisplayRows([
                    Text([0,0],model3['modelname'].replace('.CBmodel',''),TextType.h2,colour=(50, 35, 117),font='Segoe UI'),
                    Text([0,0],'- by '+model3['username'],TextType.h3,colour=(52, 42, 97),font='Segoe UI'),
                    None
                ]),
                DisplayRows([
                    None,
                    Text([0,0],f'Relatively {modelsize[0]} ~ {modelsize[1]} kilobytes',TextType.h3,font='Segoe UI',colour=(153, 38, 143)),
                    Text([0,0],'Shape',TextType.h3) if model3['modeldata'].startswith('[]\n[]\n') else Text([0,0],'Wireframe model',TextType.h3),
                    #Text([0,0],model3['modeldata'][:50]+'...'  if len(model3['modeldata']) > 50 else model3['modeldata'],TextType.h3,colour=(77, 76, 76)),
                ]),
                
                Button([0,0],'Download',[245,60],None,lambda:(childDownloadModel(model3['modeldata'])))
            ])
        )

    modelarray.append(
        DisplayColumns([
            Button([0,0],'<-',None,None,lambda: (changeUploaderPage(directory,pageNum-1 if pageNum!=0 else 0))),
            Text([0,0],f'page {pageNum+1}',TextType.h3),
            Button([0,0],'->',None,None,lambda: (changeUploaderPage(directory,(pageNum+1) if len(directory)-(3*(pageNum+1)) > 0 else pageNum)))
        ])
    )
    
    obj.add_content(
        DisplayRows(modelarray)
    )
    
    handler.add(obj)
    

def childBuildFileUploader():
    savename = guizero.select_file("Open CBmodel",filetypes=[["CBmodels","*.CBmodel"]])
                            
    if savename == "":
        pass #user has closed the file opener, so pass

    else:
        print(savename)
        with open(savename,'r') as opened_file:
            lines = opened_file.read()
        json = {
            'modelname':os.path.basename(savename), 
            'modelData':lines,
            'username':api_username
        }
        r=requests.post(f"http://{localnetworkIP}:8000/upload/", json=json, headers={"Authorization":f'Bearer {api_token}'})
        if r.status_code in range(200,299):
            print(r.json())
            guizero.info('Model uploaded!',"See all models on the 'Models' tab")


def setHostName():
    name = guizero.askstring('Set host name','Ask your host for their device name!')
    if name!='':
        with open('_hostname.cblog', 'w') as addhostname:
            addhostname.write(name)
        global localnetworkIP
        localnetworkIP=socket.gethostbyname(name)
        if localnetworkIP == socket.gethostbyname(socket.gethostname()):
            localnetworkIP='127.0.0.1'
        print(localnetworkIP)
    else:
        pass


def buildTextureMenu():
    textureMenu = GUIobj([int(round(winsize[0]-scale_to_window(752))), 0], [300,900], "Textures")

    textureMenu.add_content(
        DisplayRows(
            tRows
        )
    )
    handler.add(textureMenu)

def buildTransform(points,planetype):
    input_options = handler.collate_textinput_inputs()
    colour_submitted = (int(input_options['redV']), int(input_options['greenV']), int(input_options['blueV']))
    transformations = transform(points,planetype,input_options['Extrusion'],input_options['From'])
    texture = input_options['Texture']
    if texture != 'default':
        texture = catalogue.textures[texture]
    else:
        texture = None
    for transformation in transformations:
        if len(transformation) == 4:
            cbmod.add_plane(transformation, [0,1,0,3,1,2,2,3], colour_submitted, texture)
        else:

            cbmod.add_plane(transformation, [i for i in range(len(transformation))], colour_submitted, texture)



###GUI MENUS
def createMenu():
    file_list = [
        Button([0,0],"Return",[200,60],None,open_saved),
        Button([0,0],"New",[200,60],None,new_file),
        Button([0,0],"Load",[200,60],None,load_file),
    ]    
    help_list = [
        Button([0,0],"Docs",[200,60],None,open_help),
        Button([0,0],"Keys",[200,60],None,show_instructions),
        Button([0,0],"Github",[200,60],None,my_github),
    ]
    network_list = [
        Button([0,0],"Set host", [210,60],None, setHostName),
        Button([0,0],"Upload",[210,60],None, lambda: (checkAuthBuild(childBuildFileUploader))),
        Button([0,0],"Models",[210,60],None, lambda: (checkAuthBuild(childBuildFileViewer))),
        Button([0,0],"Register",[210,60],None, childRegister),
        Button([0,0],"Login",[210,60],None, childLogin),
        Button([0,0],"Create",[210,60],None,childNetworkCreate)
    ]
    
    _File = Dropdown([0,0], Button([0,0],"File",[200,50],(10,10,10)), file_list)#place button list in sq brackets
    _Help = Dropdown([scale_to_window(200),0], Button([scale_to_window(200),0],"Help",[200,50],(10,10,10)), help_list) 
    _Networks = Dropdown([scale_to_window(400),0], Button([scale_to_window(400),0],"Network", [210,50], (10,10,10)), network_list)
    

    start_menu = menu(
        [
            _File,
            _Help,
            _Networks
        ]
    )
   
    _menu_content = DisplayColumns(
        [

            DisplayRows(
                [
                    DisplayRows([ #TITLE + version
                        None,
                        DisplayColumns([
                            None,None,
                            Text([0,0],'CB3D',TextType.banner,font="Segoe UI",bold=True,colour=(129, 50, 168), background=None,banner_effect=False),
                            None,
                            DisplayRows([
                                None,
                                None,
                                None,
                                Text([0,0],f' v{__VERSION}', TextType.h3, font="Consolas",colour=(233, 66, 245)),    
                            ])
                            
                            
                                
                        ]),
                        None,
                        Text([0,0],splashtext, TextType.h3, font="Segoe UI",italic=True, colour=(240,90,250)),
                        None
                    ]),
                    
                    DisplayRows( #body
                        [
                            
                            DisplayColumns([
                                None,
                                DisplayRows([
                                    Text([0,0],"cb3d is a 3D modelling software packed with useful features",TextType.p,font="Segoe UI").anchor(Anchor.LEFT),
                                    Text([0,0],"- click 'File' to start working on a model...",TextType.p, font="Segoe UI").anchor(Anchor.LEFT),
                                    Text([0,0],"- or click 'Help' for some tips on buttons you can use!",TextType.p, font="Segoe UI").anchor(Anchor.LEFT),
                                    Text([0,0],"- also, use the 'networks' tab to share models locally",TextType.p, font="Segoe UI").anchor(Anchor.LEFT),
                                ]),
                                None,None,None,None
                            ]),
                
                            Text([0,0],"a short quickstarter on modelling", TextType.h2, font="Segoe UI"),
                            
                            DisplayRows([
                                Text([0,0],'- open a new file from the menu',TextType.p,font="Segoe UI"),
                                Text([0,0],"- click the plus shape button", TextType.p,font="Segoe UI"),
                                Text([0,0],"- draw your shape in the grid...", TextType.p,font="Segoe UI"),
                                Text([0,0],"- click draw and extrude the shape",TextType.p,font="Segoe UI")    
                            ]),
                            
                            
                            
                            
                        ]
                    ),
                    DisplayColumns([
                        Text([0,0],'Like this! ~>',TextType.h3,italic=True,font='Segoe UI',colour=(90,90,90)),
                        DisplayRows([Image([0,0],'demo.png')]),
                        None
                    ])
                    
                ]
            ),
            DisplayRows(
                [
                    Image([0,0],"backg.jpg" if image_preview == None else image_preview),
                ]
            )
        ]
    )
                                         
    
    start_menu.add_content(_menu_content)
    
    return start_menu


menu_screen = createMenu()

def ChildXYZselector(points) -> GUIobj: #this is implemented inside run_3d.py
    selector = GUIobj([int(round(winsize[0]-scale_to_window(452))),0],[452,1080],'Draw to')
    selector.points = []
    
    for i in points:
        if i not in selector.points:
            selector.points.append(i)

    selector.add_content(
        
        DisplayRows([
            Image([0,0],'boxo_xy.png').set_callback(lambda:buildTransform(selector.points,'xy')),
            Image([0,0],'boxo_xz.png').set_callback(lambda:buildTransform(selector.points,'xz')),
            Image([0,0],'boxo_yz.png').set_callback(lambda:buildTransform(selector.points,'yz')),
            DisplayRows([
                None,
                DisplayColumns([
                    Text([0,0],'From',TextType.h3),None
                ]), 
                
                TextInput([0,0],'','0',1,'From'),
                
            ]),
            
            DisplayRows([
                None,
                DisplayColumns([
                    Text([0,0],'Extrusion',TextType.h3),None
                ]), 
                TextInput([0,0],'','0',1,'Extrusion'),
                
            ]),
            
            DisplayRows([
                None,
                DisplayColumns([
                    Text([0,0],'Colour (rgb)',TextType.h3),None
                ]), 
                DisplayColumns([
                    TextInput([0,0],'','255',3,'redV',True), TextInput([0,0],'','255',3,'greenV',True), TextInput([0,0],'','255',3,'blueV',True)
                ]),
                
            ]),

            DisplayRows([
                None,
                DisplayColumns([
                    Text([0,0],'Texture',TextType.h3),None
                ]), 
                TextInput([0,0],'','default',7,'Texture'),
                
            ]),
            
            Button([0,0],'Preview textures',None,None,buildTextureMenu)
            
            
            
            #we use the anonymous function lambda: cbmod.add_plane(buildTransform(d.points,planetype), [], texture) to add planes!
        ]),
            
        
    )
    return selector

draw = Drawing([0,0],[800,800],"add object")
draw.draw_button.callback = ChildXYZselector



###GRID POINT INITS
grid_points = []
grid_points.append(Point([0,0,0]))
grid_points.append(Point([10000,0,0]))
grid_points.append(Point([0,10000,0]))
grid_points.append(Point([0,0,10000]))


###TO BE REMOVED
answer = '' #these globals have no place here, I shall smite them when I move to guizero fully.
default_font = pygame.font.get_default_font()
font = pygame.font.Font(default_font,60)

debug_font = pygame.font.Font(default_font,40)

###LEGACY INPUTS
def take_input(): #legacy inputs; incompatible with main menu. honestly, these are like relics at this point, it would be shameful to remove them.
    while True:
        try:
            print('')
            
            inpx = float(input("ADD POINT X: "))
            inpy = float(input("ADD POINT Y: "))
            inpz = float(input("ADD POINT Z: "))
            
            break
        except:
            print("Invalid input.")
            pass
        
    point = Point([inpx,inpy,inpz])
    cbmod.add(point)
    

def take_input_plane():
    numoftimes = int(input("Enter how many points>>>"))
    a = []
    for i in range(numoftimes):
    
        while True:
            try:
                print('')
                
                inpx = float(input("ADD POINT X: "))
                inpy = float(input("ADD POINT Y: "))
                inpz = float(input("ADD POINT Z: "))
                
                break
            except:
                print("Invalid input.")
                pass
            
        point = Point([inpx,inpy,inpz])
        a.append(point)
        cbmod.add_plane(a,[])


###GRID SETUP
runtime_dis = display_3Dgrid([],0,0,0,1) # using disgrid module to setup a 3d environment
runtime_grid = display_3Dgrid(grid_points,0,0,0,2) # create another disgrid underlayed for the xyz axis



###INTERACTION BOOLS 
pointed = True
show_grid = True
show_points = True
rotatez = False
rotatey=False
rotatex=False

inv_rotatex = False
inv_rotatey = False


rotate_xyz = False

delete_on_click = False
up = False
down = False
left = False
right = False


#IMAGE-BASED PYG OBJECTS
menusym = pygame.image.load(f'{path.parent}/menusym.png')
menusym = pygame.transform.scale(menusym,(30,30))
menu_rect = menusym.get_rect()

plussym = pygame.image.load(f'{path.parent}/plussym.png')
plussym = pygame.transform.scale(plussym,(30,30))
plus_rect = plussym.get_rect()
plus_rect.x=70
plus_rect.y=30

###FULL DELETION/CUBE ADDITION
#to be removed
def clear():
    cbmod.delete_all()

def show_grid_lines():
    global show_grid
    show_grid = not show_grid

def place_example_cube():
    cbmod.add([-1,-1,1])
    cbmod.add([1,-1,1])
    cbmod.add([1,1,1])
    cbmod.add([-1,1,1])
    cbmod.add([-1,-1,-1])
    cbmod.add([1,-1,-1])
    cbmod.add([1,1,-1])
    cbmod.add([-1,1,-1])

def show_point():   
    global show_points
    show_points = not show_points

def place_example_plane_model():
    cbmod.add_plane([Point((-1,-1,-1)), Point((1,-1,-1)), Point((1,1,-1)), Point((-1,1,-1))], [0,1,1,2,0,3,2,3], (133, 98, 58), __glass)
    cbmod.add_plane([Point((-1,-1,1)),Point((1,-1,1)),Point((1,1,1)),Point((-1,1,1))], [0,1,1,2,0,3,2,3], (133, 98, 58), __glass)

    cbmod.add_plane([Point((-1,1,1)), Point((-1,1,-1)), Point((-1,-1,-1)), Point((-1,-1,1))], [0,1,1,2,0,3,2,3], (133, 98, 58))
    cbmod.add_plane([Point((1,1,1)), Point((1,1,-1)), Point((1,-1,-1)), Point((1,-1,1))], [0,1,1,2,0,3,2,3], (133, 98, 58))
    

    #[[1.0, -1.0, 1.0], [-1.0, -1.0, 1.0], [1.0, -1.0, -1.0], [-1.0, -1.0, -1.0]]
    cbmod.add_plane([Point((1,-1,1)), Point((-1,-1,1)), Point((-1,-1,-1)), Point((1,-1,-1))], [0,1,1,2,0,3,2,3], (133, 98, 58))
    cbmod.add_plane([Point((1,1,1)), Point((-1,1,1)), Point((-1,1,-1)), Point((1,1,-1))], [0,1,1,2,0,3,2,3], (133, 98, 58), __glass)

    cbmod.add_plane([Point((0.2,1,1)), Point((-0.2,1,1)), Point((-0.2,1,-1)), Point((0.2,1,-1))], [0,1,1,2,0,3,2,3], (214,164,107))
    cbmod.add_plane([Point((-0.2,0.2,-1)), Point((0.2,0.2,-1)), Point((0.2,1,-1)), Point((-0.2,1,-1))], [0,1,1,2,0,3,2,3], (214,164,107))
    cbmod.add_plane([Point((-0.2,0.2,1)),Point((0.2,0.2,1)),Point((0.2,1,1)),Point((-0.2,1,1))], [0,1,1,2,0,3,2,3], (214,164,107))


handler = Handler()
handler.menu = menu_screen

def createoptMenu():
    
    content = DisplayRows([
        Button(None,"clear model",None,None,clear).anchor(Anchor.LEFT),
        Button(None,"toggle grid lines",None,None,show_grid_lines).anchor(Anchor.LEFT),
        Button(None,"toggle points",None,None,show_point).anchor(Anchor.LEFT),
        Button(None,"place example cube",None,None,place_example_cube).anchor(Anchor.LEFT),
        Button(None,"place example model",None,None, place_example_plane_model).anchor(Anchor.LEFT)
    ])

    options_menu = GUIobj([0,0],[700,500],"cb3d menu")
    options_menu.add_content(content)

    return options_menu


###MOUSE INITS
mousepos = pygame.mouse.get_pos() #must init because we have newpos tracking
mx = mousepos[0]
my = mousepos[1]


###MAIN LOOP
while 1: 
    clock.tick(60) #runs at 60fps

    if not start_menu_shown:
    
        runtime_dis.project_points()
        
        
        for event in pygame.event.get():
            handler.handle_event(event,mx,my)
            
            match event.type:
                case pygame.QUIT:
                    cbmod.save_on_exit() #run a docs script here first, to add recents to globals, or whatever
                    pygame.quit()
                    exit()


                case pygame.KEYDOWN:
                    since_last_moved = 0
                    show_static_image=False
                    
                    
                    match event.key:

                        case pygame.K_LCTRL:
                            delete_on_click = True
                        case pygame.K_UP:
                            up = True
                        case pygame.K_DOWN:
                            down = True
                        case pygame.K_LEFT:
                            left = True
                        case pygame.K_RIGHT:
                            right = True
                        case pygame.K_z:
                            rotatez = True
                        case pygame.K_y:
                            rotatey=True
                        case pygame.K_x:
                            rotatex=True
                        case pygame.K_g:
                            if len(handler.GUIobjs_array) < 1:
                                show_grid = not show_grid
                        case pygame.K_p:
                            take_input()
                        case pygame.K_c:
                            cbmod.delete_all()
                        case pygame.K_h:
                            rotate_x = False
                            rotate_y = False
                            rotate_z = False
                            inv_rotatex = False
                            inv_rotatey = False
                            rotate_xyz = False
                            runtime_dis.update_angles(0,0)
                            runtime_grid.update_angles(0,0)
                            runtime_dis.angle_z=0
                            runtime_dis.angle_z=0
                            runtime_grid.angle_z=0
                            runtime_grid.angle_z=0
                            
                            runtime_dis.movable_position = [0,0]
                            runtime_grid.movable_position = [0,0]

                        case pygame.K_F9:
                            debug = not debug

                        case pygame.K_e:
                            if len(handler.GUIobjs_array) < 1:
                                
                                cbmod.add([-1,-1,1])
                                cbmod.add([1,-1,1])
                                cbmod.add([1,1,1])
                                cbmod.add([-1,1,1])

                                cbmod.add([-1,-1,-1])
                                cbmod.add([1,-1,-1])
                                cbmod.add([1,1,-1])
                                cbmod.add([-1,1,-1])

                        case pygame.K_m:
                            if len(handler.GUIobjs_array) < 1:
                                cbmod.add_plane([Point((-1,-1,-1)), Point((1,-1,-1)), Point((1,1,-1)), Point((-1,1,-1))], [0,1,1,2,0,3,2,3], (133, 98, 58))
                                cbmod.add_plane([Point((-1,-1,1)),Point((1,-1,1)),Point((1,1,1)),Point((-1,1,1))], [0,1,1,2,0,3,2,3], (133, 98, 58))

                                cbmod.add_plane([Point((-1,1,1)), Point((-1,1,-1)), Point((-1,-1,-1)), Point((-1,-1,1))], [0,1,1,2,0,3,2,3], (133, 98, 58))
                                cbmod.add_plane([Point((1,1,1)), Point((1,1,-1)), Point((1,-1,-1)), Point((1,-1,1))], [0,1,1,2,0,3,2,3], (133, 98, 58))
                                

                                #[[1.0, -1.0, 1.0], [-1.0, -1.0, 1.0], [1.0, -1.0, -1.0], [-1.0, -1.0, -1.0]]
                                cbmod.add_plane([Point((1,-1,1)), Point((-1,-1,1)), Point((-1,-1,-1)), Point((1,-1,-1))], [0,1,1,2,0,3,2,3], (133, 98, 58))
                                cbmod.add_plane([Point((1,1,1)), Point((-1,1,1)), Point((-1,1,-1)), Point((1,1,-1))], [0,1,1,2,0,3,2,3], (133, 98, 58))

                                cbmod.add_plane([Point((0.2,1,1)), Point((-0.2,1,1)), Point((-0.2,1,-1)), Point((0.2,1,-1))], [0,1,1,2,0,3,2,3], (214,164,107))
                                cbmod.add_plane([Point((-0.2,0.2,-1)), Point((0.2,0.2,-1)), Point((0.2,1,-1)), Point((-0.2,1,-1))], [0,1,1,2,0,3,2,3], (214,164,107))
                                cbmod.add_plane([Point((-0.2,0.2,1)),Point((0.2,0.2,1)),Point((0.2,1,1)),Point((-0.2,1,1))], [0,1,1,2,0,3,2,3], (214,164,107))
                                
                        case pygame.K_u:
                            if len(handler.GUIobjs_array) < 1:
                                cbmod.add_plane([Point((-1,-1,-1)), Point((1,-1,-1)), Point((1,1,-1)), Point((-1,1,-1))], [0,1,1,2,0,3,2,3], (25,175,200), catalogue.textures['wood'])
                                cbmod.add_plane([Point((-1,-1,1)),Point((1,-1,1)),Point((1,1,1)),Point((-1,1,1))], [0,1,1,2,0,3,2,3],        (25,175,200), catalogue.textures['wood'])

                                cbmod.add_plane([Point((-1,1,1)), Point((-1,1,-1)), Point((-1,-1,-1)), Point((-1,-1,1))], [0,1,1,2,0,3,2,3], (25,175,200), catalogue.textures['wood'])
                                cbmod.add_plane([Point((1,1,1)), Point((1,1,-1)), Point((1,-1,-1)), Point((1,-1,1))], [0,1,1,2,0,3,2,3],     (25,175,200), catalogue.textures['wood'])
                                

                                #[[1.0, -1.0, 1.0], [-1.0, -1.0, 1.0], [1.0, -1.0, -1.0], [-1.0, -1.0, -1.0]]
                                cbmod.add_plane([Point((1,-1,1)), Point((-1,-1,1)), Point((-1,-1,-1)), Point((1,-1,-1))], [0,1,1,2,0,3,2,3], (25,175,200), catalogue.textures['wood'])
                                cbmod.add_plane([Point((1,1,1)), Point((-1,1,1)), Point((-1,1,-1)), Point((1,1,-1))], [0,1,1,2,0,3,2,3],     (25,175,200), catalogue.textures['wood'])


                        case pygame.K_s:
                            if len(handler.GUIobjs_array) < 1:
                                show_points = not show_points
                            
                        case pygame.K_j:
                            savename = guizero.select_file("Save CBmodel",save=True,filetypes=[["CBmodels","*.CBmodel"]])
                            print(savename)
                            if savename == "":
                                pass
                            else:
                                cbmod.save(savename)
                                cbmod.filename_modified = savename
                    
                        case pygame.K_k:
                            if len(handler.GUIobjs_array) < 1:
                                savename = guizero.select_file("Open CBmodel",filetypes=[["CBmodels","*.CBmodel"]])
                                
                                if savename == "":
                                    pass #user has closed the file opener, so pass

                                else:

                                    cbmod = CBModel.load(savename)
                                    cbmod.filename_modified = savename
                                    
                        case pygame.K_ESCAPE:
                            start_menu_shown = True
                            pygame.image.save(dis,str(path)+'\\_preview.jpg')
                            handler.GUIobjs_array = []


                case pygame.KEYUP:
                    match event.key:
                        case pygame.K_LCTRL:
                            delete_on_click = False
                        case pygame.K_z:
                            rotatez = False
                        case pygame.K_y:
                            rotatey=False
                        case pygame.K_x:
                            rotatex=False
                        case pygame.K_UP:
                            up = False
                        case pygame.K_DOWN:
                            down = False
                        case pygame.K_LEFT:
                            left = False
                        case pygame.K_RIGHT:
                            right = False



                case pygame.MOUSEBUTTONDOWN:
                    since_last_moved = 0
                    show_static_image = False
                    if event.button == 3:
                        if delete_on_click:
                            
                            for point in runtime_dis.rendered_pointmap:
                                    if mx in range(round(point[0])-20,round(point[0])+20) and my in range(round(point[1])-20,round(point[1])+20):
                                        print('deleting point', str(runtime_dis.rendered_pointmap.index(point)))
                                        cbmod.delete(runtime_dis.rendered_pointmap.index(point))
                            if len(cbmod.planes) > 0:
                                for plane in cbmod.planes:
                                    for point in plane.render_points:
                                        if mx in range(round(point[0])-20,round(point[0])+20) and my in range(round(point[1])-20,round(point[1])+20):
                                            del cbmod.planes[cbmod.planes.index(plane)]
                                            break
                        
                        else:
                            rotate_xyz = True
                            
                            if rotatex:
                                rotatex = False
                            if rotatey:
                                rotatey = False
                            if inv_rotatex:
                                inv_rotatex = False
                            if inv_rotatey:
                                inv_rotatey = False
                    
                    #MOUSECLICKS

                    if event.button == 1:

                        
                        if mx in range(30,80) and my in range(30,90) and "cb3d menu" not in [i.title for i in handler.GUIobjs_array]:
                            handler.add(createoptMenu())
                        elif plus_rect.collidepoint(mx,my) and "add object" not in [i.title for i in handler.GUIobjs_array]:
                            
                            handler.add(draw)
                            draw.drawdata = []
                            
                                
                    

                        elif pointed == True:
                                
                            for point in runtime_dis.rendered_pointmap:
                                if mx in range(round(point[0])-20,round(point[0])+20) and my in range(round(point[1])-20,round(point[1])+20):
                                    cbmod.connected_points.append(runtime_dis.rendered_pointmap.index(point))
                    

                    

                case pygame.MOUSEBUTTONUP:
                    if event.button == 3:
                        rotate_xyz = False

                case pygame.MOUSEWHEEL:
                    since_last_moved = 0
                    show_static_image = False
                    if runtime_dis.scale <= 175: #max zoom constraint (otherwise you can zoom into negatives and crash)
                        
                        runtime_dis.update_scale(runtime_dis.scale-event.y*5) 
                    elif event.y > 0:
                        runtime_dis.update_scale(runtime_dis.scale-event.y*5)

                    
                    
        if left is True:
            runtime_dis.movable_position[0] -= 1
            runtime_grid.movable_position[0] -=1
        if right is True:
            runtime_dis.movable_position[0] += 1
            runtime_grid.movable_position[0] +=1
        if up is True:
            runtime_dis.movable_position[1] -= 1
            runtime_grid.movable_position[1] -=1
        if down is True:
            runtime_dis.movable_position[1] += 1
            runtime_grid.movable_position[1] +=1


        if rotatez is True:
            runtime_grid.angle_z +=0.01
            runtime_dis.angle_z+=0.01
            
        if rotatey is True:
            runtime_grid.angle_y += 0.01
            runtime_dis.angle_y += 0.01
        if rotatex is True:
            runtime_dis.angle_x +=0.01
            runtime_grid.angle_x+=0.01
        if inv_rotatey is True:
            runtime_grid.angle_y -= 0.01
            runtime_dis.angle_y -= 0.01
        if inv_rotatex is True:
            runtime_dis.angle_x -=0.01
            runtime_grid.angle_x -=0.01
                
        
        if rotate_xyz is True:
            since_last_moved = 0
            show_static_image=False
            newpos = pygame.mouse.get_pos()
            npmx = newpos[0]
            npmy = newpos[1]


            #boolean hell
            #positive movement (right and down)
            if npmx-mx > 40:
                rotatey = True
                if rotatex:
                    rotatex = False
            elif npmy-my > 40:
                rotatex = True
                if rotatey:
                    rotatey =False
            
            #negative movement (left and up)
            elif npmx-mx < -40:
                inv_rotatey = True
                if inv_rotatex:
                    inv_rotatex = False
            elif npmy-my < -40:
                inv_rotatex = True
                if inv_rotatey:
                    inv_rotatey = False
            
            else:
                rotatex = False
                rotatey = False
            
            runtime_grid.angle_y += (npmx-mx) /100
            runtime_grid.angle_x += (npmy-my) / 100
            
            runtime_dis.update_angles(runtime_dis.angle_x + ((npmy-my)/100),runtime_dis.angle_y + ((npmx-mx)/100))
        
        


        if not show_static_image:
            runtime_dis.point_map = cbmod.pointmap
            dis.fill((104, 157, 242))
            dis.blit(menusym,(30,30))
            dis.blit(plussym,(70,30))
            #print(pointmap)
            for point in runtime_dis.rendered_pointmap:
                point:Point
                if show_points is True:
                    gfxdraw.filled_circle(dis,int(round(point[0])),int(round(point[1])),int(round(20-runtime_dis.scale*0.1)),(0,0,0))


            if len(cbmod.connected_points) > 1:
                counter = 0
                for i in range(0,len(cbmod.connected_points)-1,2):
                    i-=counter
                    indextocheck = cbmod.connected_points[i]
                    second_index = cbmod.connected_points[i+1]
                    if indextocheck == second_index:
                        counter+=2
                        del cbmod.connected_points[i:i+2] #just checking that no two points match, it's inefficient to render lines with no length
                        
                    for point in runtime_dis.rendered_pointmap:
                        
                        
                        if runtime_dis.rendered_pointmap.index(point) == indextocheck:
                            try: # this is to ensure that lines aren't rendered while loading files (which while extremely rare, can occasionally happen when running on slow memory)
                                pygame.draw.line(dis,(0,0,0),runtime_dis.rendered_pointmap[indextocheck],runtime_dis.rendered_pointmap[second_index],width=abs(round(3.91-runtime_dis.scale/75)))
                                
                            except:
                                pass
            
            if len(cbmod.planes)>0:
                
                
                for plane in cbmod.planes:
                    
                    raw_renders,rendered_points = runtime_dis.plane_project(plane.points,(winsize[0]/2,winsize[1]/2)) #project planes
                    
                    plane.rpoints = list(raw_renders) 
                    plane.render_points = list(rendered_points)


                
                
                plane_dlists = []
                for a in cbmod.planes:
                    d_list = [runtime_dis.observer.calc_dist_topoint(distance) for distance in list(a.rpoints)] #distance calculaions
                    avg_distance = round( sum(d_list)/len(d_list), 4) #remove floating point imprecision
                    plane_dlists.append(avg_distance)
                    a.avg_distance = avg_distance
                
                
                plane_dlists = quicksort(plane_dlists) #sort the distances


                if debug:
                    plane_dlists_2REMOVELATER = [i for i in plane_dlists]
                
                
                for distance in plane_dlists:
                    if isinstance(distance,Plane):
                        pass
                    else:
                        for plane in cbmod.planes:
                            
                            if isinstance(distance,Plane):
                                pass
                            elif plane.avg_distance == distance:
                                plane_dlists[plane_dlists.index(distance)] = plane

                
    
                
                for pl in range(len(plane_dlists)):
                    plane = plane_dlists[pl]
                    
                    try: 
                        if debug: #debug stuff, ignore
                            text = debug_font.render(f" PLANE {plane_dlists[pl]}: " +str(plane_dlists_2REMOVELATER[pl]),False,(0,0,0))
                            dis.blit(text,plane.render_points[0])

                        else: #drawing the sides of the shape
                            if plane.texture:
                                if plane.texture.transparency != 1:
                                    plane.texture.texture_map.set_alpha(int(round(255*(plane.texture.transparency + (len(plane_dlists)- pl)*0.01))))
                                    
                                gfxdraw.textured_polygon(dis,plane.render_points,plane.texture.texture_map,plane.texture.tx,plane.texture.ty)
                                
                            else:
                                gfxdraw.filled_polygon(dis,plane.render_points,plane.colour)
                            
                        
                    except Exception as e:
                        print(e)
                    
                    for point in plane.render_points: #drawing the circle over the point
                        if show_points is True:
                            gfxdraw.filled_circle(dis,int(round(point[0])),int(round(point[1])),int(round(20-runtime_dis.scale*0.1)),(0,0,0))
                    
                    
                    for i in range(0,len(plane.connections)-1,2): #drawing connections
                        indextocheck = plane.connections[i]
                        second_index = plane.connections[i+1]
                        for point in plane.render_points:
                            
                            if plane.render_points.index(point) == indextocheck: 
                                #some indexes may not exist due to mistakes in constructing the plane, so this is a final check!
                                try: 
                                    pygame.draw.line(dis,(0,0,0),plane.render_points[indextocheck],plane.render_points[second_index],width=3)
                                except:
                                    pass
                
                if debug:
                    gfxdraw.filled_polygon(dis,plane_dlists[len(plane_dlists)-1].render_points,(255,0,0))
                    print(plane_dlists[len(plane_dlists)-1].render_points)

            
            if show_grid is True:
                runtime_grid.project_points()

                pygame.draw.line(dis,(255,0,0),runtime_grid.rendered_pointmap[0],runtime_grid.rendered_pointmap[1])
                pygame.draw.line(dis,(0,255,0),runtime_grid.rendered_pointmap[0],runtime_grid.rendered_pointmap[2])
                pygame.draw.line(dis,(0,0,255),runtime_grid.rendered_pointmap[0],runtime_grid.rendered_pointmap[3])
      
        else:
            dis.blit(curr_static_image, (0,0))
        

        if rotatex or rotatey or inv_rotatex or inv_rotatey or rotate_xyz:
            since_last_moved=0
            show_static_image=False
        else:
            since_last_moved+=1
            
        if since_last_moved >= 120: #120 ticks since last moved/2 seconds
            curr_static_image=dis
            show_static_image=True
        
        for event in handler.eventLog:
            
            if event[1] == Handler.Event.move or event[1] == Handler.Event.remove or event[1] == Handler.Event.click:
                since_last_moved=0
                show_static_image=False 


    else:
        
        
        for event in pygame.event.get():
            handler.handle_event(event,mx,my)
            for callback in handler.handle_menu_event(event,mx,my):
                if (callback[1] == 'load_file' and callback[0] != None) or callback[1] == 'open_saved' or callback[1] == 'new_file':
                    start_menu_shown=False
                    for dropdown in handler.menu.dropdowns:
                        dropdown.is_dropped=False

                elif callback[1] == 'show_instructions' and len([i for i in handler.GUIobjs_array if i.title=='keybinds']) == 0:
                    handler.add(createKeyMenu())
                
                 
                
                    
            
            
            match event.type:
                case pygame.QUIT:
                    cbmod.save_on_exit()
                    pygame.quit()
                    exit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            cbmod.save_on_exit()
                            pygame.quit()
                            exit()

                        case pygame.K_F9:
                            debug=not debug
                            

                    
                    
        
    
        menu_screen.display_window(dis)

    handler.display(dis)

    mousepos = pygame.mouse.get_pos()
    mx = mousepos[0]
    my = mousepos[1]

    ###DEBUG SPACE
    if debug:
        #gfxdraw.filled_polygon(dis,[(1093.0, 545.0), (925.0, 1020.0), (1635.0, 693.0), (1467.0, 1168.0)],(0,0,255)) #debug polygon, make plane shuffler to prevent these from happening
        print(f'{runtime_dis.scale} zoom scale factor')
        print(f'{since_last_moved} ticks since last moved')

        print(f'{show_static_image} image freeze state')

        print(f"rotatey state {rotatey}, rotatex state {rotatex}")
        print(f"inv states invrotatex {inv_rotatex}, invrotatey {inv_rotatey}")
        print(f"line thickness state {abs(round(3.91-runtime_dis.scale/75))}")
    
    pygame.display.update()