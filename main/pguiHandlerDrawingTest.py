from utils import pgui
import pygame

'''
copied from pguiHandlerTest.py, just implementing a Drawing object specifically
'''

#will add to plane_sorter in utils when done
def transform(points:list, draw_plane:str,extrusion:int=None):
    p_array = []
    add_extrude = False
    if extrusion != None:
        add_extrude = True
    
    match draw_plane:
        case 'xy':
            for point in points:
                p_array.append([point[0],point[1],0])
                if add_extrude:
                    p_array.append([point[0],point[1],extrusion])
        case 'xz':
            for point in points:
                p_array.append([point[0], 0, point[1]])
                if add_extrude:
                    p_array.append([point[0],extrusion,point[1]])
        case 'yz':
            for point in points:
                p_array.append([0, point[0], point[1]])
                if add_extrude:
                    p_array.append([extrusion,point[0],point[1]])
                
    return p_array 
        

def demoChildXYZselector(points): #this is implemented inside run_3d.py
    d = pgui.GUIobj([0,0],[200,600],'test')
    d.points = points
    d.add_content(
        pgui.DisplayRows([
            pgui.Image([0,0],'boxo.png').set_callback(lambda: print(transform(d.points,'xy'))), #these will be custom 200x200 images i'll make later. for now... boxo.png!
            pgui.Image([0,0],'boxo.png').set_callback(lambda: print(transform(d.points,'xz'))),
            pgui.Image([0,0],'boxo.png').set_callback(lambda: print(transform(d.points,'yz')))
            
            #we use the anonymous function lambda: cbmod.add_plane(transform(d.points,planetype), [], texture) in the real thing
        ])
    )
    return d


draw = pgui.Drawing([0,0],[800,800],"add object")
draw.draw_button.callback = demoChildXYZselector

h3 = pgui.Handler()

h3.add(draw)
pygame.init()
dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])
x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
while 1:
    dis.fill((255,255,255))
    for event in pygame.event.get():
        h3.handle_event(event,x,y)

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
            
                
            
            #within this loop, it is beneficial to provide the event, and then feed it through pgui's handler. it's far better than running two event loops at once
    
    
    h3.display(dis)
    pygame.display.flip()
    x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]