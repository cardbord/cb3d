import pygame, guizero
from pathlib import Path
from cb3d_disgrid import menu_screen, display_3Dgrid, Button
from model import Point, CBModel

global cbmod

cbmod = CBModel.from_cblog() #return a new CBModel, or a pre-existing one from a previous cb3d runtime

path = Path(__file__).parent #just in case python refuses to locate model files, this is a slight problem since older versions of pygame are pretty fussy

grid_points = []
grid_points.append([0,0,0])
grid_points.append([10000,0,0])
grid_points.append([0,10000,0])
grid_points.append([0,0,10000])

#WINDOW_SIZE = 800 <- made fullscreen


winsize = pygame.display.get_desktop_sizes()[0]

answer = '' #these globals have no place here, I shall smite them when I move to guizero fully.
inputable = False
inputable_load = False
inputable_save = False
load_answer = ''
save_answer = ''
user_text = ''
input_rect = pygame.Rect(100, 450, 140, 56)
default_font = pygame.font.get_default_font()
font = pygame.font.Font(default_font,60)
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
    

#these are garbage, i'll make some guizero-based ones that aren't as horrible        
def take_input2():
    global answer
    global inputable
    inputable = True
    
def take_input_load():
    global load_answer
    global inputable_load
    inputable_load = True

def take_input_save():
    global save_answer
    global inputable_save
    inputable_save = True

    
def take_input_plane():
    numoftimes = int(input("Enter how many points>>>"))
    a = []
    for i in range(numoftimes):
    
        while True:
            try:
                print('')
                
                inpx = float(input("ADD POINT X: "))
                inpy = float(input("ADD POINT Y: "))
                
                break
            except:
                print("Invalid input.")
                pass
            
        point = Point([inpx,inpy,0])
        a.append(point)
        cbmod.add_plane(a,[])



runtime_dis = display_3Dgrid([],0,0,0,1) # using disgrid module to setup a 3d environment

runtime_grid = display_3Dgrid(grid_points,0,0,0,1) # create another disgrid underlayed for the xyz axis


pointed = True
show_grid = True
show_points = True
rotatez = False
rotatey=False
rotatex=False
rotate_xyz = False

delete_on_click = False
up = False
down = False
left = False
right = False



menusym = pygame.image.load(f'{path.parent}/menusym.png')
menusym = pygame.transform.scale(menusym,(30,30))
menu_rect = menusym.get_rect()

plussym = pygame.image.load(f'{path.parent}/plussym.png')
plussym = pygame.transform.scale(plussym,(30,30))
plus_rect = plussym.get_rect()


dis = pygame.display.set_mode((winsize[0],winsize[1]))
pygame.display.set_caption('cb3d','CBmodel engine')
clock = pygame.time.Clock()

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


commands = [
    #what is wrong with me why is this all manually placed
    Button(120,120,160,47,'CLEAR',clear),
    Button(120,168,400,47,f'SHOW GRID LINES: {show_grid}',show_grid_lines),
    Button(120,216,400,47,'PLACE EXAMPLE CUBE',place_example_cube),
    Button(120,264,320,47,f'SHOW POINTS: {show_points}',show_point),
    Button(120,312,320,47,'SAVE FILE',take_input_save),
    Button(120,360,320,47,'LOAD FILE',take_input_load),
    Button(120,408,320,47,'ADD POINT',take_input2),
    Button(120,456,320,47,'ADD PLANE',take_input_plane),

]
menu = menu_screen(False,commands)

mousepos = pygame.mouse.get_pos()
mx = mousepos[0]
my = mousepos[1]

