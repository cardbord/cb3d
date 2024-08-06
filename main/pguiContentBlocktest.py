from utils.pgui import TextInput, Button, DisplayColumns, DisplayRows, GUIobj, calc_rel_size, Handler, Anchor
import pygame

eventHandler = Handler()

debug = False #SET FALSE WHEN NOT TESTING

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


eventHandler.add(obj)

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
     print(eventHandler.collate_textinput_inputs())
     if debug: #would it be worth actually making this a feature at some point? if i keep having these ideas i'm never gonna be finished...
          displace_height = 50*obj._SIZE_SF
          avg_h = (obj.content[0].parent_window_size[1] - displace_height)/len(obj.content[0].content)
          for i in range(len(obj.content[0].content)):
               pygame.draw.line(dis,(0,0,0),(obj.pos[0],obj.pos[1] +displace_height + avg_h*i),(obj.pos[0]+obj.window_size[0], obj.pos[1]+displace_height+avg_h*i))
          
     x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
     pygame.display.update()