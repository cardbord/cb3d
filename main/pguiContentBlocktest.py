from utils.pgui import TextInput, Button, DisplayColumns, DisplayRows, GUIobj, Text, TextType
import pygame

#basic pygame setup
pygame.init()
dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0]) 
clock = pygame.time.Clock()


#initializing a GUIobj to test
obj = GUIobj([200,200], [900,700],"contentblocks")
obj.add_content( 
     
     #the parent parameter must be a DisplayColumns or DisplayRows object
     DisplayColumns([
          DisplayRows([
               Text([0,0],'test header 1',TextType.h1,colour=(255,0,0),ul=True,bold=True,font='comic sans ms'),
               Text([0,0],'test header 2',TextType.h2,colour=(0,255,0),italic=True, font='Segoe UI'),
               Text([0,0],"this shouldn't be here...",TextType.p,strikethrough=True, font='calibri')
          ]),

          Text([0,0],"i'm over here!",TextType.h3, font='consolas', colour=(0,0,255))
     
     ])
)


while 1: #main loop
     dis.fill((255,255,255))
     
     for event in pygame.event.get():
          
          if event.type == pygame.QUIT:
               pygame.quit()
               quit()
          elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

     obj.display_window(dis) #drawing the object with the new contentblock functionality
          

     pygame.display.update()
     clock.tick(30)