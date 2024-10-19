from utils.pgui import TextInput, Button, DisplayColumns, DisplayRows, GUIobj, Text, TextType, Image, Handler
import pygame

#basic pygame setup
pygame.init()
dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0]) 
clock = pygame.time.Clock()
handler=Handler()

#initializing a GUIobj to test
obj = GUIobj([200,200], [900,700],"contentblocks")
obj.add_content( 
     
     #the parent parameter must be a DisplayColumns or DisplayRows object
     DisplayRows([
          
          TextInput([0,0],'Test input'),
          Button([0,0],'Test button',None,None,lambda:print('button callback'))

     ])
)
x,y = pygame.mouse.get_pos()
handler.add(obj)
while 1: #main loop
     dis.fill((255,255,255))
     
     for event in pygame.event.get(): #monitoring events (to close the program)
          handler.handle_event(event,x,y)     
          if event.type == pygame.QUIT:
               pygame.quit()
               quit()
          elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

     handler.display(dis) #drawing the object with the new contentblock functionality
          

     x,y = pygame.mouse.get_pos()
     pygame.display.update()
     clock.tick(30)
     