import pygame
from pygame.locals import SRCALPHA
import pygame.math
import random
import time
import os
import copy
import math

DEBUG = False
"""
Palette des couleurs
"""
class Color:
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (50, 100, 255)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (100, 100, 100, 0)
    LIGHTGRAY = (240, 240, 240, 0)
    SHADOW = (50, 50, 50, 20)
    DEFAULT = (255, 255, 255)
    ALPHA = 255

    def random():
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

class CText:

    def draw(screen, x=50, y=50, color=(255, 0, 0)):
        font = pygame.font.Font(None, 14)

        text = f"{x:02d},{y:02d}"
        message = font.render(u'{}'.format(text),
                              True, (255, 255, 255))

        screen.blit(message, (x, y))

"""
Dessin d'un rectangle ou un carré,
    point en haut droit
    point en bas gauche
    couleur de remplissage de la forme
    largeur de la bordure
    couleur de la bordure

    Toutes les autres formes vont hériter de celle-ci

    square = Shape(200, 20, 200, 200, Color.BLUE, 10, Color.GREEN)
    # ombre de la forme
    square.activateShadow(1,5, (1,1))
    rectangle01 = Shape(100, 100, 200, 250, Color.random(), 2, Color.GREEN)
    rectangle01.activateShadow(1,5, (1,1))

"""

