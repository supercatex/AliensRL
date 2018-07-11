#!/usr/bin/env python

import random, os.path, math

#import basic pygame modules
import pygame
from pygame.locals import *
import Agent

#see if we can load more than standard BMP
if not pygame.image.get_extended():
    raise SystemExit("Sorry, extended image module required")


#game constants
MAX_SHOTS      = 2      #most player bullets onscreen
ALIEN_ODDS     = 22     #chances a new alien appears
BOMB_ODDS      = 60    #chances a new bomb will drop
ALIEN_RELOAD   = 12   #frames between new aliens
SCREENRECT     = Rect(0, 0, 640, 480)
SCORE          = 0
PLAY_TIMES = 0

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


class dummysound:
    def play(self): pass

def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(main_dir, 'data', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return dummysound()



# each type of game object gets an init and an
# update function. the update function is called
# once per frame, and it is when each object should
# change it's current position and state. the Player
# object actually gets a "move" function instead of
# update, since it is passed extra information about
# the keyboard


class Player(pygame.sprite.Sprite):
    speed = 10
    bounce = 24
    gun_offset = -11
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1

    def move(self, direction):
        if direction: self.facing = direction
        self.rect.move_ip(direction*self.speed, 0)
        self.rect = self.rect.clamp(SCREENRECT)
        if direction < 0:
            self.image = self.images[0]
        elif direction > 0:
            self.image = self.images[1]
        self.rect.top = self.origtop - (self.rect.left//self.bounce%2)

    def gunpos(self):
        pos = self.facing*self.gun_offset + self.rect.centerx
        return pos, self.rect.top


class Alien(pygame.sprite.Sprite):
    speed = 13
    animcycle = 12
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1,1)) * Alien.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing;
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1
        self.image = self.images[self.frame//self.animcycle%3]


class Explosion(pygame.sprite.Sprite):
    defaultlife = 12
    animcycle = 3
    images = []
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life//self.animcycle%2]
        if self.life <= 0: self.kill()


class Shot(pygame.sprite.Sprite):
    speed = -11
    images = []
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.kill()


class Bomb(pygame.sprite.Sprite):
    speed = 9
    images = []
    def __init__(self, alien):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=
                    alien.rect.move(0,5).midbottom)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom >= 470:
            Explosion(self)
            self.kill()


class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = Color('white')
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(10, 450)

    def update(self):
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, 0, self.color)

#Q-Learning Agent
agent = Agent.QLearningAgent()
agent.load_data()
def main(winstyle = 0):
    # Initialize pygame
    pygame.init()
    if pygame.mixer and not pygame.mixer.get_init():
        print ('Warning, no sound')
        pygame.mixer = None

    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    #Load images, assign to sprite classes
    #(do this before the classes are used, after screen setup)
    img = load_image('player1.gif')
    Player.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image('explosion1.gif')
    Explosion.images = [img, pygame.transform.flip(img, 1, 1)]
    Alien.images = load_images('alien1.gif', 'alien2.gif', 'alien3.gif')
    Bomb.images = [load_image('bomb.gif')]
    Shot.images = [load_image('shot.gif')]

    #decorate the game window
    icon = pygame.transform.scale(Alien.images[0], (32, 32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Pygame Aliens')
    pygame.mouse.set_visible(0)

    #create the background, tile the bgd image
    bgdtile = load_image('background.gif')
    background = pygame.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0,0))
    pygame.display.flip()

    #load the sound effects
    boom_sound = load_sound('boom.wav')
    shoot_sound = load_sound('car_door.wav')
    if pygame.mixer:
        music = os.path.join(main_dir, 'data', 'house_lo.wav')
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

    # Initialize Game Groups
    aliens = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()
    lastalien = pygame.sprite.GroupSingle()

    #assign default groups to each sprite class
    Player.containers = all
    Alien.containers = aliens, all, lastalien
    Shot.containers = shots, all
    Bomb.containers = bombs, all
    Explosion.containers = all
    Score.containers = all

    #Create Some Starting Values
    global score
    alienreload = ALIEN_RELOAD
    kills = 0
    clock = pygame.time.Clock()

    #initialize our starting sprites
    global SCORE
    player = Player()
    Alien() #note, this 'lives' because it goes into a sprite group
    if pygame.font:
        all.add(Score())

#Agent: var
    direction = 0
    firing = 0
    global agent
    global KILL_BY_ALIEN
    global KILL_BY_BOMB

    prev_state = {}
    curr_state = {}
    prev_action = ''
    curr_action = ''
    reward = 0
    target_alien = ''
    is_killed = False
    is_missed = False
###
    while player.alive():

        #get input
        for event in pygame.event.get():
            if event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
        keystate = pygame.key.get_pressed()

        # clear/erase the last drawn sprites
        all.clear(screen, background)

        #update all the sprites
        all.update()
        
        #handle player input
#        direction = keystate[K_RIGHT] - keystate[K_LEFT]
        player.move(direction)
