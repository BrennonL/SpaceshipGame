'''
Brennon Laney 
SpaceShip Game
'''

import pygame as pg
import os
import time
import random
pg.font.init()


WIDTH, HEIGHT = 750, 750
WIN = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Space Shooter") 

# Set the background img to the variable BACKGROUND 
BACKGROUND =  pg.transform.scale(pg.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Set ship imgages to variables
# Also these will be imorted into the class Ship
BLUE_SHIP = pg.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
GREEN_SHIP = pg.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
RED_SHIP = pg.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
YELLOW_SHIP = pg.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Set lazer images to variables
BLUE_LASER = pg.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pg.image.load(os.path.join("assets", "pixel_laser_green.png"))
RED_LASER = pg.image.load(os.path.join("assets", "pixel_laser_red.png"))
YELLOW_LASER = pg.image.load(os.path.join("assets", "pixel_laser_yellow.png"))







class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pg.mask.from_surface(self.img)


    def draw(self, window):
        '''
        Input: self, window
        This function just draws the laser
        Output: None
        '''
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        '''
        Input: self, vel(represents the velocity of the bullets)
        Functionality: Moves the bullets at a certain velocity by adding vel to the current y position
        Output: None
        '''
        self.y += vel

    def off_screen(self, height):
        '''
        Input: self, height(of the screen)
        Functionality: If the bullet is off the screen it will return a true or false statement 
        Return: Boolean
        '''
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        '''
        Input: self, obj(either an enemy ship or player_ship)
        Functionality: Detects if the laser hits any ships
        Return: Boolean
        '''
        return collide(self, obj)


class Ship:
    COOLDOWN = 30


    def __init__(self, x, y , health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        '''
        Input: self, window
        Functionality: For each laser called in one of the ship classes it will draw them on the window
        Output: Void
        '''
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        '''
        Input: self, vel, obj
        Functionality: It will call the move() function in the laser class and then it will delete the laser
        if it goes off the screen or it hits and enemy. If it hits the player it will make the player loose 10 
        health
        Output: Void
        '''
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        '''
        Input: self
        Functionality: This will add 1 to cool_down_counter until it is equal to COOLDOWN where it will reset to 0
        Return: Void
        '''
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0 
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        '''
        Input: self
        Functionality: This will only allow the ships to shoot if the cool-down is equal to 0
        Return: Void
        '''
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


            Laser_sound = pg.mixer.Sound("assets/laser.wav")
            Laser_sound.play()

    def get_width(self):
        '''
        Input: self
        Functionality: Gets the width of the ship_img
        Output: The size of the ship image
        '''
        return self.ship_img.get_width()

    def get_height(self):
        '''
        Input: self
        Functionality: Gets the height of the ship_img
        Output: The size of the ship image
        '''
        return self.ship_img.get_height()




class Player(Ship):
    def __init__(self, x, y, health=100):

        # This super()... calls all initiators from parent class
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pg.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        '''
        Input: self, vel, objs
        Functionality: This checks the player's bullets and if it collides with another ship 
        or goes off the screen it will delete the laser
        Return: Void
        '''
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)


    def draw(self, window):
        '''
        Input: self, window
        Functionality: This will draw the player ship at the x and y coordinates
        Return: void
        '''
        super().draw(window)
        self.Health_bar(window)

    def Health_bar(self, window):
        '''
        Input: sefl, window
        Functionality: This will draw a red and a green bar. Both will be the same size but the green one
        will shrink based on the amount of life the player has
        Return: void
        '''
        pg.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pg.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))



class Enemy(Ship):
    COLOR_MAP = {
                    "red" : (RED_SHIP, RED_LASER),
                    "green": (GREEN_SHIP, GREEN_LASER),
                    "blue" : (BLUE_SHIP, BLUE_LASER)
                }
    def __init__(self, x, y, color, health=100):# "red", "green", "blue"
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pg.mask.from_surface(self.ship_img)

    def move(self, vel):
        '''
        Input: self, vel
        Functionality: This will add the vel to the enemy ships y coordinate 
        Return: Void
        '''
        self.y += vel

    def shoot(self):
        '''
        Input: self
        Functionality: This will only allow the enemy ship to shoot if the cool_down_counter is equal to 0.
        In the cooldown() function it will calculate the cool_down_counter
        '''
        if self.cool_down_counter == 0:
            # I subtracted 10 because originally the lasters were shooting from the side of the ship
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1



