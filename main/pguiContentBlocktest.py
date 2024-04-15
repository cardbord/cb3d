from utils.pgui import TextInput, Button, DisplayColumns, DisplayRows, GUIobj, calc_rel_size, Handler, Anchor
import pygame

eventHandler = Handler()

pygame.init()

obj = GUIobj([200,200], [1400,1000],"content block test")
obj.add_content(
     DisplayRows(
          [
               Button([0,0],"ce").anchor(Anchor.CENTER),
               Button([0,0],"to").anchor(Anchor.TOP),
               Button([0,0],"bo").anchor(Anchor.BOTTOM),
               Button([0,0],"br").anchor(Anchor.BOTTOMRIGHT)
          ]
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
     displace_height = 50*obj._SIZE_SF
     avg_h = (obj.content[0].parent_window_size[1] - displace_height)/len(obj.content[0].content)
     for i in range(len(obj.content[0].content)):
          pygame.draw.line(dis,(0,0,0),(obj.pos[0],obj.pos[1] +displace_height + avg_h*i),(obj.pos[0]+obj.window_size[0], obj.pos[1]+displace_height+avg_h*i))
     x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
     pygame.display.update()