from utils.pgui import TextInput, Button, DisplayColumns, DisplayRows, GUIobj, calc_rel_size
import pygame



pygame.init()

obj = GUIobj([200,200], [600,500],"content block test")
obj.content = [
     DisplayColumns(
               obj.pos, obj.window_size,
               [
               Button([0,0],"test button"),
               TextInput([0,0],"hello there")
               ],        
     )
]




dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])
size_Sf = calc_rel_size()
print(obj.content[0].content[0].pos)
print(obj.content[0].content[0].text_box_width)
print(obj.content[0].content[0].button_rect.width)
print(obj.content[0].content[0]._SIZE_SF)

obj.content[0]._calc_obj_rel_pos(50*size_Sf)
print("STARTING MAIN LOOP")
while 1: #main loop
     dis.fill((255,255,255))
     
     print(obj.content[0].content[0].pos)
     print(obj.content[0].content[0].text_box_width)
     print(obj.content[0].content[0].button_rect.width)
     print(obj.content[0].content[0]._SIZE_SF)
     for event in pygame.event.get():
          if event.type == pygame.QUIT:
               pygame.quit()
               quit()
          elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

     obj.display_window(dis)

     pygame.display.update()