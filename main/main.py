import pygame

from main_attrs import menu_screen, display_3Dgrid, Button
global points
global connected_points
points = []
WINDOW_SIZE = 800
answer = ''
inputable = False
inputable_load = False
inputable_save = False
load_answer = ''
save_answer = ''
user_text = ''
input_rect = pygame.Rect(350, 350, 140, 56)
default_font = pygame.font.get_default_font()
font = pygame.font.Font(default_font,60)
def take_input():
    while True:
        try:
            print('    ')
            
            inpx = float(input("ADD POINT X: "))
            inpy = float(input("ADD POINT Y: "))
            inpz = float(input("ADD POINT Z: "))
            break
        except:
            print("Invalid input.")
            pass
        
    point = [inpx,inpy,inpz]
    
    points.append(point)
        
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



grid_points = []
grid_points.append([0,0,0])
grid_points.append([10000,0,0])
grid_points.append([0,10000,0])
grid_points.append([0,0,10000])

scale = 1

connected_points = []
connect_circle = []

runtime_dis = display_3Dgrid(points,0,0,0,scale)

runtime_grid = display_3Dgrid(grid_points,0,0,0,scale)

circled = False
pointed = True
show_grid = True
pos = (0,0)
mouse_values = [0,0]
show_points = True
rotatez = False
rotatey=False
rotatex=False
rotate_xyz = False
done = False


up = False
down = False
left = False
right = False



defualt_position = [WINDOW_SIZE/2,WINDOW_SIZE/2]

dis = pygame.display.set_mode((WINDOW_SIZE,WINDOW_SIZE))
pygame.display.set_caption('CBmodeller','CBmodel engine')
menusym = pygame.image.load('menusym.png')
menusym = pygame.transform.scale(menusym,(30,30))
menu_rect = menusym.get_rect()
icon = pygame.image.load('icon.PNG')
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

def clear():
    global points
    global connected_points
    points = []
    connected_points = []
    runtime_dis.point_map = []


def show_grid_lines():
    global show_grid
    show_grid = not show_grid

def place_example_cube():
    global points
    global connected_points
    points = []
    connected_points = []
    runtime_dis.point_map = []
    


    points.append([-1,-1,1])
    points.append([1,-1,1])
    points.append([1,1,1])
    points.append([-1,1,1])
    points.append([-1,-1,-1])
    points.append([1,-1,-1])
    points.append([1,1,-1])
    points.append([-1,1,-1])

def show_point():
    global show_points
    show_points = not show_points

def passer():
    pass


commands = [

    Button(120,120,160,47,'CLEAR',clear),
    Button(120,168,400,47,f'SHOW GRID LINES: {show_grid}',show_grid_lines),
    Button(120,216,400,47,'PLACE EXAMPLE CUBE',place_example_cube),
    Button(120,264,320,47,f'SHOW POINTS: {show_points}',show_point),
    Button(120,312,320,47,'SAVE FILE',passer),
    Button(120,360,320,47,'LOAD FILE',passer),
    Button(120,408,320,47,'ADD POINT',take_input2)

]


menu = menu_screen(False,commands)