def collide(obj1, obj2):
    '''
    Input: obj1, obj2
    Functionality: This will check to see if obj1's position doesn't collide with obj2's.
    If they do collide it will return a false
    Return: False
    '''
    offset_x = obj2.x - obj1.x
    offset_y = obj1.y - obj2.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():

    # Declare my Constants
    run = True
    FPS = 80
    level = 0
    lives = 5
    main_font = pg.font.SysFont("comicsans", 25)
    lost_font = pg.font.SysFont("comicsans", 30)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 6

    # Declare the ship class
    player_ship = Player(300, 630)

    clock = pg.time.Clock()

    # Used to make sure the player hasn't lost yet
    lost = False
    lost_count = 0

    def redraw_window():
        '''
        Input: void
        Functionality: This will redraw the page according to the FPS. It will draw, enemies, move ships, draw player ships and lasers
        Return: Void
        '''
        WIN.blit(BACKGROUND, (0,0))
        # draw level and lives on screne
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        WIN.blit(lives_label , (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # Draw each enemy ship in the enemies list
        for enemy in enemies:
            enemy.draw(WIN)

        # Draw the ship
        player_ship.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2- lost_label.get_width()/2, 350))

        pg.display.update()

    while run:
        clock.tick(FPS)

        redraw_window()


        
        if lives <= 0 or player_ship.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        
        # This will move the player to the next level if they kill all the enemies of the first wave. The next wave will have 5 more enemies
        if len(enemies) == 0:
            level += 1
            wave_length += 5

            if level == 1:
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red"]))
                    enemies.append(enemy)

            elif level == 2 or level == 3:
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "green"]))
                    enemies.append(enemy)

            else:
                wave_length -= 2
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                    enemies.append(enemy)   

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

        keys = pg.key.get_pressed()
        # This grabs all the keys pressed at the current time and adds it to a dictonary

        # Moves left
        if keys[pg.K_a] and player_ship.x - player_vel > 0: #
            player_ship.x -= player_vel

        # Moves right
        if keys[pg.K_d] and player_ship.x + player_vel + player_ship.get_width() < WIDTH:
            player_ship.x += player_vel

        # Moves up
        if keys[pg.K_w] and player_ship.y - player_vel > 0:
            player_ship.y -= player_vel 

        # Moves down
        if keys[pg.K_s] and player_ship.y + player_vel + player_ship.get_width() + 15 < HEIGHT:
            player_ship.y += player_vel

        # Shoots laser
        if keys[pg.K_SPACE]:
            player_ship.shoot()

        # This will make a copy of the enemies list and remove it if the enemy goes off screen or gets hit by a bullet
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player_ship)

            if random.randrange(0, 2*FPS) == 1: # 4*60 is because we want it to have 1/4 chance of shooting and there are 60 frames per second
                enemy.shoot()


            if collide(enemy, player_ship):
                player_ship.health -= 10
                enemies.remove(enemy)
            
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy) 

        player_ship.move_lasers(-laser_vel, enemies) 


def main_menu():
    '''
    Input: Void
    Functionality: This will load a main menu before the game loads. It will start the game once the player clicks
    Return: Void
    '''
    title_font = pg.font.SysFont("comicsans", 50)
    run = True

    # initialize the mixer 
    pg.mixer.init()
    pg.mixer.music.load("assets/music.wav")
    pg.mixer.music.set_volume(0.2)

    # this is to make it so that the music is on repeat
    pg.mixer.music.play(-1)
    while run:
        WIN.blit(BACKGROUND, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.MOUSEBUTTONDOWN:
                main()
    pg.quit()


main_menu()