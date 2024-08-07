#NECESSARY IMPORTS
import pygame, guizero


###DISPLAY SETUP
pygame.init()
winsize = pygame.display.get_desktop_sizes()[0]
dis = pygame.display.set_mode((winsize[0],winsize[1]))
pygame.display.set_caption('cb3d','CBmodel engine')
clock = pygame.time.Clock()

#OTHER IMPORTS
from pathlib import Path
from cb3d_disgrid import display_3Dgrid
from model import Point, CBModel, Plane
from pygame import gfxdraw
from utils.plane_sorter import quicksort, transform
from utils.pgui import Text, TextType, Anchor, Button, TextInput, Dropdown, menu, Drawing, DisplayColumns, DisplayRows, Image, Handler, GUIobj, scale_to_window
from utils.textures.textureCatalogue import TextureCatalogue
from webbrowser import open_new_tab



#REMOVELATER
a = TextureCatalogue()
__glass = a.textures['glass']


###GLOBALS

debug = False #SET FALSE WHEN NOT TESTING (can be toggled through F9)
start_menu_shown = True
since_last_moved = 0
curr_static_image = None
show_static_image = False

global cbmod

path = Path(__file__).parent #just in case python refuses to locate model files, this is a slight problem since older versions of pygame are pretty fussy
cbmod, successful_load = CBModel.from_cblog() #return a new CBModel, or a pre-existing one from a previous cb3d runtime

if successful_load: #if saved normally, there should be a preview for it
    pass


with open(str(path.parent)+'\\_globals.cblog','r') as version_doc:
    __VERSION = version_doc.read().replace("'","")
    version_doc.close()

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


def buildTransform(points,planetype):
    input_options = handler.collate_textinput_inputs()
    
    transformations = transform(points,planetype,input_options['Extrusion'],input_options['From'])

    for transformation in transformations:
        if len(transformation) == 4:
            cbmod.add_plane(transformation, [0,1,0,3,1,2,2,3], None, None)
        else:

            cbmod.add_plane(transformation, [i for i in range(len(transformation))], None, None)



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
    
    _File = Dropdown([0,0], Button([0,0],"File",[200,50],(10,10,10)), file_list)#place button list in sq brackets
    _Help = Dropdown([scale_to_window(200),0], Button([scale_to_window(200),0],"Help",[200,50],(10,10,10)), help_list) 

    

    start_menu = menu(
        [
            _File,
            _Help
        ]
    )
   
    _menu_content = DisplayColumns(
        [

            DisplayRows(
                [
                    Text([0,0],f'cb3d v{__VERSION}',TextType.h1,font="Segoe UI",bold=True,colour=(214,164,107)),
                    DisplayRows(
                        [
                            Text([0,0],'hit "file" to get started',TextType.h2, font="comic sans ms"),
                            Text([0,0],'or hit "help" for some useful info',TextType.h2, font="comic sans ms"),
                            None
                        ]
                    ),
                    None
                ]
            ),
            DisplayRows(
                [
                    Image([0,0],"backg.jpg"),
                ]
            )
        ]
    )
                                         
    
    start_menu.add_content(_menu_content)
    
    return start_menu


menu_screen = createMenu()

def ChildXYZselector(points) -> GUIobj: #this is implemented inside run_3d.py
    selector = GUIobj([0,0],[452,1000],'Draw to')
    selector.points = []
    for i in points:
        if i not in selector.points:
            selector.points.append(i)
    
    print(selector.points)

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
                None
            ]),
            
            DisplayRows([
                None,
                DisplayColumns([
                    Text([0,0],'Extrusion',TextType.h3),None
                ]), 
                TextInput([0,0],'','0',1,'Extrusion'),
                None
            ])
            
            
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
                    
                    if event.key == pygame.K_RETURN:
                        if inputable is True:
                            inputable = False
                            
                            answer = user_text
                            try:
                                answer = answer.split(',')
                                a = [float(x) for x in answer]
                                
                                a = Point(a)
                                cbmod.add([a])
                            except Exception as e:
                                print(e)
                            user_text = ''    


                    
                    else:
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
                                
                                cbmod.add([-1,-1,1])
                                cbmod.add([1,-1,1])
                                cbmod.add([1,1,1])
                                cbmod.add([-1,1,1])

                                cbmod.add([-1,-1,-1])
                                cbmod.add([1,-1,-1])
                                cbmod.add([1,1,-1])
                                cbmod.add([-1,1,-1])

                            case pygame.K_m:
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
                                


                            case pygame.K_s:
                                show_points = not show_points
                                
                            case pygame.K_j:
                                savename = guizero.select_file("Save CBmodel",save=True,filetypes=[["CBmodel","*.CBmodel"]])
                                print(savename)
                                if savename == "":
                                    pass
                                else:
                                    cbmod.save(savename)
                                    cbmod.filename_modified = savename
                        
                            case pygame.K_k:
                                savename = guizero.select_file("Open cbmodel",filetypes=[["CBmodels","*.CBmodel"]])
                                
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
                #sorter
                
                for plane in cbmod.planes:
                    
                    raw_renders,rendered_points = runtime_dis.plane_project(plane.points,(winsize[0]/2,winsize[1]/2))
                    
                    plane.rpoints = list(raw_renders)
                    plane.render_points = list(rendered_points)
                #cbmod.planes = quicksort(runtime_dis,cbmod.planes)
                #condition for sorting: sum([runtime_dis.observer.calc_dist_topoint(runtime_dis.rendered_pointmap[i]) for i in plane[1]])/len(plane[1])
                
                
                plane_dlists = []
                for a in cbmod.planes:
                    d_list = [runtime_dis.observer.calc_dist_topoint(distance) for distance in list(a.rpoints)]
                    avg_distance = round( sum(d_list)/len(d_list), 4) #remove floating point imprecision
                    plane_dlists.append(avg_distance)
                    a.avg_distance = avg_distance
                
                
                plane_dlists = quicksort(plane_dlists)
                
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
                        if debug:
                            text = debug_font.render(f" PLANE {plane_dlists[pl]}: " +str(plane_dlists_2REMOVELATER[pl]),False,(0,0,0))
                            dis.blit(text,plane.render_points[0])
                        else:
                            if plane.texture:
                                if plane.texture.transparency != 1:
                                    plane.texture.texture_map.set_alpha(int(round(255*(plane.texture.transparency + (len(plane_dlists)- pl)*0.01))))
                                    
                                gfxdraw.textured_polygon(dis,plane.render_points,plane.texture.texture_map,plane.texture.tx,plane.texture.ty)
                                
                            else:
                                gfxdraw.filled_polygon(dis,plane.render_points,plane.colour)
                            
                        
                    except Exception as e:
                        print(e)
                    
                    for point in plane.render_points:
                        if show_points is True:
                            gfxdraw.filled_circle(dis,int(round(point[0])),int(round(point[1])),int(round(20-runtime_dis.scale*0.1)),(0,0,0))
                    
                    
                    for i in range(0,len(plane.connections)-1,2):
                        indextocheck = plane.connections[i]
                        second_index = plane.connections[i+1]
                        for point in plane.render_points:
                            
                            if plane.render_points.index(point) == indextocheck:
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