class Shape(pygame.sprite.Sprite):
    width = 0
    height = 0
    shadow = None
    background = None
    edge = 0

    resistance = 50
    speed = 0
    strengh = 0

    angle = 0

    hide = False
    timer = 0
    start_timer = 0

    stick = False

    target = None
    velocity = 10

    guidance = [0, 0]

    animations = None

    # Initialisation de l'objet
    def __init__(
        self,
        x=10,
        y=10,
        width=50,
        height=50,
        color=Color.DEFAULT
    ):

        # Mémorisation des données pour construire la forme
        self.width = width
        self.height = height
        self.color = color
        self.animations = None

        # Création de la surface pour dessiner la forme
        self.surface = pygame.Surface((self.width, self.height))
        pygame.draw.rect(self.surface, self.color, self.surface.get_rect())

        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.init_x = x
        self.init_y = y

    def copy(self, x=0, y=0):

        x = self.rect.x if x == 0 else x
        y = self.rect.y if y == 0 else y

        newCopy = Shape(x, y, self.width, self.height, self.color)
        if self.animations:
            newCopy.loadAnimations(self.animations,
                                  self.animations.getCurrentAnimation(),
                                  self.animations.getShift_x(),
                                  self.animations.getShift_y())
        return newCopy

    def activateEdge(self, edge, colorEdge):
        self.edge = edge
        if edge > 0:
            self.background = copy.copy(self.surface)
            self.background = pygame.transform.scale(self.background,
                                                     (self.width + edge,
                                                      self.height + edge))
            pygame.draw.rect(self.background,
                             colorEdge,
                             self.background.get_rect())

    # désactivation de l'ombre
    def disableEdge(self):
        self.background = None

    # activation de l'ombre
    def activateShadow(self, orientation=(5, 5), distance=1.5):

        self.orientation = orientation
        self.distance = distance
        self.shadow = pygame.Surface(
            (self.width * self.distance, self.height * self.distance), SRCALPHA
        )

    # désactivation de l'ombre
    def disableShadow(self):
        self.shadow = None

    # Dessin de la forme sur l'écran
    def draw(self, screen):

        if not self.hide :
            if self.background:
                screen.blit(self.background, (self.rect.x, self.rect.y))

            if self.animations :
                self.animations.draw(screen, self.rect.x, self.rect.y, self.guidance)
            else:
                screen.blit(self.surface,
                        (self.rect.x+(self.edge//2),
                         self.rect.y+(self.edge//2)))
            CText.draw(screen, self.rect.x, self.rect.y)

    def goto(self, x=None, y=None):
        self.rect.x = x if x is not None else self.rect.x
        self.rect.y = y if y is not None else self.rect.y

    def changeSizeBy(self, size):
        self.width = self.width + size if (((self.width + size) > 0) and
                                           ((self.height + size) > 0)) else self.width
        self.height = (self.height +
                       size if (((self.width + size) > 0) and
                                ((self.height + size) > 0)) else self.height)
        self.surface = pygame.transform.scale(self.surface,
                                              (self.width, self.height))

    def setSizeTo(self, percentage=None):
        if percentage and percentage > 0 :
            self.width = (self.width / 100) * percentage
            self.height = (self.height / 100) * percentage
            x = self.rect.x
            y = self.rect.y
            self.surface = pygame.transform.scale(self.surface,
                                                  (self.width, self.height))
            self.rect = self.surface.get_rect()
            self.rect.x = x
            self.rect.y = y

    def rotate(self, angle=None):
        if angle :
            x = self.rect.x
            y = self.rect.y
            self.rect = self.surface.get_rect()
            self.surface = pygame.transform.rotate(self.surface, angle)
            self.rect = self.surface.get_rect(center=self.rect.center)
            self.rect.x = x
            self.rect.y = y

    def setShow(self , show=True, timer=0):
        self.timer = timer
        if timer > 0:
            self.start_timer = time.time()
        self.hide = not show

    def isCollide(self, collider):
        if self.rect.colliderect(collider):
            return True
        else:
            return False

    def isJumpOnIt(self, collider):
        print(collider.getGuidance()[1])
        if collider.getGuidance()[1] < 0 :
            print("saute dessus")
            return True
        else:
            return False

    def setStick(self, stick):
        self.stick = stick

    def isStick(self):
        return self.stick

    def loadAnimations(self, animations, firstAnimation, shift_x = 0, shift_y = 0):
        if animations:
            self.animations = copy.copy(animations)
            self.animations.setCurrentAnimation(firstAnimation, shift_x, shift_y)

    def move(self, guidance = None):

        if self.animations :
            self.animations.move(self.animations.getCurrentAnimation())

        if self.target is not None:

            # Créer les vecteurs pour les positions des objets
            #if isinstance
            target_vec = None

            if isinstance(self.target, pygame.sprite.Sprite):
                target_vec = pygame.math.Vector2([self.target.rect.x, self.target.rect.y])
            elif isinstance(self.target, tuple) or isinstance(self.target, list):
                target_vec = pygame.math.Vector2([self.init_x + self.target[0], self.init_y + self.target[1]])
            elif isinstance(self.target, int):
                target_vec = pygame.math.Vector2([self.init_x + self.target, self.rect.y])
            if target_vec:
                self_vec = pygame.math.Vector2([self.rect.x, self.rect.y])

                # Calculer le vecteur de déplacement
                deplacement_vec = target_vec - self_vec

                self.setGuidance((1 if target_vec[0] > self_vec[0] else -1,1 if target_vec[1] > self_vec[1] else -1))

                inversion = True
                if isinstance(self.target, int):
                    if deplacement_vec[0] < -1*(self.velocity+1) or deplacement_vec[0] > self.velocity+1:
                        inversion=False
                elif isinstance(self.target, list) or isinstance(self.target, tuple):
                    if self.target[0] != 0:
                        if deplacement_vec[0] < -1*(self.velocity+1) or deplacement_vec[0] > self.velocity+1:
                            inversion=False
                    elif self.target[1] != 0:
                        if deplacement_vec[1] < -1*(self.velocity+1) or deplacement_vec[1] > self.velocity+1:
                            inversion=False
                    else:
                        inversion=False
                else:
                    inversion=False

                if inversion:

                    if isinstance(self.target, int):
                        self.target *= -1
                    elif isinstance(self.target, list):
                        self.target[0] *= -1
                        self.target[1] *= -1
                    else:
                        self.target = None

                else:

                    try:
                        deplacement_vec.normalize_ip()
                        # Multiplier par la vitesse de déplacement
                        deplacement_vec *= self.velocity
                        # Déplacer l'objet 1
                        self_vec += deplacement_vec
                        self.rect.x = int(self_vec.x)
                        if isinstance(self.target, tuple) or isinstance(self.target, list):
                            self.rect.y = int(self_vec.y)
                        if self.animations :
                            self.animations.move(self.animations.getCurrentAnimation())

                    except ValueError as e:
                        self.target = None
                    except Exception as e:
                        self.target = None


    def getAnimationCurrent(self):
        if self.animations :
            return self.animations.getCurrentAnimation()
        else:
            None

    def setAnimation(self, animation = None, velocity = None):
        if velocity:
            self.velocity = velocity

        if animation :
            if self.animations:
                self.animations.setCurrentAnimation(animation)


    def distance(self, objet) :
        return math.sqrt((self.rect.x - objet.rect.x)**2 + (self.rect.y - objet.rect.y)**2)


    def goToTarget(self, target, velocity = 10):
        self.target = target
        self.velocity = velocity

    def setGuidance(self, guidance):
        self.guidance = guidance

    def getGuidance(self):
        return self.guidance

    def getX(self):
        return self.rect.x

    def getY(self):
        return self.rect.y

    def toStartAgain(self):
        self.rect.x = self.init_x
        self.rect.y = self.init_y

"""
Dessin d'un polygone à plusieurs cotés
    liste des points
    couleur de remplissage de la forme

    polygon = Polygon([(150, 10), (200, 100), (100, 100)], Color.RED)
    # ombre de la forme
    polygon.activateShadow(1,5, (1,1))

"""
class Polygon(Shape):
    def __init__(self, coordinates=None, color=Color.DEFAULT):

        self.color = color
        self.coordinates = []

        self.x = 999999
        self.y = 999999
        self.width = 0
        self.height = 0
        for coordinate in coordinates:
            if coordinate[0] < self.x :
                self.x = coordinate[0]
            if coordinate[1] < self.y :
                self.y = coordinate[1]
            if coordinate[0] > self.width :
                self.width = coordinate[0]
            if coordinate[1] > self.height :
                self.height = coordinate[1]

        for coordinate in coordinates:
            self.coordinates.append((coordinate[0]-self.x, coordinate[1]-self.y))

        self.width = self.width - self.x
        self.height = self.height - self.y

        self.surface = pygame.Surface((self.width, self.height), SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        self.rect = self.surface.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        pygame.draw.polygon(self.surface, self.color, self.coordinates)

"""
Dessin du cercle
    Coordonnées du centre
    Rayon
    Couleur de remplissage ou None si pas de remplissage
    largeur du bordure
    couleur du bord

    circle = Circle(600, 300, 50, None, 5, Color.RED)
    # ombre de la forme
    circle.activateShadow(1,5, (,1))

"""
class Circle(Shape):
    def __init__(self, x=10, y=10, radius=10, color=Color.DEFAULT):
        self.color = color
        self.radius = radius
        self.width = self.radius * 2
        self.height = self.radius * 2
        self.surface = pygame.Surface((self.width, self.height), SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.init_x = x
        self.init_y = y

        pygame.draw.circle(self.surface, self.color,
                           (self.radius, self.radius),
                           self.radius)

    def copy(self, x=0, y=0):

        x = self.rect.x if x == 0 else x
        y = self.rect.y if y == 0 else y

        newCopy = Circle(x, y, self.radius, self.color)
        if self.animations:
            newCopy.loadAnimations(self.animations,
                                  self.animations.getCurrentAnimation(),
                                  self.animations.getShift_x(),
                                  self.animations.getShift_y())
        return newCopy


"""
Dessin d'une ellipse
    Coordonnées des points de l'élipse
    Couleur de l'élipse

    ellipse = Ellipse((Screen.SIZE[0]/2-50, 10, 300, 100), Color.RED)
    # ombre de la forme
    ellipse.activateShadow(1.5, (1,1))


"""
class Ellipse(Shape):
    def __init__(self, coordinates=[10, 10, 50, 50], color=Color.DEFAULT):

        self.color = color
        self.coordinates = [0, 0, coordinates[2], coordinates[3]]
        self.width = coordinates[2]
        self.height = coordinates[3]
        self.surface = pygame.Surface((self.width, self.height), SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        self.rect = self.surface.get_rect()
        self.rect.x = coordinates[0]
        self.rect.y = coordinates[1]
        pygame.draw.ellipse(self.surface,
                            self.color,
                            self.coordinates)

"""
Dessin d'un trait
    Coordonnées de départ
    Coordonnées de fin
    Couleur du trait
    Largeur du trait

    line = Line((10, 10), (100, 100), Color.RED, 1)
    # ombre de la forme
    line.activateShadow(1.5, (1,1))

"""
class Line(Shape):
    def __init__(self,
                 startPoint=(0, 0),
                 endPoint=(10, 10),
                 color=Color.DEFAULT,
                 thickness=1):

        self.color = color
        self.thickness = thickness
        self.width = endPoint[0] - startPoint[0]
        self.height = endPoint[1] - startPoint[1]
        self.startPoint = (0, 0)
        self.endPoint = (endPoint[0] - startPoint[0], endPoint[1] - startPoint[1])

        self.surface = pygame.Surface((self.width, self.height), SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        self.rect = self.surface.get_rect()
        self.rect.x = startPoint[0]
        self.rect.y = startPoint[1]
        pygame.draw.line(self.surface,
                         self.color,
                         self.startPoint,
                         self.endPoint,
                         self.thickness)

"""
Affichage d'un texte
    Texte à afficher
    x
    y
    Couleur
    Font à utiliser
    Taille de la police

    text = Text(10.5, 125, 225, Color.RED)
    # ombre de la forme
    text.activateShadow(1,5, (1,1))

"""
class Text(Shape):
    def __init__(
        self,
        text=None,
        x=0,
        y=0,
        color=Color.DEFAULT,
        font_name=None,
        size=50,
    ):
        self.font = pygame.font.Font(font_name, size)
        self.x = x
        self.y = y
        self.text = text
        self.color = color

        self.surface = self.font.render(u'{}'.format(self.text), True, self.color)
        self.surface.fill((0, 0, 0, 0))
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen, text=None):
        if self.timer > 0:
            if (time.time() - self.start_timer >= self.timer):
                self.hide = not self.hide
                self.timer = 0

        if not self.hide :
            if text is None:
                text = self.text
            if text is not str:
                text = str(text)

            if self.shadow and text:
                self.message = self.font.render(u'{}'.format(self.text),
                                                True,
                                                Color.SHADOW)
                self.message.set_alpha(Color.SHADOW[3]
                                       if len(Color.SHADOW) > 3 else 128)
                screen.blit(
                    self.message,
                    (self.rect.x + self.orientation[0],
                     self.rect.y + self.orientation[1]),
                )
            if text:
                self.message = self.font.render(u'{}'.format(text),
                                                True, self.color)
                screen.blit(self.message, (self.rect.x, self.rect.y))

"""
Plannificateur pour le lancement d'objets graphiques
    plannerShappes = PlannerShappes()
    plannerShappes.add(square)
    plannerShappes.add(text)
    plannerShappes.add(image)

    planner.start(3)

"""
class PlannerShapes:
    shapes = []
    currentChrono = 0

    def __init__(self):
        pass

    def add(self, shape):
        self.shapes.append(shape)

    def init(self):
        self.shapes = []

    def start(self, delay=3):
        self.startChrono = time.time()

        self.delay = delay
        self.currentChrono = delay

    def draw(self, screen):
        # print(self.current, self.current - self.start, self.delay * 1000)
        if self.currentChrono > 0:
            # Vérifier si le temps d'affichage est écoulé
            self.currentChrono = time.time()
            if (
                self.currentChrono - self.startChrono >= self.delay
            ):  # Conversion en millisecondes
                self.currentChrono = 0
            # Affichage de tous les objets planifiés
            for shape in self.shapes:
                shape.draw(screen)

"""
Lancement et affichage d'un chronomètre

    textChrono = Text("00:00", 15, 15, Color.RED)
    shapeChrono = Shape(10, 10, 100, 40, Color.BLUE, 2, Color.GREEN)
    chronometer = Chronometer(textChrono, shapeChrono)

"""
class Chronometer:
    chrono = None
    currentChrono = 0
    startChrono = 0
    delay = 0

    def __init__(self, text=None, shape=None):
        if text :
            self.text = text
        else:
            self.text = Text(x=10, y=10)
        self.shape = shape

    def stop(self):
        self.delay = 0
        self.currentChrono = 0
        self.startChrono = 0

    def start(self, delay=3):
        if self.startChrono == 0:
            self.startChrono = time.time()
            self.delay = delay
            self.currentChrono = delay

    def getChrono(self):
        self.currentChrono = 0
        if self.delay > 0:
            # Vérifier si le temps d'affichage est écoulé
            self.currentChrono = time.time()
            if (
                self.currentChrono - self.startChrono >= self.delay
            ):  # Conversion en millisecondes
                self.stop()
        minutes = int((self.delay - (self.currentChrono - self.startChrono)) // 60)
        seconds = int((self.delay - (self.currentChrono - self.startChrono)) % 60)

        return f"{minutes:02d}:{seconds:02d}"

    def draw(self, screen):
        if self.delay > 0 and self.text:
            if self.shape:
                self.shape.draw(screen)
            self.text.draw(screen, self.getChrono())

    def isAlert(self):
        pass

"""
Chargement d'images
"""
class Image:

    def load(path, nameFile, size=None):
        if nameFile:
            try:
                if size:
                    return pygame.transform.scale(
                        pygame.image.load(os.path.join(path, nameFile)), size
                    )
                else:
                    return pygame.image.load(os.path.join(path, nameFile))
            except Exception as e:
                print(
                    "Une erreur est survenue lors de l'ouverture du fichier : "
                    + path
                    + "/"
                    + nameFile,
                    str(e),
                )
                return None
        else:
            return None
"""
Affichage d'une image
"""
class ShapeImage(Shape):

    # Initialisation de l'objet
    def __init__(self, path, nameFile, x=0, y=0, size=None, color=Color.DEFAULT):

        self.color = color
        # Création de la surface pour dessiner la forme
        self.surface = Image.load(path, nameFile, size)
        if not size:
            if self.surface:
                self.width, self.height = self.surface.get_size()
            else:
                self.width, self.height = (32, 32)

        if not self.surface:
            self.surface = pygame.Surface((self.width, self.height), SRCALPHA)
            square = pygame.Rect(0, 0, self.width, self.height)
            pygame.draw.rect(self.surface, self.color, square)

        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y

    # Dessin de la forme sur l'écran
    def draw(self, screen):
        if self.shadow:
            square = pygame.Rect(
                0, 0, self.width * self.distance, self.height * self.distance
            )
            pygame.draw.rect(self.shadow, Color.SHADOW, square)
            screen.blit(
                self.shadow,
                (self.rect.x + self.orientation[0], self.rect.y + self.orientation[1]),
            )

        if self.background:
            screen.blit(self.background, (self.rect.x, self.y))
            screen.blit(self.surface,
                        (self.rect.x + self.edge,
                         self.rect.y + self.edge))
        else:
            screen.blit(self.surface, (self.rect.x, self.rect.y))

class Transform():
    def scale(originalImage=None, scale=None):
        if originalImage and scale:
            return pygame.transform.scale(originalImage, scale)



