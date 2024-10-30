from utils import pgui
import pygame

'''
mimics pguitest.py and pguiContentBlocks.py, but makes use of the GUIobj Handler class to abstract 
-all obj movement
-textinput additions
-window priority
-button clicks
away from the main program
'''

#basic pygame and pgui handler setup
handler = pgui.Handler()
pygame.init()
dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])

#object generation function
def generate_object(): 
    obj = pgui.GUIobj([200,200], [900,700],"contentblocks")
    obj.add_content( 
        
        #the parent parameter must be a DisplayColumns or DisplayRows object
        pgui.DisplayRows([
            pgui.TextInput([0,0],'Test input'),
            pgui.TextInput([0,0],'Test input 2'),
            pgui.Button([0,0],'Test button',None,None,lambda:print('button callback'))
        ])
    )
    return obj

handler.add(generate_object())

x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]

while 1:
    dis.fill((255,255,255))
    for event in pygame.event.get():
        handler.handle_event(event,x,y)
        #within this loop, it is beneficial to feed the event through pgui's handler 
        #it's far better than running two event loops at once
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
            elif event.key == pygame.K_DELETE:
                handler.add(generate_object())
        
            
    handler.display(dis)
    pygame.display.flip()
    x,y = pygame.mouse.get_pos()