from utils import pgui
import pygame

'''
copied from pguiHandlerTest.py, just implementing a Drawing object specifically
'''

#will add to plane_sorter in utils when done



def transform(points:list, draw_plane:str,extrusion:str='0',zerodisplacement:str='0'):
    plane_array = []
    extrusion=float(extrusion)
    zerodisplacement=float(zerodisplacement)
    match draw_plane:
        case 'xy':
            extruded_plane=[]
            for point in points:
                extruded_plane.append([point[0],point[1],zerodisplacement])
            plane_array.append(extruded_plane)

            for i in range(1,len(points)):
                side_plane = []
                side_plane.append([[points[i][0],points[i][1],zerodisplacement], [points[i][0],points[i][1],extrusion+zerodisplacement], [points[i-1][0],points[i-1][1],zerodisplacement], [points[i-1][0],points[i-1][1],extrusion+zerodisplacement]])
                plane_array.append(side_plane)
            side_plane = []
            side_plane.append([[points[-1][0],points[-1][1],zerodisplacement], [points[-1][0],points[-1][1],extrusion+zerodisplacement], [points[0][0],points[0][1],zerodisplacement], [points[0][0],points[0][1],extrusion+zerodisplacement]])
            plane_array.append(side_plane)

        case 'xz':
            extruded_plane = []
            for point in points:
                extruded_plane.append([point[0],zerodisplacement,point[1]])
            plane_array.append(extruded_plane)


            for i in range(1,len(points)):
                side_plane = []
                side_plane.append([[points[i][0],zerodisplacement,points[i][1]], [points[i][0],extrusion+zerodisplacement,points[i][1]], [points[i-1][0],zerodisplacement,points[i-1][1]], [points[i-1][0],extrusion+zerodisplacement,points[i-1][1]]])
                plane_array.append(side_plane)
            side_plane = []
            side_plane.append([[points[-1][0],zerodisplacement,points[-1][1]], [points[-1][0],extrusion+zerodisplacement,points[-1][1]], [points[0][0],zerodisplacement,points[0][1]], [points[0][0],extrusion+zerodisplacement,points[0][1]]])
            plane_array.append(side_plane)
        
        case 'yz':
            extruded_plane = []
            for point in points:
                extruded_plane.append([zerodisplacement,point[0],point[1]])
            plane_array.append(extruded_plane)


            for i in range(1,len(points)):
                side_plane = []
                side_plane.append([[zerodisplacement,points[i][0],points[i][1]], [extrusion+zerodisplacement,points[i][0],points[i][1]], [zerodisplacement,points[i-1][0],points[i-1][1]], [extrusion+zerodisplacement,points[i-1][0],points[i-1][1]]])
                plane_array.append(side_plane)
            side_plane = []
            side_plane.append([[zerodisplacement,points[-1][0],points[-1][1]], [extrusion+zerodisplacement,points[-1][0],points[-1][1]], [zerodisplacement,points[0][0],points[0][1]], [extrusion+zerodisplacement,points[0][0],points[0][1]]])
            plane_array.append(side_plane)
            
    

        
def buildTransform(points,planetype):
    input_options = h3.collate_textinput_inputs()
    print(input_options)
    print(transform(points,planetype,input_options['Extrusion'],input_options['From']))

def demoChildXYZselector(points): #this is implemented inside run_3d.py
    d = pgui.GUIobj([0,0],[452,1000],'demochildXYZselector')
    d.points = points

    

    d.add_content(
        
        pgui.DisplayRows([
            pgui.Image([0,0],'boxo_xy.png').set_callback(lambda: buildTransform(d.points,'xy')),
            pgui.Image([0,0],'boxo_xz.png').set_callback(lambda:buildTransform(d.points,'xz')),
            pgui.Image([0,0],'boxo_yz.png').set_callback(lambda:buildTransform(d.points,'yz')),
            pgui.DisplayRows([
                None,
                pgui.DisplayColumns([
                    pgui.Text([0,0],'From',pgui.TextType.h3),None
                ]), 
                
                pgui.TextInput([0,0],'','0',1,'From'),
                None
            ]),
            
            pgui.DisplayRows([
                None,
                pgui.DisplayColumns([
                    pgui.Text([0,0],'Extrusion',pgui.TextType.h3),None
                ]), 
                pgui.TextInput([0,0],'','0',1,'Extrusion'),
                None
            ])
            
            
            #we use the anonymous function lambda: cbmod.add_plane(buildTransform(d.points,planetype), [], texture) in the real thing
        ]),
            
        
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
    
    for event in h3.eventLog:
        print(event)
    
    h3.display(dis)
    pygame.display.flip()
    x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]