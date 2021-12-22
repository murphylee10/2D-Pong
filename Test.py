import pygame

# Credit for this dropdown goes to https://stackoverflow.com/questions/59236523/trying-creating-dropdown-menu-pygame-but-got-stuck
class DropDown():
    def __init__(self, color_menu, color_option, x_pos, y_pos, width, height, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x_pos, y_pos, width, height)
        self.font = font
        self.main = main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center = rect.center))

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((640, 480))

DROPDOWN_GRAY = (175, 175, 175)
DROPDOWN_BLUE = (100, 200, 255)
DROPDOWN_RED = (255, 150, 150)

list1 = DropDown(
    [DROPDOWN_GRAY, DROPDOWN_BLUE],
    [DROPDOWN_BLUE, DROPDOWN_RED],
    50, 50, 200, 50, 
    pygame.font.SysFont(None, 30), 
    "Player", ["Player", "Computer"]
)

list2 = DropDown(
    [DROPDOWN_GRAY, DROPDOWN_BLUE],
    [DROPDOWN_BLUE, DROPDOWN_RED],
    300, 50, 200, 50,
    pygame.font.SysFont(None, 30),
    "Player", ["Player", "Computer"]
)

run = True
while run:
    clock.tick(30)

    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            run = False

    selected_option1 = list1.update(event_list)
    if selected_option1 >= 0:
        list1.main = list1.options[selected_option1]
        paddle1Choice = selected_option1

    selected_option2 = list2.update(event_list)
    if selected_option2 >= 0:
        list2.main = list2.options[selected_option2]
        paddle2Choice = selected_option2


    screen.fill((143, 67, 255))
    list1.draw(screen)
    list2.draw(screen)
    pygame.display.flip()
    
pygame.quit()
exit()