#        firing = keystate[K_SPACE]
        if not player.reloading and firing and len(shots) < MAX_SHOTS:
            Shot(player.gunpos())
            shoot_sound.play()
        player.reloading = firing

        # Create new alien
        if alienreload:
            alienreload = alienreload - 1
        elif not int(random.random() * ALIEN_ODDS):
            Alien()
            alienreload = ALIEN_RELOAD

        # Drop bombs
        if lastalien and not int(random.random() * BOMB_ODDS):
            Bomb(lastalien.sprite)

        # Detect collisions
        for alien in pygame.sprite.spritecollide(player, aliens, 1):
            boom_sound.play()
            Explosion(alien)
            Explosion(player)
            SCORE = SCORE + 1
            player.kill()

        for alien in pygame.sprite.groupcollide(aliens, shots, 1, 1).keys():
            if alien == target_alien:
                is_killed = True
            boom_sound.play()
            Explosion(alien)
            SCORE = SCORE + 1

        for bomb in pygame.sprite.spritecollide(player, bombs, 1):
            boom_sound.play()
            Explosion(player)
            Explosion(bomb)
            player.kill()

        #Agent: State Model
        #bombs order by distance
        bomb_dict = {}
        for i in range(0, len(bombs.sprites())):
            dx = bombs.sprites()[i].rect.centerx - player.rect.centerx
            dy = bombs.sprites()[i].rect.centery - player.rect.centery
            distance = math.sqrt(dx * dx + dy * dy)
            bomb_dict[distance] = bombs.sprites()[i]
        bomb_keys = list(bomb_dict.keys())
        bomb_keys.sort(reverse = False)
        bomb_list = []
        for i in range(0, len(bomb_keys)):
            bomb_list.append(bomb_dict[bomb_keys[i]])
        #bombs find a bomb on the top of the player as S
        cur_bomb_count = 0
        max_bomb_count = 1
        bomb_state = ''
        for i in range(0, len(bomb_list)):
            dx = bomb_list[i].rect.centerx - player.rect.centerx #left: -, right +
            dy = player.rect.centery - bomb_list[i].rect.centery #top +
            if abs(dx) > player.rect.width / 2 + bomb_list[i].rect.width * 2:
                continue
            if player.rect.centerx >= player.rect.width / 2 and \
               player.rect.centerx <= player.rect.width and dx >= 0:
                dx = dx - player.rect.width / 2 + player.rect.centerx - player.rect.width / 2
            if player.rect.centerx >= 640 - player.rect.width and \
               player.rect.centerx <= 640 - player.rect.width / 2 and dx < 0:
                dx = dx + player.rect.width / 2 - (player.rect.centerx - (640 - player.rect.width / 2))
            if dx < 0:
                ddx = math.ceil(dx / bomb_list[i].rect.width)
            else:
                ddx = math.floor(dx / bomb_list[i].rect.width)
            ddy = math.ceil(dy / bomb_list[i].rect.height)
            bomb_state += '(' + str(ddx) + ',' + str(ddy) + ')'
            cur_bomb_count += 1
            if cur_bomb_count >= max_bomb_count:
                break

        #aliens order by y
        alien_dict = {}
        for i in range(0, len(aliens.sprites())):
            dx = aliens.sprites()[i].rect.centerx - player.rect.centerx
            dy = aliens.sprites()[i].rect.centery - player.rect.centery
            distance = math.sqrt(dx * dx + dy * dy)
            alien_dict[dy] = aliens.sprites()[i]
        alien_keys = list(alien_dict.keys())
        alien_keys.sort(reverse = True)
        alien_list = []
        for i in range(0, len(alien_keys)):
            alien_list.append(alien_dict[alien_keys[i]])
        #aliens find the nearest one as S
        cur_alien_count = 0
        max_alien_count = 1
        alien_state = ''
        target_alien = ''
        for i in range(0, len(alien_list)):
            dx = alien_list[i].rect.centerx - player.rect.centerx
            dy = player.rect.centery - alien_list[i].rect.centery
            if dx < 0:
                ddx = math.floor(dx / alien_list[i].rect.width)
            else:
                ddx = math.ceil(dx / alien_list[i].rect.width)
            ddy = math.ceil(dy / alien_list[i].rect.height)
            alien_state += '(' + str(ddx) + ',' + str(ddy) + ',' + str(alien_list[i].facing) + ')'
            cur_alien_count += 1
            if target_alien != '' and is_killed == False and alien_list[i].rect.centery > target_alien.rect.centery:
                is_missed = True
            target_alien = alien_list[i]
            if cur_alien_count >= max_bomb_count:
                break    
        
        prev_state = curr_state
        curr_state = {
            'bomb': bomb_state,
            'alien': alien_state
            #'firing': len(shots)
        }
        #print(curr_state)
        agent.add_state(curr_state, ['L', 'R', 'F'])
        ###
        #Agent: Get action
        #direction: left = -1, right = 1
        #firing = 1
        prev_action = curr_action
        curr_action = agent.get_action(curr_state)
        direction = 0
        firing = 0
        if curr_action == 'L':
            direction = -1
        elif curr_action == 'R':
            direction = 1
        elif curr_action == 'F':
            firing = 1
        ###
        #Agent: Study
        if prev_action != '':
            reward = 0
            if is_missed:
                #reward = -50
                is_missed = False
            if is_killed:
                reward = 1
                is_killed = False
            if not player.alive():
                reward = -1000

            agent.study(prev_state, prev_action, curr_state, reward)
        ###
            
        #draw the scene
        dirty = all.draw(screen)
        pygame.display.update(dirty)

        #cap the framerate
        clock.tick(60)

    #restart game constants
    global PLAY_TIMES
    PLAY_TIMES = PLAY_TIMES + 1
    agent.training += 1
    print('ROUND ' + str(agent.training) + \
          ': ' + str(SCORE).zfill(2) + \
          ', S: ' + str(len(agent.Q.keys())) + \
          ', Zero: ' + str(agent.get_Q_zero_count())
          )
    agent.save_data()
###
    
#    if pygame.mixer:
#        pygame.mixer.music.fadeout(1000)
#    pygame.time.wait(1000)
    f = open ( 'score.txt' , 'w+' )
    f.write ( str ( SCORE ) )
    f.close()

    pygame.quit()


#call the "main" function if running this script
if __name__ == '__main__':
    main()
