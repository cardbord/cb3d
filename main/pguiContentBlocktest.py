from utils.pgui import TextInput, Button, DisplayColumns, DisplayRows, GUIobj, calc_rel_size, Handler, Anchor
import pygame

eventHandler = Handler()

pygame.init()

obj = GUIobj([200,200], [1400,1000],"content block test")
obj.add_content(
     DisplayColumns(
               
               [
                    
                    DisplayRows(
                         [
                              Button([0,0],"hello"),
                              Button([0,0],"hello2").anchor(Anchor.CENTER)
                         ]
                    ),
                    
                    DisplayRows(
                         [
                              Button([0,0],"helo2"),
                              Button([0,0],"hello3")
                         ]
                    )
                    
               ],
          )
     )



dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])
size_Sf = calc_rel_size()


eventHandler.GUIobjs_array.append(obj)
print("STARTING MAIN LOOP")
xy = pygame.mouse.get_pos()
x,y = xy[0], xy[1]
while 1: #main loop
     dis.fill((255,255,255))
     
     for event in pygame.event.get():
          
          eventHandler.handle_event(event,x,y)
          if event.type == pygame.QUIT:
               pygame.quit()
               quit()
          elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

     eventHandler.display(dis)
     x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
     pygame.display.update()