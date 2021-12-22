import pygame
import random
from sys import exit

from pygame.constants import MOUSEBUTTONDOWN

class Paddle(pygame.sprite.Sprite):
    speed = 10
    def __init__(self, num):
        super().__init__()
        self.num = num

        self.image = pygame.image.load('graphics/Paddle/SmallPaddle.png').convert_alpha()
        
        if num == 0:
            self.rect = self.image.get_rect(midleft = (12, HEIGHT/2 + 20))

        else:
            self.rect = self.image.get_rect(midright = (1188, HEIGHT/2 + 20))

        self.height = self.rect.bottom - self.rect.top

    def paddle_input(self, num):
        keys = pygame.key.get_pressed()
        # Left mouse controller - move according to w or s key
        if num == 0:
            if keys[pygame.K_w] and self.rect.top >= 40:
                self.rect.y -= Paddle.speed
            if keys[pygame.K_s] and self.rect.bottom <= 640:
                self.rect.y += Paddle.speed
                
        # Right mouse controller - move according to down or up key
        else:
            if keys[pygame.K_UP] and self.rect.top > 40:
                self.rect.y -= Paddle.speed
            if keys[pygame.K_DOWN] and self.rect.bottom < 640:
                self.rect.y += Paddle.speed

    def update(self):
        self.paddle_input(self.num)

class AIPaddle(pygame.sprite.Sprite):
    speed = 10
    def __init__(self, num):
        super().__init__()

        self.num = num

        self.image = pygame.image.load('graphics/Paddle/SmallPaddle.png').convert_alpha()
        
        if num == 0:
            self.rect = self.image.get_rect(midleft = (12, HEIGHT/2 + 20))

        elif num == 1:
            self.rect = self.image.get_rect(midright = (1188, HEIGHT/2 + 20))

        # For menu screen
        elif num == 2:
            self.rect = self.image.get_rect(midleft = (300, 355))

        else:
            self.rect = self.image.get_rect(midright = (900, 355))

        self.height = self.rect.bottom - self.rect.top

    def paddle_movement(self):
        if roundNum == 1:
            DIVISOR = 11
        elif roundNum == 2:
            DIVISOR = 9
        else:
            DIVISOR = 7

        # Set the speed according to ball and paddle positions
        AIPaddle.speed = (ball.sprite.rect.centery - self.rect.centery) / DIVISOR

        # At higher and lower postions, attach the edges of the paddle to the ball (for higher rounds)
        if self.rect.y > 600 and roundNum >= 3:
            AIPaddle.speed = (ball.sprite.rect.y - self.rect.bottom) / DIVISOR

        if self.rect.y < 80 and roundNum >= 3:
            AIPaddle.speed = (ball.sprite.rect.y - self.rect.top) / DIVISOR

        # Limit the speed of the paddle
        if AIPaddle.speed > 20:
            AIPaddle.speed = 20

        if AIPaddle.speed < -20:
            AIPaddle.speed = -20

        # Update the positions based on the speed
        if AIPaddle.speed < 0 and self.rect.top > 40:
            self.rect.y += AIPaddle.speed

        elif AIPaddle.speed > 0 and self.rect.bottom < 640:
            self.rect.y += AIPaddle.speed

    def update(self):
        self.paddle_movement()