while not done:
    clock.tick(60)
    pointmap = runtime_dis.project_points((WINDOW_SIZE/2,WINDOW_SIZE/2))
    
    for event in pygame.event.get():
        if menu.active is True:
            for button in commands:
                button.when_clicked(event)
                if 'SHOW GRID' in button.text:
                    button.text = f'SHOW GRID LINES: {show_grid}'
                elif 'SHOW POINTS' in button.text:
                    button.text = f'SHOW POINTS: {show_points}'

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()


        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_RETURN:
                if inputable is True:
                    inputable = False
                    
                    answer = user_text
                    try:
                        answer = answer.split(',')
                        a = [float(x) for x in answer]
                        points.append(a)
                    except:
                        pass
                    user_text = ''
                elif inputable_save is True:
                    name = user_text
                    if name.lower() == 'exit':
                        pass
                    else:
                        with open(f'{name}.CBmodel','w') as writable:
                            
                            writable.write(str(points) + '\n')
                            writable.write(str(connected_points)+ '\n')
                            writable.close()
                        print(f'SAVED {name}.CBmodel')

                elif inputable_load is True:
                    name = user_text
                    if name.lower() == 'exit':
                        pass
                    else:
                        points = []
                        connected_points = []
                        runtime_dis.point_map = []
                        try:
                            with open(f'{name}.CBmodel','r') as model:
                                model_info = model.readlines()
                                model_points = eval((model_info[0]).replace('\n',''))
                                model_connections = eval((model_info[1]).replace('\n',''))

                                
                                model.close()
                            connected_points = model_connections
                            points = model_points

                        except FileNotFoundError:
                            print(f'Could not find file {name}.CBmodel; please check your local files.')


            
            if event.key == pygame.K_BACKSPACE and inputable is True:
                user_text = user_text[:-1]


            elif inputable is True or inputable_load is True or inputable_save is True:
                user_text+=event.unicode
            else:
                if event.key == pygame.K_UP:
                    up = True
                if event.key == pygame.K_DOWN:
                    down = True
                if event.key == pygame.K_LEFT:
                    left = True
                if event.key == pygame.K_RIGHT:
                    right = True
                if event.key == pygame.K_z:
                    rotatez = True
                if event.key == pygame.K_y:
                    rotatey=True
                if event.key == pygame.K_x:
                    rotatex=True
                
                if event.key == pygame.K_o:
                    print('CIRCLE TOGGLED')
                    pointed = not pointed
                    circled = not circled

                if event.key == pygame.K_g:
                    show_grid = not show_grid

                if event.key == pygame.K_p:
                    take_input()
                if event.key == pygame.K_c:
                    points = []
                    connected_points = []
                    runtime_dis.point_map = []
                if event.key == pygame.K_e:
                    points = []
                    connected_points = []
                    runtime_dis.point_map = []

                    points.append([-1,-1,1])
                    points.append([1,-1,1])
                    points.append([1,1,1])
                    points.append([-1,1,1])
                    points.append([-1,-1,-1])
                    points.append([1,-1,-1])
                    points.append([1,1,-1])
                    points.append([-1,1,-1])
                if event.key == pygame.K_s:
                    show_points = not show_points
                if event.key == pygame.K_j:
                    name = input("ENTER SAVE FILE NAME (EXIT TO EXIT)>>>")
                    if name.lower() == 'exit':
                        pass
                    else:
                        with open(f'{name}.CBmodel','w') as writable:
                            
                            writable.write(str(points) + '\n')
                            writable.write(str(connected_points)+ '\n')
                            writable.close()
                        print(f'SAVED {name}.CBmodel')
                
                if event.key == pygame.K_k:
                    
                    name = input("ENTER FILENAME (EXIT TO EXIT) >>>")
                    if name.lower() == 'exit':
                        pass
                    else:
                        points = []
                        connected_points = []
                        runtime_dis.point_map = []
                        try:
                            with open(f'{name}.CBmodel','r') as model:
                                model_info = model.readlines()
                                model_points = eval((model_info[0]).replace('\n',''))
                                model_connections = eval((model_info[1]).replace('\n',''))

                                
                                model.close()
                            connected_points = model_connections
                            points = model_points

                        except FileNotFoundError:
                            print(f'Could not find file {name}.CBmodel; please check your local files.')




        if event.type == pygame.KEYUP:
            if event.key == pygame.K_z:
                rotatez = False
            if event.key == pygame.K_y:
                rotatey=False
            if event.key == pygame.K_x:
                rotatex=False

            if event.key == pygame.K_UP:
                up = False
            if event.key == pygame.K_DOWN:
                down = False
            if event.key == pygame.K_LEFT:
                left = False
            if event.key == pygame.K_RIGHT:
                right = False



        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                rotate_xyz = True
            
            
            #MOUSECLICKS

            if event.button == 1:

                if menu.active is True:
                    mousepos = pygame.mouse.get_pos()
                    mx = mousepos[0]
                    my = mousepos[1]
                    if mx in range(30,80) and my in range(30,90):
                        menu.active = not menu.active
                        


                elif pointed == True:
                    mousepos = pygame.mouse.get_pos()
                    mx = mousepos[0]
                    my = mousepos[1]
                    if mx in range(30,80) and my in range(30,90):
                        menu.active = not menu.active
                        
                        
                    else:
                        for point in pointmap:
                            if mx in range(round(point[0])-20,round(point[0])+20) and my in range(round(point[1])-20,round(point[1])+20):
                                connected_points.append(pointmap.index(point))
                elif circled == True:
                    mousepos = pygame.mouse.get_pos()
                    mx = mousepos[0]
                    my = mousepos[1]
                    for point in pointmap:
                        if mx in range(round(point[0])-20,round(point[0])+20) and my in range(round(point[1])-20,round(point[1])+20):
                            point_index = pointmap.index(point)
                            connect_circle.append(point_index)

                

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                
                
                rotate_xyz = False

        if event.type == pygame.MOUSEWHEEL:
            scale -= event.y*5
            runtime_dis.scale = scale
            runtime_grid.scale = scale

    
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
        pos = pygame.mouse.get_pos()
        

        runtime_dis.angle_z = pos[0] /100
        runtime_dis.angle_x = pos[1] /100
        runtime_grid.angle_z = pos[0] /100
        runtime_grid.angle_x = pos[1] / 100
    
    runtime_dis.point_map = points
    dis.fill((104, 157, 242))
    dis.blit(menusym,(30,30))
    #print(pointmap)
    for point in pointmap:
        if show_points is True:
            pygame.draw.circle(dis,(0,0,0),point,20-runtime_dis.scale*0.1)
    if len(connected_points) > 1:
        
        for i in range(0,len(connected_points)-1,2):
            indextocheck = connected_points[i]
            second_index = connected_points[i+1]
            for point in pointmap:
                
                if pointmap.index(point) == indextocheck:
                    try:
                        pygame.draw.line(dis,(0,0,0),pointmap[indextocheck],pointmap[second_index])
                    except:
                        pass
    if len(connect_circle) > 3:

        for i in range(0,len(connect_circle)-1,4):
            indextocheck = connect_circle[i]
            second_index = connect_circle[i+1]
            third_index = connect_circle[i+2]
            fourth_index = connect_circle[i+3]



            for point in pointmap:

                if pointmap.index(point) == indextocheck:
                    width = pointmap[second_index][0] - pointmap[indextocheck][0]
                    
                    height = pointmap[second_index][1] - pointmap[second_index][1]
                    
                    
    
    if show_grid is True:
        grid_lines = runtime_grid.project_points((WINDOW_SIZE/2,WINDOW_SIZE/2))

        pygame.draw.line(dis,(255,0,0),grid_lines[0],grid_lines[1])
        pygame.draw.line(dis,(0,255,0),grid_lines[0],grid_lines[2])
        pygame.draw.line(dis,(0,0,255),grid_lines[0],grid_lines[3])


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
        input_rect.w = max(100,text_surface)

    if inputable_save is True:
        pygame.draw.rect(dis,pygame.Color('gray'),input_rect)
        text_surface = font.render(user_text,True,(255,255,255))
        dis.blit(text_surface,(input_rect.x+5,input_rect.y+5))
        input_rect.w = max(100,text_surface)



    pygame.display.update()
    