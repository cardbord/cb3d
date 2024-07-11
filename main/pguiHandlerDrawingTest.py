from utils import pgui
import pygame

'''
mimics pguitest.py in functionality, but makes use of the GUIobj Handler class to abstract all obj movement/textinput additions/window priority away from the main program.
'''

draw = pgui.Drawing([0,0],[800,800],"add object")

h3 = pgui.Handler()

h3.add(draw)
pygame.init()
dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])
x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
while 1:
    dis.fill((0,0,0))
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
    
    draw.on_hover(x,y)
    h3.display(dis)
    pygame.display.flip()
    x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]