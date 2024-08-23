from utils.pgui import TextInput, Button, DisplayColumns, DisplayRows, GUIobj, Text, TextType, Image
import pygame

#basic pygame setup
pygame.init()
dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0]) 
clock = pygame.time.Clock()


#initializing a GUIobj to test
obj = GUIobj([200,200], [900,700],"contentblocks")
obj.add_content( 
     
     #the parent parameter must be a DisplayColumns or DisplayRows object
     DisplayRows([
          Image([0,0],'boxo.png'), #filename, looked for in cb3d\main\utils\content\...

          Image([0,0],'W:\\downloads-copied\\other_boxo.jpg'), #full filename

          Image([0,0],'https://www.boxo.ovh/cat_boxo') #not a direct link! this redirects to an image on the same site

     ])
)

while 1: #main loop
     dis.fill((255,255,255))
     
     for event in pygame.event.get(): #monitoring events (to close the program)
          
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