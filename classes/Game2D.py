import pygame
from pygame.locals import SRCALPHA
from .common import Color, Shape, Image, ShapeImage
import time
from classes.levelsTiled import Levels_2D
import copy
import random


class LifeBar:

    def __init__(self, nbrLifes, image, path, x=10, y=10, size=(32,32)):

        self.x = x
        self.y = y
        self.size = size
        self.image = image
        self.path = path

        self.refresh(nbrLifes)

    def draw(self, screen):
        for index, heart in enumerate(self.hearts):
            heart.draw(screen)

    def refresh(self, nbrLifes):
        self.hearts = []
        for index in range(0,nbrLifes):
            heart = ShapeImage(self.path, self.image, (index*self.size[0]) + self.x, self.y, self.size)
            self.hearts.append(heart)


class Projectile(pygame.sprite.Sprite):
    SPEED_MOVING = 30

    def __init__(self, x, y, guidance):
        super().__init__()

        self.velocity = 5
        self.image = Image.load("images/","bullet.png",(10,10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.guidance = copy.copy(guidance)

    def move(self):
        if self.guidance[0] != 0:
            self.rect.x = self.rect.x + (self.SPEED_MOVING * self.guidance[0])
            if self.rect.x > Game2D.SCREEN_SIZE[0] or self.rect.x < 0 :
                return True
        elif self.guidance[1] != 0:
            self.rect.y = self.rect.y + (self.SPEED_MOVING * (1 if self.guidance[1] > 0 else -1))
            if self.rect.y > Game2D.SCREEN_SIZE[1] or self.rect.y < 0 :
                return True
        return False

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class Animation(pygame.sprite.Sprite):
    shift_x = 0
    shift_y = 0
    currentAnimation = None
    soundAnimation = None

    def __init__(self, animationGroup, path=None, size=(40, 60), delay=10, soundAnimation = None, soundPath = None):
        super().__init__()

        try:

            scale_image = 1

            self.animationGroup = animationGroup
            # Chargement des images
            for name, animations in self.animationGroup.items():
                new_animations = []
                for index, imageName in enumerate(animations):

                    imageVignettes = imageName.split(":")
                    imageVignettes = [vignette.strip() for vignette in imageVignettes]

                    nbr_decoupage = 1
                    sens_decoupage = "H"

                    for index_vignette, vignette in enumerate(imageVignettes):
                        if index_vignette == 0 :
                            imageName = vignette
                        if index_vignette == 1 :
                            nbr_decoupage = int(vignette)
                        if index_vignette == 2 :
                            sens_decoupage = vignette

                    image = Image.load(path, imageName, (size[0] * nbr_decoupage , size[1]))

                    for col in range(0, nbr_decoupage):
                        # Définir la position de la sous-image
                        rect = pygame.Rect(col * size[0], 0, size[0], size[1])
                        # Découper la sous-image
                        sub_image = image.subsurface(rect)
                        # Ajouter la sous-image à la liste
                        if scale_image != 1:
                            sub_image = pygame.transform.scale(sub_image, (size[0]*scale_image, size[1]*scale_image))
                        # sub_image = pygame.transform.flip(sub_image, True, False)
                        new_animations.append(sub_image)

                self.animationGroup[name] = new_animations

        except ValueError as e:
            self.animationGroup = None
        except Exception as e:
            self.animationGroup = None

        # Charegement des sons
        self.soundAnimationGroup = soundAnimation

        if self.soundAnimationGroup != None:
            for name, sounds in self.soundAnimationGroup.items():
                for index, sound in enumerate(sounds):
                    sounds[index] = pygame.mixer.Sound(soundPath + "\\" + sound)
                    self.soundAnimationGroup[name] = sounds

        self.delay = delay
        self.index = 0
        self.currentAnimation = None
        self.imageAnimation = None
        self.last_tick = pygame.time.get_ticks()

    def move(self, animation):

        if self.animationGroup != None:
            if animation and animation == self.currentAnimation :
                if pygame.time.get_ticks() - self.last_tick >= (self.delay*Game2D.fps):
                    self.last_tick = pygame.time.get_ticks()
                    self.index += 1
                    if self.index >= len(self.animationGroup[animation]):
                        self.index = 0
            else:
                self.currentAnimation = animation
                self.index = 0
                self.last_tick = pygame.time.get_ticks()

                if self.soundAnimation!= None:
                    self.soundAnimation.stop()
                    self.soundAnimation = None

                if self.soundAnimationGroup != None and animation in self.soundAnimationGroup:
                        self.soundAnimation = self.soundAnimationGroup[animation][0]

            self.imageAnimation = self.animationGroup[animation][self.index]

    # Dessin du joueur et des animations
    def draw(self, screen, x=0, y=0, guidance = (0,0)):

        if self.imageAnimation :
            if guidance[0] < 0 :
                self.imageInversion = pygame.transform.flip(self.imageAnimation, True, False)
                screen.blit(self.imageInversion, (x-self.shift_x, y-self.shift_y))
            else:
                screen.blit(self.imageAnimation, (x-self.shift_x, y-self.shift_y))

            if self.soundAnimation !=None and self.index == 0 :
                if not pygame.mixer.get_busy():
                    self.soundAnimation.play()


    def setCurrentAnimation(self, animation, shift_x=0, shift_y=0):
        if self.currentAnimation != animation:
            self.currentAnimation = animation
            self.index = 0
            self.last_tick = pygame.time.get_ticks()
            if shift_x > 0 :
                self.shift_x = shift_x
            if shift_y > 0 :
                self.shift_y = shift_y

            # Animation du joueur en fonction de sa direction
            if self.animationGroup != None:
                self.imageAnimation = self.animationGroup[self.currentAnimation][self.index]

            if self.soundAnimation!= None:
                self.soundAnimation.stop()
                self.soundAnimation = None
            if self.soundAnimationGroup != None and animation in self.soundAnimationGroup:
                    self.soundAnimation = self.soundAnimationGroup[animation][0]

    def getCurrentAnimation(self):
        return self.currentAnimation

    def getShift_x(self):
        return self.shift_x

    def getShift_y(self):
        return self.shift_y


class DestructionManager:
    def __init__(self):
        self.entitiesDestroyGroup = []

    def addEntity(self, entity, delay = 0, animation = None):

        newEntity = copy.copy(entity)
        self.entitiesDestroyGroup.append((newEntity, delay, pygame.time.get_ticks()))

        if newEntity.animations and animation :
            newEntity.animations.move(animation)

    def move(self):

        for item_deleted in self.entitiesDestroyGroup:
            entity_deleted = item_deleted[0]
            delay = item_deleted[1]
            last_ticks = item_deleted[2]

            if pygame.time.get_ticks() - last_ticks >= (delay*1000):
                self.entitiesDestroyGroup = [item for item in self.entitiesDestroyGroup if item != item_deleted]

        for item in self.entitiesDestroyGroup:
            item[0].move()

    def draw(self, screen):
        for item in self.entitiesDestroyGroup:
            item[0].draw(screen)


class EntitiesManager:

    def __init__(self, entity, pointsList = None, start_x=0, start_y=0, end_x=0, end_y=0):
        self.entitiesGroup = []

        if end_x == 0 and end_y==0:
            end_x = Game2D.SIZE[0]

        if entity is not None and pointsList is not None:
            if isinstance(pointsList, int):
                for index in range(0, pointsList):
                    x = random.randint(start_x, end_x) if end_x > 0 else start_x
                    y = random.randint(start_y, end_y) if end_y > 0 else start_y
                    new = entity.copy(x, y)
                    self.entitiesGroup.append(new)

            if isinstance(pointsList, tuple) or isinstance(pointsList, list):
                if len(pointsList) > 1 :
                    for point in pointsList:
                        new = entity.copy(point[0], point[1])
                        self.entitiesGroup.append(new)
                else:
                    new = entity.copy(pointsList[0], pointsList[1])
                    self.entitiesGroup.append(new)


    def addEntity(self, entity):
        self.entitiesGroup.append(entity)

    def move(self):

        for entity in self.entitiesGroup:
            entity.move()

    def draw(self, screen):
        for entity in self.entitiesGroup:
            entity.draw(screen)

    def getList(self):
        return self.entitiesGroup

    def isCollide(self, collider):

        for entity in self.entitiesGroup:
            if entity.rect.colliderect(collider):
                return entity

        return None

    def isJumpOnIt(self, collider):
        for entity in self.entitiesGroup:
            if entity.isJumpOnIt(collider):
                return entity

        return None

    def remove_entity(self, entity_deleted):
        self.entitiesGroup = [entity for entity in self.entitiesGroup if entity != entity_deleted]


    def goToTarget(self, target, velocity = 10):

        for entity in self.entitiesGroup:
            entity.goToTarget(target, velocity)


class Player(Shape):

    def __init__(
        self,
        x=10,
        y=10,
        width=50,
        height=50,
        color=Color.DEFAULT
    ):
        super().__init__(x, y, width, height, color)

        self.state = "IDLE"
        self.guidance = [0, 0]
        self.start_moving = time.time()
        self.speed_moving = Event.VELOCITY
        self.threshold_moving = 0.3
        self.start_idle = time.time()
        self.threshold_idle = 0.5
        self.all_projectiles = pygame.sprite.Group()

    def move(self, guidance):

        if guidance[0] == 0 and guidance[1] == 0:
            self.guidance[1] = 0
            self.start_moving = time.time()
            if self.state and self.state[0:4] != "IDLE":
                self.state = "IDLE" + self.state
                self.start_idle = time.time()
            else:
                if ((time.time() - self.start_idle) > self.threshold_idle):
                    self.state = "IDLE"
        else:
            if ((time.time() - self.start_moving) > self.threshold_moving) :
                self.speed_moving *= Event.VELOCITY_UP
                if self.speed_moving > Event.VELOCITY_MAX:
                    self.speed_moving = Event.VELOCITY_MAX
            else:
                self.speed_moving = Event.VELOCITY
            if guidance[0] > 0:
                self.state = "RIGHT"
                self.guidance[0] = guidance[0]
                self.rect.x = self.rect.x + (self.speed_moving * guidance[0])
                if self.rect.x + self.width > Game2D.SIZE[0] :
                    self.rect.x = Game2D.SIZE[0] - 1

            if guidance[0] < 0:
                self.state = "LEFT"
                self.guidance[0] = guidance[0]
                self.rect.x = self.rect.x + (self.speed_moving * guidance[0])
                if self.rect.x - self.width < 0 :
                    self.rect.x = 1 - self.width
            if guidance[1] > 0:
                self.state = "DOWN"
                self.guidance[1] = guidance[1]
                self.rect.y = self.rect.y + guidance[1]
            if guidance[1] < 0 and self.isStick():
                #if self.guidance[1] == 0:
                self.state = "UP"
                self.guidance[1] = guidance[1]
                self.rect.y = self.rect.y + guidance[1]

        if Event.lauch:
            self.start_idle = time.time()
            self.addProjectiles(self.guidance)

        if self.animations :
            self.animations.move(self.state)

        x = (self.rect.x - (Game2D.SCREEN_SIZE[0]//2)
             if self.rect.x > (Game2D.SCREEN_SIZE[0]//2) else 0)
        y = (self.rect.y - (Game2D.SCREEN_SIZE[1]//2)
             if self.rect.y > (Game2D.SCREEN_SIZE[1]//2) else 0)
        if (Game2D.SIZE[0] - self.rect.x) < (Game2D.SCREEN_SIZE[0]//2):
            x = Game2D.SIZE[0] - (Game2D.SCREEN_SIZE[0])
        if (Game2D.SIZE[1] - self.rect.y) < (Game2D.SCREEN_SIZE[1]//2):
            y = Game2D.SIZE[1] - (Game2D.SCREEN_SIZE[1])

        if len(self.all_projectiles) > 0 :
            for projectile in self.all_projectiles:
                if projectile.move():
                    pygame.sprite.Group.remove(self.all_projectiles, projectile)

        return x, y

    def draw(self, screen):
        if not self.hide :

            if self.animations :
                self.animations.draw(screen, self.rect.x, self.rect.y)
            else:
                screen.blit(self.surface, (self.rect.x, self.rect.y))

            if len(self.all_projectiles) > 0 :
                for projectile in self.all_projectiles:
                    projectile.draw(screen)

    def addProjectiles(self, guidance):
        if guidance[0] != 0 or guidance[1] != 0:
            self.all_projectiles.add(Projectile(self.rect.x, self.rect.y, guidance))

class Event:
    quit = False
    key = 0
    keydown = False
    guidance = [0, 0]
    mouse = False
    mousexy = [0, 0]
    button1 = False
    button2 = False
    lauch = False

    JUMP = 10
    VELOCITY = 1
    VELOCITY_MAX = 20
    VELOCITY_UP = 1.1

    key = 0

    def set(events):
        Event.quit = False
        Event.keydown = False
        Event.mouse = False
        Event.button1 = False
        Event.button2 = False
        Event.lauch = False
        for event in events:
            if event.type == pygame.QUIT:
                Event.quit = True

            elif event.type == pygame.KEYDOWN:
                Event.keydown = True
                Event.key = event.key
                if event.key == pygame.K_ESCAPE:
                    Event.quit = True
                # Gestion du clavier et des mouvements
                if event.key == pygame.K_LEFT:
                    Event.guidance[0] = (-1*Event.VELOCITY)
                elif event.key == pygame.K_RIGHT:
                    Event.guidance[0] = Event.VELOCITY
                elif event.key == pygame.K_UP:
                    Event.guidance[1] = Event.JUMP * (-1)
                elif event.key == pygame.K_SPACE:
                    Event.lauch = True
                elif event.key == pygame.K_DOWN:
                    Event.guidance[1] = Event.VELOCITY
                """
                else:
                    Event.guidance[0] = 0
                    Event.guidance[1] = 0
                """
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    Event.guidance[0] = 0
                if event.key == pygame.K_UP :
                    Event.guidance[1] = 0
                Event.lauch = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    Event.mouse = True
                    Event.button1 = True
                elif event.button == 3:
                    Event.mouse = True
                    Event.button2 = True
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if not (Event.mousexy[0] == x) or not (Event.mousexy[1] == y):
                    Event.mouse = True
                    Event.mousexy[0], Event.mousexy[1] = event.pos

class CollisionsManager:
    def __init__(self):
        self.collidersGroup = []
        self.movingObjectsGroup = []

    def addCollider(self, collider):
        self.collidersGroup.append(collider)

    def addMovingObject(self, movingObject):
        if isinstance(movingObject, list):
            for mobject in movingObject:
                self.movingObjectsGroup.append(mobject)
        else:
            self.movingObjectsGroup.append(movingObject)

    def move(self):

        for collider in self.collidersGroup:

            if isinstance(collider, pygame.sprite.Sprite):
                for movingObject in self.movingObjectsGroup:
                    guidance = movingObject.getGuidance()
                    if movingObject.rect.colliderect(collider):
                        if (movingObject.rect.y + movingObject.height - 10) > collider.rect.y:

                            if guidance[0] > 0:
                                movingObject.rect.x = collider.rect.x - movingObject.width
                            if guidance[0] < 0:
                                movingObject.rect.x = collider.rect.x + collider.width

            if isinstance(collider, pygame.sprite.Group):
                for movingObject in self.movingObjectsGroup:
                    guidance = movingObject.getGuidance()
                    collides = pygame.sprite.spritecollide(movingObject, collider, False)
                    if collides and len(collides) > 0:
                        if (movingObject.rect.y + movingObject.height - 10) > collides[0].rect.y:
                            if guidance[0] > 0:
                                movingObject.rect.x = collides[0].rect.x - movingObject.width - movingObject.velocity
                            if guidance[0] < 0:
                                movingObject.rect.x = collides[0].rect.x + collides[0].width + movingObject.velocity

class Gravity:
    def __init__(self, gravity=20):
        self.gravity = gravity // 10
        self.collidersGroup = []
        self.collidersFloor = []

    def addFloor(self, floor):
        self.collidersFloor.append(floor)

    def addObject(self, obj):
        if isinstance(obj, list):
            for mobj in obj:
                self.collidersGroup.append(mobj)
        else:
            self.collidersGroup.append(obj)

    def move(self, guidance):
        if self.collidersGroup and self.collidersFloor :
            for collider in self.collidersGroup:
                if collider in self.collidersFloor:
                    floorTouched = False
                    for floor in self.collidersFloor:
                        if floor is not collider :
                            if isinstance(floor, pygame.sprite.Sprite):
                                if floor.rect.colliderect(collider):
                                    floorTouched = floor
                            if isinstance(floor, pygame.sprite.Group):
                                pass

                    if floorTouched :
                        collider.speed = 0
                        if (floorTouched.resistance / 10) < self.gravity:
                            collider.speed += self.gravity - (floorTouched.resistance / 10)
                            collider.rect.y += collider.speed
                            collider.setGuidance([collider.getGuidance()[0],1])
                        else:
                            collider.rect.y = floorTouched.rect.y - collider.height + 1
                            break
                    else :
                        collider.speed += self.gravity
                        collider.rect.y += collider.speed
                        collider.setGuidance([collider.getGuidance()[0],1])

            for collider in self.collidersGroup:
                if not (collider in self.collidersFloor):
                    floorTouched = None
                    collider.setStick(False)
                    for floor in self.collidersFloor:
                        if floor is not collider :
                            if isinstance(floor, pygame.sprite.Sprite):
                                if floor.rect.colliderect(collider):
                                    floorTouched = floor
                                    break
                            if isinstance(floor, pygame.sprite.Group):
                                collides = pygame.sprite.spritecollide(collider,
                                                                       floor,
                                                                       False)
                                if collides and len(collides) > 0:
                                    floorTouched = collides[0]
                                    break
                    if floorTouched:
                        if (((floorTouched.resistance / 10) < self.gravity) and
                             ((collider.rect.y + collider.height) < (floorTouched.rect.y + floorTouched.height))):
                            collider.speed += self.gravity - (floorTouched.resistance / 10)
                            collider.rect.y += collider.speed
                            collider.setGuidance([collider.getGuidance()[0],1])
                            collider.setStick(True)
                        else:
                            if (floorTouched.rect.y - (collider.rect.y + collider.height)) < 0:

                                if (collider.rect.y - floorTouched.rect.y) > collider.height:
                                    collider.speed += self.gravity
                                    collider.rect.y += collider.speed
                                    collider.setGuidance([collider.getGuidance()[0],1])
                                else:
                                    collider.speed = 0
                                    collider.rect.y = (floorTouched.rect.y -
                                                       collider.height + 1)
                                    collider.setStick(True)
                    else :
                        collider.speed += self.gravity
                        collider.rect.y += collider.speed
                        collider.setGuidance([collider.getGuidance()[0],1])

class Game2D:

    camera_x = 0
    camera_y = 0
    SIZE = [3000, 600]
    SCREEN_SIZE = [800, 600]
    CAPTION = ""
    FILL_COLOR = Color.LIGHTGRAY
    player = None
    stickToFloor = False
    fps = 20

    def __init__(self,
                 caption,
                 game2D_width=3000,
                 game2D_height=3000,
                 screen_width=800,
                 screen_height=600,
                 fill_color=Color.LIGHTGRAY,
                 fps=20):
        self.fps = fps
        self.SIZE[0] = game2D_width
        self.SIZE[1] = game2D_height
        self.SCREEN_SIZE[0] = screen_width
        self.SCREEN_SIZE[1] = screen_height
        self.CAPTION = caption
        self.FILL_COLOR = fill_color
        self.levels = None

    def myUpdate(self):
        pass

    # Modification des objets du jeu
    def update(self):
        # Changement de niveau
        if self.levels:
            if self.levels.getCurrentLevel():
                if self.levels.getCurrentLevel().isChanged():
                    pygame.display.set_caption(self.CAPTION +
                                               " (" +
                                               self.levels.getCurrentLevel().name +
                                               ")")

        self.myUpdate()

        if self.player :
            self.camera_x, self.camera_y = self.player.move(Event.guidance)

        if self.collisionsManager:
            self.collisionsManager.move()

        if self.gravity:
            self.gravity.move(Event.guidance)

        if self.destructionManager:
            self.destructionManager.move()

    def myDisplayBehind(self, surface):
        pass

    def myDisplayInFront(self, surface):
        pass

    # Affichage du jeu
    def display(self):
        self.screen.fill(self.FILL_COLOR)

        camera = pygame.Surface((self.SIZE[0], self.SIZE[1]), SRCALPHA)
        sreen = pygame.Surface((self.SCREEN_SIZE[0], self.SCREEN_SIZE[1]), SRCALPHA)

        self.myDisplayBehind(camera, self.screen)

        self.screen.blit(camera, (self.camera_x*-1, self.camera_y*-1))
        self.screen.blit(sreen, (0, 0))

        # Dessin du niveau par Tiled
        camera = pygame.Surface((self.SIZE[0], self.SIZE[1]), SRCALPHA)
        if self.levels and self.levels.getCurrentLevel():
            self.levels.getCurrentLevel().draw(camera)
        self.screen.blit(camera, (self.camera_x*-1, self.camera_y*-1))

        camera = pygame.Surface((self.SIZE[0], self.SIZE[1]), SRCALPHA)
        sreen = pygame.Surface((self.SCREEN_SIZE[0], self.SCREEN_SIZE[1]), SRCALPHA)


        if self.destructionManager:
            self.destructionManager.draw(camera)

        self.myDisplayInFront(camera, self.screen)


        self.screen.blit(camera, (self.camera_x*-1, self.camera_y*-1))
        self.screen.blit(sreen, (0, 0))

        pygame.display.update()

    def myInitialization(self):
        pass

    def setPlayer(self, player):
        self.player = player

    def loadTiled(self, fileName, path=None):
        self.levels = Levels_2D(fileName, path)

    def run(self):
        # Initialisation du jeu et création de la fenêtre du jeu
        pygame.init()
        self.screen = pygame.display.set_mode((Game2D.SCREEN_SIZE[0],
                                               Game2D.SCREEN_SIZE[1]))
        pygame.display.set_caption(self.CAPTION)

        self.gravity = Gravity()
        self.collisionsManager = CollisionsManager()
        self.destructionManager = DestructionManager()

        running = True

        self.myInitialization()

        if self.levels and self.levels.getCurrentLevel():
            self.gravity.addFloor(self.levels.getCurrentLevel().collidersFloor)
            self.collisionsManager.addCollider(self.levels.getCurrentLevel().collidersGroup)

        while running:

            # Vitesse d'affichage
            pygame.time.Clock().tick(self.fps)

            # Gestion des intéractions clavier avec le joueur
            Event.set(pygame.event.get())
            if Event.quit:
                running = False
            if Event.key == pygame.KEYDOWN:
                running = False

            # Modification en cours du jeu
            self.update()
            # Affichage du jeu
            self.display()

        # Arrêt du jeu
        pygame.quit()

