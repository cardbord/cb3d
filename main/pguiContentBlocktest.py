from utils.pgui import TextInput, Button, DisplayColumns, DisplayRows, GUIobj, calc_rel_size
import pygame

pygame.init()

obj = GUIobj([200,200], [800,400],"content block test")
obj.add_content(
     DisplayRows([
          DisplayColumns(
               [
                    Button([0,0],'hey'),
                    Button([0,0],'hi')
               ]
          ),
          
          TextInput([0,0],"test TextInput"),
          Button([0,0],"test button"),
          ],
     )
)


dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])
size_Sf = calc_rel_size()




print("STARTING MAIN LOOP")
xy = pygame.mouse.get_pos()
x,y = xy[0], xy[1]
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

     obj.display_window(dis)
          
     x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
     pygame.display.update()