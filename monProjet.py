from classes.Game2D import Game2D, Player, Event, Animation, LifeBar, EntitiesManager
from classes.common import Color, Shape, Circle, Text


class MyGame(Game2D):
    def __init__(
        self,
        caption,				# Titre du jeu
        game2D_width=6000,		# Espace du jeu en largeur en pixel
        game2D_height=800,		# Espace du jeu en hauteur en pixel
        screen_width=1200,		# Largeur de l’écran en pixel
        screen_height=600,		# Hauteur de l’écran en pixel
        fill_color=Color.LIGHTGRAY,	# Couleur du fond de l’écran
        fps=20				# Nombre d’images par seconde
    ):
        super().__init__(
            caption,
            game2D_width,
            game2D_height,
            screen_width,
            screen_height,
            fill_color,
            fps,
        )

    def generatePlayer(self):
        # Création d'un joueur
        player = Player(300, 200, 10, 20, Color.GREEN)

        # Définition des animations du joueur
        ANIMATIONS_PLAYER = {"DOWN" : ["devant01.png",
                                            "devant02.png",
                                            "devant03.png"],
                             "UP" : ["dos01.png",
                                          "dos02.png",
                                          "dos03.png"],
                             "LEFT" : ["cotegauche01.png",
                                               "cotegauche02.png",
                                               "cotegauche03.png"],
                             "RIGHT" : ["cotedroit01.png",
                                                 "cotedroit02.png",
                                                 "cotedroit03.png"],
                             "IDLE" : ["attendredevant.png"],
                             "IDLEDOWN" : ["attendredevant.png"],
                             "IDLEUP" : ["attendredos.png"],
                             "IDLELEFT" : ["attendregauche.png"],
                             "IDLERIGHT" : ["attendredroit.png"]}

        SOUNDS_PLAYER = { "UP" : ["jump_01.wav"],
                          "LEFT" : ["SF-course_beton-2.mp3"],
                          "RIGHT" : ["SF-course_beton-2.mp3"]}

        animation = Animation(ANIMATIONS_PLAYER, "images/player", delay=5, soundAnimation = SOUNDS_PLAYER, soundPath = "sounds")

        # Affextation de l'animation au joueur
        player.loadAnimations(animation, "IDLE", 15, 40)

        return player

    def generateToken(self):
        # Animations graphiques du jeton
        ANIMATIONS_TOKEN = {
            "WAIT": ["token01.png", "token02.png", "token03.png", "token04.png"],
            "DEAD": ["token_dead.png"],
        }
        # son lorsque le jeton est touché par le joueur
        SOUNDS_TOKEN = { "DEAD" : ["hit_12.wav"]}

        # création de l'animation du jeton
        animationToken = Animation(ANIMATIONS_TOKEN, "images/token", (64, 64), delay=1, soundAnimation = SOUNDS_TOKEN, soundPath = "sounds")
        # création d'un token et affectation de son animation
        token = Circle(50, 50, 30, (255, 255, 0))
        token.loadAnimations(animationToken, "WAIT")
        return token

    def generateMonster(self):

        ANIMATIONS_MONSTER = {
            "DEAD": ["Pink_Monster_Dead_4.png:4:H"],
            "WALK": ["Pink_Monster_Walk_6.png:6:H"],
        }

        SOUNDS_MONSTER = { "DEAD" : ["sf_defenestration_01.mp3"]}

        animationMonster = Animation(ANIMATIONS_MONSTER, "images/Monsters", (32, 32), delay=1, soundAnimation = SOUNDS_MONSTER, soundPath = "Sounds")

        monster = Shape(300, 750, 32, 32, Color.RED)
        monster.loadAnimations(animationMonster, "WALK", 0, 0)

        return monster

    """
    Organiser tous les déplacements des objets de votre jeu
    """
    def myUpdate(self):
        global nbrLifes

        # Faire bouger les plateformes
        platform01.move()

        # Faire bouger les monstres
        monsters.move()

        monster = monsters.isJumpOnIt(player)
        if monster :
            self.destructionManager.addEntity(monster,1, "DEAD")
            monsters.remove_entity(monster)

        monster = monsters.isCollide(player)
        if monster :
            if nbrLifes > 0:
                self.destructionManager.addEntity(monster,1, "DEAD")
                monsters.remove_entity(monster)
                nbrLifes-=1
                hearts.refresh(nbrLifes)

        # Gestion des collisions avec les tokens
        tokens.move()
        # si collision entre le joueur et un des tokens
        token = tokens.isCollide(player)
                # si un token a été touché alors animer et programmer sa disparition

        if token :
            self.destructionManager.addEntity(token,1, "DEAD")
            tokens.remove_entity(token)
            nbrLifes+=1
            hearts.refresh(nbrLifes)

        # Si le joueur sort de la scène vers le bas, tombe hors du jeu
        if player.rect.y > Game2D.SIZE[1] :
            player.toStartAgain() # le joueur reparet au début de lal scène
            nbrLifes-=1 # il perd une vie
            hearts.refresh(nbrLifes)


    """
    Dessiner tous les objets de votre jeu
    """
    # en arrière
    def myDisplayBehind(self, camera, screen):
        sun.draw(screen)

    # devant
    def myDisplayInFront(self, camera, screen):

        # Dessin des obstacles
        #wall01.draw(camera)
        # Dessin du sol
        #sol.draw(camera)
        # Dessin des plateformes
        platform01.draw(camera)
        platform02.draw(camera)
        platform03.draw(camera)

        tokens.draw(camera)
        monsters.draw(camera)
        # Dessin du joueur
        player.draw(camera)

        numberLevel.draw(screen)

        hearts.draw(screen)




    """
    Initialisation du jeu
    Initialiser tous les objets dont vous aurez besoin pour votre jeu
    """
    def myInitialization(self):
        global sol
        global player
        global platform01
        global platform02
        global platform03
        global wall01
        global sun
        global numberLevel
        global hearts
        global tokens
        global nbrLifes
        global monsters

        # Création d'un sol vert
        sol = Shape(0, Game2D.SIZE[1]-30,
                    Game2D.SIZE[0], 50,
                    Color.GREEN)

        # Création d'un joueur
        player = self.generatePlayer()

        # Indication au moteur du jeu le joueur
        self.setPlayer(player)
        # Création des plateformes
        platform01 = Shape(5000, 480, 300, 30, (77, 52, 37))
        platform02 = Shape(730, 380, 500, 30, (77, 52, 37))
        platform03 = Shape(1260, 280, 50, 30, (77, 52, 37))

        # Création de murs
        wall01 = Shape(730, 390, 500, 700, (255,200,10))

        # Création d'un soleil
        sun = Circle(700, 200, 150, (255,255,0))

        numberLevel = Text("Niveau : 01", (Game2D.SCREEN_SIZE[0]/2)-40 , Game2D.SCREEN_SIZE[1]-40, Color.RED)


        # Génération des jetons
        token = self.generateToken()
        # générateur de topkens
        #tokens = EntitiesManager(token, 10, 100, 150, Game2D.SIZE[0], Game2D.SIZE[1]-300)
        tokens = EntitiesManager(token, ((120,300),(400,200),(800,100),(1100,210)))
        tokens.goToTarget([0,100],10)


        platform01.goToTarget([0,100],5)

        monster = self.generateMonster()
        monsters = EntitiesManager(monster, 10, 100, 150, Game2D.SIZE[0], Game2D.SIZE[1]-300)

        #monsters = EntitiesManager(monster, ((120,550)))
        monsters.goToTarget(player)
        #monsters.goToTarget([100,0],10)

        nbrLifes = 0
        # génération de la barre des vies
        hearts = LifeBar(nbrLifes, "heart.png", "images/token", 10, Game2D.SCREEN_SIZE[1]-40)

        # Chargement des maps TILED
        self.loadTiled("Farwest Level 01.tmx", "tiled\\")


        # Gestion de l'action de la gravité sur le joueur avec le sol
        # Déclaration des sols
        #self.gravity.addFloor(sol)
        self.gravity.addFloor(platform01)
        self.gravity.addFloor(platform02)
        self.gravity.addFloor(platform03)
        # Déclaration des objets soumis à la gravité
        self.gravity.addObject(player)
        self.gravity.addObject(monsters.getList())

        # Gestion des collisions
        # Déclaration de tous les murs ou objets contre lesquels ont peut rentrer en collision
        # self.collisionsManager.addCollider(wall01)
        # Déclaration des objets en mouvement qui peuvent rentrer en collision
        self.collisionsManager.addMovingObject(player)
        self.collisionsManager.addMovingObject(monsters.getList())

        # Gestion de la force du saut du joueur
        Event.JUMP = 150
        # Gestion de la vitesse de déplacement du joueur
        Event.VELOCITY = 3
        Event.VELOCITY_UP = 1.1
        Event.VELOCITY_MAX = 20


"""
Lancement du jeu
- titre du jeu
- largeur de l'espace du jeu en pixel
- hauteur de l'espace du jeu en pixel
- largeur de la fenêtre de jeu en pixel
- hauteur de la fenêtre de jeu en pixel
- couleur de fond de la fenêtre de jeu
- FPS nombres d'images par seconde
"""

# Amuse-toi à modifier l’écran
myGame = MyGame("Mon premier jeu",
                			6016, 640,
                			1200, 640,
               			 (220, 220, 240), 60)

myGame.run()