class Ball(pygame.sprite.Sprite):
    existingBall = False
    def __init__(self):
        super().__init__()
        Ball.existingBall = True
        self.vx = 0
        self.vy = 0

        if roundNum == 1:
            self.speed = 10
        elif roundNum == 2:
            self.speed = 11
        else:
            self.speed = 12

        self.score_positive_sound = pygame.mixer.Sound('sounds/ScorePositive.wav')
        self.score_negative_sound = pygame.mixer.Sound('sounds/ScoreNegative.wav')
        self.hit_sound = pygame.mixer.Sound('sounds/HitBall.wav')

        self.image = pygame.image.load('graphics/Ball/LargeBall.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.8)
        self.rect = self.image.get_rect(center = (WIDTH/2, HEIGHT/2 + 20))

        self.launch_ball()

    # Called when someone has scored, launching the ball in a random direction
    def launch_ball(self):
        global game_active 
        game_active = True
        # Set random velocities for the ball if the current game is being played
        if game_state.state == "two_player_game" or game_state.state == "one_player_game":
            self.vx = self.speed * 1 * (random.choice([1, -1]))   # vX should always be 1 (bounds of 75 degrees)
            self.vy = round(self.speed * (random.randint(-100, 100) / 100), 2)  # vY is between -1 and 1

        else:
            self.vx = self.speed
            self.vy = 0

    # Moving moving the ball according to its direction and speed
    def ball_movement(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
    
    # When colliding with top and bottom walls, set the velocity to the opposite of its former
    def wall_collision(self, wall):
        self.vy = -self.vy

        # If ball is stuck on wall, move it
        while pygame.sprite.collide_rect(self, wall):
            self.ball_movement()

    # When colliding with paddles, set the velocity depending on where it hit the paddle
    def paddle_collision(self, paddle):
        if game_state.state == "two_player_game" or game_state.state  == "one_player_game":
            self.hit_sound.play()
            intersectionPoint = self.rect.centery - paddle.rect.centery
            normalisedIntersectionPoint = intersectionPoint / (paddle.height / 2)

            # Dont let the normalised intersection point be greater than 1
            if normalisedIntersectionPoint > 1.1 or normalisedIntersectionPoint < -1.1:
                normalisedIntersectionPoint = -int(normalisedIntersectionPoint)

            # Set new ball velocities according to collision point
            self.vx = -self.vx
            self.vy = normalisedIntersectionPoint * self.speed

            # Prevent an AI stalemate
            if (paddle1Choice == 1 and paddle2Choice == 1) and (self.vy < 1.0 and self.vy > -1.0):
                self.vy = self.speed * 0.5

            # AI stalemate 2
            if (paddle1Choice == 1 and paddle2Choice == 1) and (self.vy == 2.909090909090909 or self.vy == -2.909090909090909):
                self.vy = round(self.vy, 0)

        else:
            self.vx = -self.vx
            self.vy = 0

        print(self.vy)

        # If ball is stuck on top of paddle, send it off by moving the ball in desired direction
        while (self.rect.top <= paddle.rect.top or self.rect.bottom >= paddle.rect.bottom) and pygame.sprite.collide_rect(self, paddle):
            self.ball_movement()

    # If ball has been scored, destroy this instance of ball
    def destroy(self, x_pos):
        global game_state

        # Kill instance of class if its outside bounds
        self.kill()
        Ball.existingBall = False

        # If the x-position is more than 1200, the player on the left scored
        if x_pos >= 1200:
            scores[0] += 1
            if game_state.state == "one_player_game" and paddle2Choice == 0:
                self.score_negative_sound.play()
            else:
                self.score_positive_sound.play()

        # Otherwise, the player on the right scored
        elif x_pos <= 0:
            scores[1] += 1
            if game_state.state == "one_player_game" and paddle1Choice == 0:
                self.score_negative_sound.play()
            else:
                self.score_positive_sound.play()

    def update(self):
        # Reflect the ball if it bounces off top or bottom ceiling
        global horizWall, vertWall, ball, paddle
        if pygame.sprite.spritecollide(ball.sprite, horizWall, False):
            collidingWall = pygame.sprite.spritecollide(ball.sprite, horizWall, False)[0]
            self.wall_collision(collidingWall)
       
        if pygame.sprite.spritecollide(ball.sprite, paddle, False):
            # Returns a list of the items in the group that collided, take the first instance (paddle)
            collidingPaddle = pygame.sprite.spritecollide(ball.sprite, paddle, False)[0]
            self.paddle_collision(collidingPaddle)

        # Ball movement (constant)
        self.ball_movement()

        # Kill current ball if scored
        if self.rect.x <= -10 or self.rect.x >= 1210:
            self.destroy(self.rect.x)

class HorizWall(pygame.sprite.Sprite):
    count = 0
    def __init__(self):
        super().__init__()
        # Setting 2 walls for collisions
        self.image = pygame.image.load('graphics/Wall/HorizWall.png').convert_alpha()
        if HorizWall.count == 0:
            self.rect = self.image.get_rect(midbottom = (WIDTH/2, 45))
        else:
            self.image = pygame.image.load('graphics/Wall/HorizWall.png').convert_alpha()
            self.rect = self.image.get_rect(midtop = (WIDTH/2, 635))
        
        HorizWall.count += 1

class VertWall(pygame.sprite.Sprite):
    count = 0
    def __init__(self):
        super().__init__()
        if VertWall.count == 0:
            self.image = pygame.image.load('graphics/Wall/VertWall.png').convert_alpha()
            self.rect = self.image.get_rect(midright = (5, HEIGHT/2))
        else:
            self.image = pygame.image.load('graphics/Wall/VertWall.png').convert_alpha()
            self.rect = self.image.get_rect(midleft = (1195, HEIGHT/2))

        VertWall.count += 1

    def update(self):
        pass

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
        msg = self.font.render(self.main, 1, BLACK)
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, BLACK)
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

class GameState():
    def __init__(self):
        self.state = "menu"

    def menu(self):
        global menu_music_played, paddle1Choice, paddle2Choice, displayError, label_1, label_2

        # Play Music
        if (menu_music_played == False):
            menu_music.play(loops = -1)
            menu_music_played = True

        mx, my = pygame.mouse.get_pos()
        background1_surf.fill((143, 67, 255))

        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == MOUSEBUTTONDOWN and event.button == 1 and playButton_rect.collidepoint(mx, my):
                if paddle1Choice == -1 or paddle2Choice == -1:
                    displayError = True

                else:
                    # Stop the music
                    menu_music.stop()

                    # Assign different game states dependding on the dropbox selection
                    if paddle1Choice + paddle2Choice == 1:
                        self.state = "one_player_game"
                    else:
                        self.state = "two_player_game"

                    # Reset the sprites 
                    ball.sprite.destroy(1)
                    paddle.empty()
                    displayError = False

                    # Add new paddles
                    paddle.add(Paddle(0) if paddle1Choice == 0 else AIPaddle(0))
                    paddle.add(Paddle(1) if paddle2Choice == 0 else AIPaddle(1))

                    label_1 = "Player" if paddle1Choice == 0 else "Computer"
                    label_2 = "Player" if paddle2Choice == 0 else "Computer"

                    ball.add(Ball())
                    return
                    

        # Dropdown handling
        selected_option1 = list1.update(event_list)
        if selected_option1 >= 0:
            list1.main = list1.options[selected_option1]
            paddle1Choice = selected_option1

        selected_option2 = list2.update(event_list)
        if selected_option2 >= 0:
            list2.main = list2.options[selected_option2]
            paddle2Choice = selected_option2


        screen.blit(background1_surf, (0, 0))
        screen.blit(title_surf, title_rect)
        screen.blit(instructions_surf, instructions_rect)
        screen.blit(playButton_surf, playButton_rect)
        
        if displayError == True:
            screen.blit(error_surf, error_rect)

        paddle.draw(screen)
        ball.draw(screen)

        list1.draw(screen)
        list2.draw(screen)

        ball.update()
        paddle.update()


        pygame.display.update()

    def main_game(self):
        global game_active, scores, roundNum, music_played, menu_music_played

        # Setup background and menubar images
        if roundNum == 1:
            # background1_surf.fill((146, 168, 209))
            background1_surf.fill((148, 186, 253))

        elif roundNum == 2:
            background1_surf.fill((140, 175, 150))

        elif roundNum == 3:
            background1_surf.fill((238, 201, 134))
        
        menubar_surf.fill((175, 175, 175))

        # Get the current mouse position
        mx, my = pygame.mouse.get_pos()

        # Quitting or starting a game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == MOUSEBUTTONDOWN and event.button == 1 and menuButton_rect.collidepoint(mx, my):
                self.state = "menu"
                menu_music_played = False
                ball.sprite.destroy(1)
                paddle.empty()

                # Add new paddles
                paddle.add(AIPaddle(2))
                paddle.add(AIPaddle(3))
                ball.add(Ball())

                # Create new lists to bring back the default option
                list1 = DropDown(
                [DROPDOWN_GRAY, DROPDOWN_BLUE],
                [DROPDOWN_BLUE, DROPDOWN_RED],
                205, 230, 200, 50, 
                pygame.font.SysFont(None, 30), 
                "Paddle 1", ["Player", "Computer"]
                )

                list2 = DropDown(
                    [DROPDOWN_GRAY, DROPDOWN_BLUE],
                    [DROPDOWN_BLUE, DROPDOWN_RED],
                    788, 230, 200, 50,
                    pygame.font.SysFont(None, 30),
                    "Paddle 2", ["Player", "Computer"]
                )
                scores = [0, 0]
                roundNum = 1
            
            if not game_active:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_active = True
                    scores = [0, 0]
                    roundNum = 1
                    music_played = False
                    ball.add(Ball())
        
        screen.blit(background1_surf, (0, 40))
        screen.blit(dashes_surf, dashes_rect)

        display_scores(scores)


        horizWall.draw(screen)
        vertWall.draw(screen)
        paddle.draw(screen)
        
        screen.blit(menubar_surf, (0, 0))
        screen.blit(menubar_surf, (0, 640))
        screen.blit(menuButton_surf, menuButton_rect)
        display_player_labels()

        # Display round if it's single player mode
        if game_state.state == "one_player_game":
            display_round(roundNum)

        # Select a winner if the one of the players scored 10 points
        if self.state == "two_player_game" and scores[0] >= 10:
            game_active = False
            winner_surf = font_small.render('Left Player Wins!', False, TEAL)
            winner_rect = winner_surf.get_rect(center = (270, 140))
            screen.blit(winner_surf, winner_rect)
            if music_played == False:
                WIN_SOUND.play()
                music_played = True

        elif self.state == "two_player_game" and scores[1] >= 10:
            game_active = False
            winner_surf = font_small.render('Right Player Wins!', False, TEAL)
            winner_rect = winner_surf.get_rect(center = (930, 140))
            screen.blit(winner_surf, winner_rect)
            if music_played == False:
                WIN_SOUND.play()
                music_played = True

        elif self.state == "one_player_game" and (scores[0] >= 5 or scores[1] >= 5):

            # Set the locations of the rect depending on which player is at 5 points
            location = (270, 140) if scores[0] >= 5 else (930, 140)

            # If the round is 5 and the player has won
            if (roundNum == 3) and ((scores[0] >= 5 and paddle1Choice == 0) or (scores[1] >= 5 and paddle2Choice == 0)):
                game_active = False
                winner_surf = font_small.render("You Have Won The Game!", False, TEAL)
                winner_rect = winner_surf.get_rect(center = location)
                screen.blit(winner_surf, winner_rect)
                if music_played == False:
                    WIN_SOUND.play()
                    music_played = True

            # If the user lost
            elif (scores[0] >= 5 and paddle2Choice == 0) or (scores[1] >= 5 and paddle1Choice == 0):
                game_active = False
                winner_surf = font_small.render("Computer Wins!", False, (255, 23, 23))
                winner_rect = winner_surf.get_rect(center = location)
                screen.blit(winner_surf, winner_rect)
                if music_played == False:
                    LOSE_SOUND.play()
                    music_played = True

            # Otherwise, the user has progressed a round
            else:
                roundNum += 1
                scores = [0, 0]

        # If the game is still going, update the positions of the walls, paddles, and ball
        if game_active:
            horizWall.update()
            vertWall.update()
            paddle.update()
            
            ball.draw(screen)
            ball.update()
            
            if Ball.existingBall == False:
                ball.add(Ball())

        # Prompt the user to start a new game
        else:
            instruction_surf = font_small.render('Press SPACE to start game', False, LAVENDER)
            instruction_rect = instruction_surf.get_rect(center = (600, 340))
            screen.blit(instruction_surf, instruction_rect)

        pygame.display.update() # Updates display surface after each iteration

    def state_manager(self):
        if self.state == "menu":
            self.menu()
        elif self.state == "two_player_game" or self.state == "one_player_game":
            self.main_game()

def display_scores(scores):
    score_surf_left = font.render(f'{scores[0]}', False, WHITE)
    score_rect_left = score_surf_left.get_rect(topright = (575, 52))

    score_surf_right = font.render(f'{scores[1]}', False, WHITE)
    score_rect_right = score_surf_right.get_rect(topleft = (625, 52))

    screen.blit(score_surf_left, score_rect_left)
    screen.blit(score_surf_right, score_rect_right)

def display_round(roundNum):
    round_surf = font_small.render(f'Round {roundNum}', False, BLACK)
    round_rect = round_surf.get_rect(center = (600, 20))

    screen.blit(round_surf, round_rect)

def display_player_labels():
    label_1_surf = font_smallest.render(label_1, False, BLACK)
    label_1_rect = label_1_surf.get_rect(center = (300, 655))

    label_2_surf = font_smallest.render(label_2, False, BLACK)
    label_2_rect = label_2_surf.get_rect(center = (900, 655))

    screen.blit(label_1_surf, label_1_rect)
    screen.blit(label_2_surf, label_2_rect)

pygame.init()

# GENERAL SETUP
WIDTH = 1200
HEIGHT = 680
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAL = (125, 212, 171)
LAVENDER = (180, 118, 228)
GREEN = (101, 253, 0)
DROPDOWN_GRAY = (175, 175, 175)
DROPDOWN_BLUE = (100, 200, 255)
DROPDOWN_RED = (255, 150, 150)
LOSE_SOUND = pygame.mixer.Sound('sounds/Lose.wav')
WIN_SOUND = pygame.mixer.Sound('sounds/Win.wav')

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pong')
clock = pygame.time.Clock() # Clock object for controlling framerate
font = pygame.font.Font('fonts/Source_Sans_Pro/SourceSansPro-SemiBold.ttf', 100)
font_small = pygame.font.Font('fonts/Source_Sans_Pro/SourceSansPro-SemiBold.ttf', 40)
font_smallest = pygame.font.Font('fonts/Source_Sans_Pro/SourceSansPro-SemiBold.ttf', 30)

# MENU VARIABLES
title_surf = font.render('PONG FOR LEGENDS', False, WHITE)
title_rect = title_surf.get_rect(center = (600, 75))
instructions_surf = font_small.render('Choose Your Paddle Modes:', False, WHITE)
instructions_rect = instructions_surf.get_rect(center = (600, 150))
displayError = False
error_surf = font_small.render('You Must Select A Mode For Each Paddle!', False, GREEN)
error_rect = error_surf.get_rect(center = (600, 590))
paddle1Choice = -1
paddle2Choice = -1
list1 = DropDown(
    [DROPDOWN_GRAY, DROPDOWN_BLUE],
    [DROPDOWN_BLUE, DROPDOWN_RED],
    205, 230, 200, 50, 
    pygame.font.SysFont(None, 30), 
    "Paddle 1", ["Player", "Computer"]
)

list2 = DropDown(
    [DROPDOWN_GRAY, DROPDOWN_BLUE],
    [DROPDOWN_BLUE, DROPDOWN_RED],
    788, 230, 200, 50,
    pygame.font.SysFont(None, 30),
    "Paddle 2", ["Player", "Computer"]
)

menu_music = pygame.mixer.Sound('sounds/MenuMusic.wav')
menu_music_played = False

# GAME VARIABLES

# Surfaces
roundNum = 1
scores = [0, 0]
background1_surf = pygame.Surface((WIDTH, HEIGHT))
menubar_surf = pygame.Surface((WIDTH, 40))
game_active = False
music_played = False

menuButton_surf = pygame.image.load('graphics/Background/MenuButton.png').convert_alpha()
menuButton_rect = menuButton_surf.get_rect(center = (1150, 20))

playButton_surf = pygame.image.load('graphics/Background/PlayButton.png').convert_alpha()
playButton_rect = playButton_surf.get_rect(center = (600, 500))

dashes_surf = pygame.image.load('graphics/Background/Dashes.png').convert_alpha()
dashes_rect = dashes_surf.get_rect(center = (WIDTH/2, HEIGHT/2))

label_1 = ""
label_2 = ""

game_state = GameState()

ball = pygame.sprite.GroupSingle()
ball.add(Ball())

paddle = pygame.sprite.Group()
paddle.add(AIPaddle(2))
paddle.add(AIPaddle(3))

horizWall = pygame.sprite.Group()
horizWall.add(HorizWall())
horizWall.add(HorizWall())

vertWall = pygame.sprite.Group()
vertWall.add(VertWall())
vertWall.add(VertWall())


while True:
    game_state.state_manager()
    clock.tick(60)

    