while 1:
    clock.tick(75) #runs at 75fps

    runtime_dis.project_points((winsize[0]/2,winsize[1]/2))
    
    for event in pygame.event.get():
        if menu.active is True:
            for button in commands:
                button.when_clicked(event)
                if 'SHOW GRID' in button.text:
                    button.text = f'SHOW GRID LINES: {show_grid}'
                elif 'SHOW POINTS' in button.text:
                    button.text = f'SHOW POINTS: {show_points}'
        
        match event.type:
            case pygame.QUIT:
                cbmod.save_on_exit() #run a docs script here first, to add recents to globals, or whatever
                pygame.quit()
                quit()


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
                    elif inputable_save is True:
                        inputable_save = False
                        
                        name = user_text
                        user_text = ''
                        if name.lower() == 'exit':
                            pass
                        else:
                            with open(f'{path}/{name}.CBmodel','w') as writable:
                                
                                writable.write(str(cbmod.pointmap) + '\n')
                                writable.write(str(cbmod.connected_points)+ '\n')
                                writable.close()
                            print(f'SAVED {name}.CBmodel')

                    elif inputable_load is True:
                        inputable_load = False
                        name = user_text
                        user_text = ''
                        if name.lower() == 'exit':
                            pass
                        else:
                            
                            runtime_dis.point_map = []
                            try:
                                with open(f'{path}/{name}.CBmodel','r') as model:
                                    model_info = model.readlines()
                                    model_points = eval((model_info[0]).replace('\n',''))
                                    model_connections = eval((model_info[1]).replace('\n',''))

                                    
                                    model.close()
                                cbmod.connected_points = model_connections
                                cbmod.add(model_points)

                            except FileNotFoundError:
                                print(f'Could not find file {name}.CBmodel; please check your local files.')


                
                if event.key == pygame.K_BACKSPACE and (inputable is True or inputable_load is True or inputable_save is True):
                    user_text = user_text[:-1]

                        


                elif inputable is True or inputable_load is True or inputable_save is True:
                    user_text+=event.unicode
                else:
                    match event.key:
                        case pygame.K_0:
                            take_input_plane()
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
                            
                        case pygame.K_e:
                            
                            cbmod.add([-1,-1,1])
                            cbmod.add([1,-1,1])
                            cbmod.add([1,1,1])
                            cbmod.add([-1,1,1])
                            cbmod.add([-1,-1,-1])
                            cbmod.add([1,-1,-1])
                            cbmod.add([1,1,-1])
                            cbmod.add([-1,1,-1])


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
                            cbmod.save_on_exit()
                            pygame.quit()
                            exit()


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
                        print('attempting to delete')
                        for point in runtime_dis.rendered_pointmap:
                                if mx in range(round(point[0])-20,round(point[0])+20) and my in range(round(point[1])-20,round(point[1])+20):
                                    print('deleting point', str(runtime_dis.rendered_pointmap.index(point)))
                                    cbmod.delete(runtime_dis.rendered_pointmap.index(point))
                    else:
                        rotate_xyz = True
                
                
                #MOUSECLICKS

                if event.button == 1:

                    if menu.active is True:
                        
                        
                        if mx in range(30,80) and my in range(30,90):
                            menu.active = not menu.active
                            
                

                    elif pointed == True:
                        
                        
                        if mx in range(20,60) and my in range(20,60):
                            menu.active = not menu.active

                        elif mx in range(60,100) and my in range(20,60):
                            menu._commands[6]._command()
                            
                            
                        else:
                            for point in runtime_dis.rendered_pointmap:
                                if mx in range(round(point[0])-20,round(point[0])+20) and my in range(round(point[1])-20,round(point[1])+20):
                                    cbmod.connected_points.append(runtime_dis.rendered_pointmap.index(point))
                    

                

            case pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    rotate_xyz = False

            case pygame.MOUSEWHEEL:
                runtime_dis.scale -= event.y*5
                runtime_grid.scale -= event.y*5

    
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
        runtime_dis.angle_z +=0.01
        runtime_grid.angle_z +=0.01
    if rotatey is True:
        runtime_dis.angle_y +=0.01
        runtime_grid.angle_y += 0.01
    if rotatex is True:
        runtime_dis.angle_x +=0.01
        runtime_grid.angle_x+=0.01
    if rotate_xyz is True:
        
        newpos = pygame.mouse.get_pos()
        npmx = newpos[0]
        npmy = newpos[1]

        runtime_dis.angle_z += (npmx-mx) /100
        runtime_dis.angle_x += (npmy-my) /100
        runtime_grid.angle_z += (npmx-mx) /100
        runtime_grid.angle_x += (npmy-my) / 100
    
    runtime_dis.point_map = cbmod.pointmap
    dis.fill((104, 157, 242))
    dis.blit(menusym,(30,30))
    dis.blit(plussym,(70,30))
    #print(pointmap)
    for point in runtime_dis.rendered_pointmap:
        if show_points is True:
            pygame.draw.circle(dis,(0,0,0),point,20-runtime_dis.scale*0.1)
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
                        pygame.draw.line(dis,(0,0,0),runtime_dis.rendered_pointmap[indextocheck],runtime_dis.rendered_pointmap[second_index])
                    except:
                        pass
    
                    
    
    if show_grid is True:
        runtime_grid.project_points((winsize[0]/2,winsize[1]/2))

        pygame.draw.line(dis,(255,0,0),runtime_grid.rendered_pointmap[0],runtime_grid.rendered_pointmap[1])
        pygame.draw.line(dis,(0,255,0),runtime_grid.rendered_pointmap[0],runtime_grid.rendered_pointmap[2])
        pygame.draw.line(dis,(0,0,255),runtime_grid.rendered_pointmap[0],runtime_grid.rendered_pointmap[3])


    if menu.active is True:
        pygame.draw.rect(dis,(180,180,180),menu.menurect)
        menu.display(dis)

    if inputable is True:
        pygame.draw.rect(dis,pygame.Color('gray'),input_rect)
        
        text_surface = font.render(user_text,True,(255,255,255))
        dis.blit(text_surface,(input_rect.x+5,input_rect.y+5))
        input_rect.w = max(100,text_surface.get_width()+10)
    
    if inputable_load is True:
        pygame.draw.rect(dis,pygame.Color('gray'),input_rect)
        text_surface = font.render(user_text,True,(255,255,255))
        dis.blit(text_surface,(input_rect.x+5,input_rect.y+5))
        input_rect.w = max(100,text_surface.get_width()+10)

    if inputable_save is True:
        pygame.draw.rect(dis,pygame.Color('gray'),input_rect)
        text_surface = font.render(user_text,True,(255,255,255))
        dis.blit(text_surface,(input_rect.x+5,input_rect.y+5))
        input_rect.w = max(100,text_surface.get_width()+10)

    mousepos = pygame.mouse.get_pos()
    mx = mousepos[0]
    my = mousepos[1]

    print(runtime_grid.angle_x,runtime_grid.angle_z)

    pygame.display.update()
    
    
    