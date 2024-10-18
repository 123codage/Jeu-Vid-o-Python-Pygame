import pygame
import xml.etree.ElementTree as ET
from .levelTiled import *

ALPHA = 60
COLLIDER_COLOR = (255,0,0)
# Création d'un collider
# Classe pour gérer les niveaux du jeu
class Levels_2D:


    levels = {}
    nameLevel = ""
    currentLevel = None

    def __init__(self, fileNameTiled=None, path=None):
        if fileNameTiled:
            self.PATHTILED = path
            self.nameLevel = fileNameTiled
            self.level = self.loadTiledXml(self.PATHTILED, fileNameTiled)

    # Objet pour représenter chaque tuile
    class Tile(pygame.sprite.Sprite):
        def __init__(self, image, x, y):
            pygame.sprite.Sprite.__init__(self)
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

    # Objet pour représenter chaque collision
    class Collider(pygame.sprite.Sprite):
        resistance = 5
        def __init__(self, id, cmd, typeCmd, x, y, width, height, resistance):
            pygame.sprite.Sprite.__init__(self)

            self.id = id
            self.width = width
            self.height = height
            self.image = pygame.Surface([width, height])
            # Définir la transparence de la surface pour les zones de collision
            self.image.convert_alpha()
            self.image.set_alpha(ALPHA)
            self.image.fill(COLLIDER_COLOR)

            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

            self.cmd = cmd
            if cmd :
                self.cmd = cmd.split(':')

            self.typeCmd = typeCmd

            self.resistance = resistance

    # Chargement de l'image et découpe en tuiles
    def loadImages(self, nameTiles, imageTiles, firstgid, widthTile, heightTile):
        try:
            image = pygame.image.load(self.PATHTILED+nameTiles).convert_alpha()

            width, height = image.get_size()
            nbrTilesWidth = width//widthTile
            nbrTilesHeight = height//heightTile

            for i in range(firstgid, firstgid+(nbrTilesWidth*nbrTilesHeight)):
                imageTiles.append(None)

            for row in range(nbrTilesHeight):
                for col in range(nbrTilesWidth):
                    # Calcul de l'index du tableau pour charger les images des tuiles
                    index = firstgid+(row*nbrTilesWidth)+col
                    x = widthTile*(col)
                    y = heightTile*(row)
                    # Découpe dans l'image des images des tuiles
                    rect_decoupe = pygame.Rect(x, y, widthTile, heightTile)
                    tile = image.subsurface(rect_decoupe).convert_alpha()
                    # Chargement du tableau des images des tuiles
                    imageTiles[index] = tile

        except FileNotFoundError as e:
            print("Le fichier des niveaux du jeu n'a pas été trouvé : %s" % e)
        except IOError as e:
            print("Erreur d'entrée/sortie : %s" % e)
        except Exception as e:
            print("Une erreur est survenue lors de l'ouverture du fichier " + self.PATHTILED+nameTiles + " : ", str(e))

        return imageTiles

    # Chargement du fichier de configuration du fichier de description des images des tuiles
    def loadTilesetdXml(self, tilesetFile, imageTiles, firstgid, tilewidth, tileheight):
        try:

            tree = ET.parse(self.PATHTILED+tilesetFile)
            root = tree.getroot()
            # Parcourir les tuiles de la carte
            for image in root.findall(".//image"):
                imageTiles = self.loadImages(image.attrib['source'],
                                             imageTiles,
                                             firstgid,
                                             tilewidth,
                                             tileheight)
                firstgid = len(imageTiles)
            self.tiles = []
            for tile in root.findall(".//tile"):
                self.tiles.append({'id': tile.attrib['id']})

        except FileNotFoundError as e:
            print("Le fichier des niveaux du jeu n'a pas été trouvé : %s " % e)
        except IOError as e:
            print("Erreur d'entrée/sortie : %s" % e)
        except Exception as e:
            print("Une erreur est survenue lors de l'ouverture du fichier " + self.PATHTILED+tilesetFile + " : ", str(e))

        return imageTiles

    # Chargement du fichier de configuration du logiciel TILED
    def loadTiledXml(self, pathTiled, fileNameTiled):

        level = None
        levelFile = pathTiled + fileNameTiled if pathTiled else fileNameTiled
        # Chargement des niveaux
        levels = []
        root = None
        try:
            # Charger le fichier XML de la carte Tiled
            # Attributs généraux
            tree = ET.parse(levelFile)
            root = tree.getroot()
        except FileNotFoundError as e:
            print("Le fichier des niveaux du jeu n'a pas été trouvé : %s " % e)
        except IOError as e:
            print("Erreur d'entrée/sortie : %s " % e)
        except Exception as e:
            print("Une erreur est survenue lors de l'ouverture du fichier " + pathTiled + fileNameTiled + " : ", str(e))

        if root:
            width = int(root.attrib['width'])
            height = int(root.attrib['height'])
            tileheight = int(root.attrib['tileheight'])
            tilewidth = int(root.attrib['tilewidth'])

            # Chargement des images des tuiles
            imageTiles = []
            firstgid = 0
            # Parcourir les tuiles de la carte et chargement des images
            for tileset in root.findall(".//tileset"):
                imageTiles = self.loadTilesetdXml(tileset.attrib['source'],
                                                  imageTiles,
                                                  firstgid,
                                                  tilewidth,
                                                  tileheight)
                firstgid = len(imageTiles)

            tilesGroup = pygame.sprite.Group()
            for layer in root.findall(".//layer"):

                layers = [[-1 for j in range(width)] for i in range(height)]
                # Récupérer les données des tuiles (format CSV encodé)
                data = layer.find('data').text
                lignes = data.split('\n') # Séparation initiale par retour chariot

                if lignes and len(lignes) > 0:
                    # Parcourir chaque ligne
                    r = 0
                    for ligne in lignes:
                        # Vérifier si la ligne n'est pas vide après le retrait des espaces et caractères vides
                        if ligne and ligne.strip():
                            # Si la ligne n'est pas vide, découper les valeurs par la virgule et ajouter à la liste des résultats
                            valeurs = ligne.split(',')
                            c = 0
                            for valeur in valeurs:
                                if valeur and valeur.strip() and int(valeur.strip())>0:
                                    layers[r][c] = (int(valeur.strip())-1)
                                c += 1
                            r += 1


                for row in range(height):
                    for col in range(width):
                        x = tilewidth*(col)
                        y = tileheight*(row)

                        if layers[row][col]>=0 and imageTiles[layers[row][col]]:
                            tile = self.Tile(imageTiles[layers[row][col]], x, y)
                            tilesGroup.add(tile)

            # Chargement des zones de collisions du jeu
            collidersGroup = pygame.sprite.Group()
            collidersFloor = pygame.sprite.Group()
            resistance = 5
            for objectgroup in root.findall(".//objectgroup"):
                name = objectgroup.attrib['name']
                classColliderGroup = objectgroup.attrib['class'] if 'class' in objectgroup.attrib else None
                for properties in objectgroup.findall("./properties"):
                    for property in properties.findall(".//property"):
                        if ('name' in property.attrib and
                            property.attrib['name']=="resistance"):
                            resistance = float(property.attrib['value'])

                for objectCollider in objectgroup.findall(".//object"):
                    resistanceCollider = 0
                    for properties in objectCollider.findall("./properties"):
                        for property in properties.findall(".//property"):
                            if ('name' in property.attrib and
                                property.attrib['name']=="resistance"):
                                resistanceCollider = float(property.attrib['value'])

                    if resistanceCollider == 0 :
                        resistanceCollider = resistance

                    collider = self.Collider(objectCollider.attrib['id'],
                                             objectCollider.attrib['name'] if 'name' in objectCollider.attrib else None,
                                             objectCollider.attrib['type'] if 'type' in objectCollider.attrib else None,
                                             float(objectCollider.attrib['x']),
                                             float(objectCollider.attrib['y']),
                                             float(objectCollider.attrib['width']),
                                             float(objectCollider.attrib['height'] if 'height' in objectCollider.attrib else 50),
                                             resistanceCollider)
                    if classColliderGroup=='Floor':
                        collidersFloor.add(collider)
                    else:
                        collidersGroup.add(collider)
            level = Level_2D(fileNameTiled,
                             width,
                             height,
                             tilewidth,
                             tileheight,
                             tilesGroup,
                             collidersFloor,
                             collidersGroup)

        return level

    def getCurrentLevel(self):
        return self.level

    def collide(self, player, direction):
        if self.getCurrentLevel():
            collides = self.getCurrentLevel().collide(player, direction)
            if collides:
                for collide in collides:
                    if collide.cmd:
                        self.nameLevel = collide.cmd[0]
                        if collide.typeCmd == "level":
                            self.level = self.loadTiledXml(self.PATHTILED, self.nameLevel)
                return True
            else:
                return False

