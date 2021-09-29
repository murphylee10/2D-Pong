import pygame
import random
from sys import exit

# Colours: Ash Gray (178, 190, 181), Sage Green (138, 154, 91), Victory Green (0, 104, 71)
# ToDo: Refactoring (put images into seperate folders), main menu, and AI bot, SOUND, TRAIL?, Inc ball speed for AI

class Paddle(pygame.sprite.Sprite):
    speed = 10
    def __init__(self, num):
        super().__init__()
        self.num = num

        self.image = pygame.image.load('graphics/Paddle/SmallPaddle.png').convert_alpha()
        
        if num == 0:
            self.rect = self.image.get_rect(midleft = (12, HEIGHT/2))

        else:
            self.rect = self.image.get_rect(midright = (1188, HEIGHT/2))

        self.height = self.rect.bottom - self.rect.top

    def paddle_input(self, num):
        keys = pygame.key.get_pressed()
        # Left mouse controller - move according to w or s key
        if num == 0:
            if keys[pygame.K_w] and self.rect.top >= 0:
                self.rect.y -= Paddle.speed
            if keys[pygame.K_s] and self.rect.bottom <= 600:
                self.rect.y += Paddle.speed
                
        # Right mouse controller - move according to down or up key
        else:
            if keys[pygame.K_UP] and self.rect.top >= 0:
                self.rect.y -= Paddle.speed
            if keys[pygame.K_DOWN] and self.rect.bottom <= 600:
                self.rect.y += Paddle.speed

    def update(self):
        self.paddle_input(self.num)

class Ball(pygame.sprite.Sprite):
    existingBall = False
    def __init__(self):
        super().__init__()
        Ball.existingBall = True
        self.vx = 0
        self.vy = 0
        self.speed = 8

        self.image = pygame.image.load('graphics/Ball/LargeBall.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.8)
        self.rect = self.image.get_rect(center = (WIDTH/2, HEIGHT/2))

        self.launch_ball()

    # Called when someone has scored, launching the ball in a random direction
    def launch_ball(self):
        global game_active 
        game_active = True
        # Set random velocities for the ball
        self.vx = self.speed * 1 * (random.choice([1, -1]))   # vX should always be 1 (bounds of 75 degrees)
        self.vy = round(self.speed * (random.randint(-100, 100) / 100), 2)  # vY is between -1 and 1

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
        intersectionPoint = self.rect.centery - paddle.rect.centery
        normalisedIntersectionPoint = intersectionPoint / (paddle.height / 2)

        # Dont let the normalised intersection point be greater than 1
        if normalisedIntersectionPoint > 1.1 or normalisedIntersectionPoint < -1.1:
            normalisedIntersectionPoint = -int(normalisedIntersectionPoint)

        # Set new ball velocities according to collision point
        self.vx = -self.vx
        self.vy = normalisedIntersectionPoint * self.speed

        # If ball is stuck on top of paddle, send it off by moving the ball in desired direction
        while (self.rect.top <= paddle.rect.top or self.rect.bottom >= paddle.rect.bottom) and pygame.sprite.collide_rect(self, paddle):
            self.ball_movement()

    # If ball has been scored, destroy this instance of ball
    def destroy(self, x_pos):
        # Kill instance of class if its outside bounds
        self.kill()
        Ball.existingBall = False

        # If the x-position is positive, the player on the left scored
        if x_pos > 0:
            scores[0] += 1
        # Otherwise, the player on the right scored
        else:
            scores[1] += 1

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
            self.rect = self.image.get_rect(midbottom = (WIDTH/2, 5))
        else:
            self.image = pygame.image.load('graphics/Wall/HorizWall.png').convert_alpha()
            self.rect = self.image.get_rect(midtop = (WIDTH/2, 595))
        
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

def display_scores(scores):
    score_surf_left = font.render(f'{scores[0]}', False, WHITE)
    score_rect_left = score_surf_left.get_rect(topright = (575, 12))

    score_surf_right = font.render(f'{scores[1]}', False, WHITE)
    score_rect_right = score_surf_right.get_rect(topleft = (625, 12))

    screen.blit(score_surf_left, score_rect_left)
    screen.blit(score_surf_right, score_rect_right)

pygame.init()

# WIDTH = 1000
WIDTH = 1200
HEIGHT = 600
WHITE = (255, 255, 255)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pong')
game_active = False
clock = pygame.time.Clock() # Clock object for controlling framerate
font = pygame.font.Font('fonts/Source_Sans_Pro/SourceSansPro-SemiBold.ttf', 100)
font_small = pygame.font.Font('fonts/Source_Sans_Pro/SourceSansPro-SemiBold.ttf', 40)
scores = [0, 0]

# SURFACES
background_surf = pygame.Surface((WIDTH, HEIGHT))
background_surf.fill((146, 168, 209))

dashes_surf = pygame.image.load('graphics/Background/Dashes.png').convert_alpha()
dashes_rect = dashes_surf.get_rect(center = (WIDTH/2, HEIGHT/2))

ball = pygame.sprite.GroupSingle()
# ball.add(Ball())

paddle = pygame.sprite.Group()
paddle.add(Paddle(0))
paddle.add(Paddle(1))

horizWall = pygame.sprite.Group()
horizWall.add(HorizWall())
horizWall.add(HorizWall())

vertWall = pygame.sprite.Group()
vertWall.add(VertWall())
vertWall.add(VertWall())

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if not game_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                scores = [0, 0]
                ball.add(Ball())
                
    screen.blit(background_surf, (0, 0))
    screen.blit(dashes_surf, dashes_rect)

    display_scores(scores)

    horizWall.draw(screen)
    vertWall.draw(screen)
    paddle.draw(screen)
    
 # Select a winner if the one of the players scored 10 points
    if scores[0] >= 10:
        game_active = False
        winner_surf = font_small.render('Left Player Wins!', False, (0, 104, 71))
        winner_rect = winner_surf.get_rect(center = (270, 100))
        screen.blit(winner_surf, winner_rect)

    elif scores[1] >= 10:
        game_active = False
        winner_surf = font_small.render('Right Player Wins!', False, (0, 104, 71))
        winner_rect = winner_surf.get_rect(center = (930, 100))
        screen.blit(winner_surf, winner_rect)

    if game_active:
        horizWall.update()
        vertWall.update()
        paddle.update()
        
        ball.draw(screen)
        ball.update()
        
        if Ball.existingBall == False:
            ball.add(Ball())

    else:
        instruction_surf = font_small.render('Press SPACE to start game', False, WHITE)
        instruction_rect = instruction_surf.get_rect(center = (600, 300))
        screen.blit(instruction_surf, instruction_rect)

    pygame.display.update() # Updates display surface after each iteration
    clock.tick(60)

    