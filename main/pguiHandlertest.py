from utils import pgui
import pygame

'''
mimics pguitest.py in functionality, but makes use of the GUIobj Handler class to abstract all obj movement/textinput additions/window priority away from the main program.
'''

def create_random_textbox_for_the_funsies():
        tb1 = pgui.TextInput([0,0],"hi")
        tib1 = pgui.TextInputBox([50,100],[600,500],[tb1],"this is a demo")
        
        tib1.confirm_button.callback = lambda : print([i.user_text for i in tib1.text_inputs])
        return tib1

h3 = pgui.Handler()

h3.GUIobjs_array.append(pgui.TextInputBox([50,100],[600,500],[pgui.TextInput([0,0],"hi"),pgui.TextInput([0,0],"hi2")],"this is a demo"))
h3.GUIobjs_array.append(pgui.TextInputBox([50,100],[600,500],[pgui.TextInput([0,0],"hi"),pgui.TextInput([0,0],"hi2")],"this is a demo"))

pygame.init()
dis = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])
x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
while 1:
    dis.fill((255,255,255))
    for event in pygame.event.get():
        h3.handle_event(event,x,y)

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
            elif event.key == pygame.K_DELETE:
                h3.GUIobjs_array.append(create_random_textbox_for_the_funsies())
            
            #within this loop, it is beneficial to provide the event, and then feed it through pgui's handler. it's far better than running two event loops at once
            
    h3.display(dis)
    pygame.display.flip()
    x,y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]