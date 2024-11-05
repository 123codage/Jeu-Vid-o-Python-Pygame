from classes.Game2D import Game2D, Player, Event, Animation, LifeBar, EntitiesManager
from classes.common import Color, Shape, Circle, Text, DEBUG, Chronometer


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

        animation = Animation(ANIMATIONS_PLAYER, "images/player", (100, 200),  scale=0.5, delay=5, soundAnimation = SOUNDS_PLAYER, soundPath = "sounds")

        # Affextation de l'animation au joueur
        player.loadAnimations(animation, "IDLE", 20, 80)

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
        animationToken = Animation(ANIMATIONS_TOKEN, "images/token", (128, 128), scale=0.5, delay=1, soundAnimation = SOUNDS_TOKEN, soundPath = "sounds")
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

        animationMonster = Animation(ANIMATIONS_MONSTER, "images/Monsters", (32, 32), scale=2, delay=1, soundAnimation = SOUNDS_MONSTER, soundPath = "Sounds")

        monster = Shape(300, 750, 32, 32*2, Color.RED)
        monster.loadAnimations(animationMonster, "WALK", 16, 0)

        return monster

    def generateFlag(self):

        ANIMATIONS_FLAG = {
            "FLOATING": ["red flag.png:5:H"],
            "FIXED": ["red flag.png:1:H"],
        }

        animationFlag = Animation(ANIMATIONS_FLAG, "images/flag", (64, 64), scale=1, delay=1)

        flag = Shape(200, 513, 64, 64, Color.RED)
        flag.loadAnimations(animationFlag, "FIXED", 0, 0)

        return flag


    """
    Organiser tous les déplacements des objets de votre jeu
    """
    def myUpdate(self):
        global monsters
        global tokens
        global flags

        """
        Chargement des niveaux
        """
        # Chargement du niveau 1
        if self.level == 0 :

            # Chargement des maps TILED
            self.loadTiled("Farwest Level 01.tmx", "tiled\\", level=1, x=200, y=300)

            # Gestion de l'action de la gravité sur le joueur avec le sol
            # Déclaration des sols
            #self.gravity.addFloor(sol)
            self.gravity.addFloor(platform01)
            self.gravity.addFloor(platform02)
            self.gravity.addFloor(platform03)

            # Génération des jetons
            token = self.generateToken()
            # générateur de topkens
            #tokens = EntitiesManager(token, 10, 100, 150, Game2D.SIZE[0], Game2D.SIZE[1]-300)
            tokens = EntitiesManager(token, ((120,300),(400,200),(800,100),(1100,210)))
            tokens.moveToTarget([0,100],10)

            platform01.moveToTarget([0,100],5)

            # Générations des flags
            flag = self.generateFlag()
            flags = EntitiesManager(flag, ((3500,370),(Game2D.SIZE[0]-300, 513)))

        # Chargement du niveau 2
        if self.level == 1 and self.step == 2 and player.rect.x > Game2D.SIZE[0] - 40 :
            self.setDarken()
            self.loadTiled("Farwest Level 02.tmx", "tiled\\", level=2, x=400, y=400)

            platform01.setStartPoint((350,280))
            platform02.setStartPoint((1000,400))
            platform03.setStartPoint((1500,400))
            platform01.goToTarget(platform01.getStartPoint())

            platform01.setColor(Color.BLUE, 100)

            self.gravity.addFloor(platform01)
            self.gravity.addFloor(platform02)
            self.gravity.addFloor(platform03)

            platform01.moveToTarget([0,100],5)
            platform02.moveToTarget([0,200],5)
            platform03.moveToTarget([100,0],5)

            flag = self.generateFlag()
            flags = EntitiesManager(flag, ((800,150),(Game2D.SIZE[0]-300, 513)))


        """
        Mouvements pour tous les niveaux
        """
        # Faire bouger les plateformes
        platform01.move()
        platform02.move()
        platform03.move()

        if monsters :
            monsters.move()
            # Le joueur saute sur le mosntre
            monster = monsters.isJumpOnIt(player)
            if monster :
                # Création d'un monstre qui va mourir
                self.destructionManager.addEntity(monster,1, "DEAD")
                # Destruction du monstre dans la liste des monstres
                monsters.remove_entity(monster)

            # Quand un monstre rencontre le palyer
            monster = monsters.isCollide(player)
            if monster :
                # Le joueur recommence au début du niveau
                self.goToStartOfLevel()
                # Le joueur perd une vie
                if self.player.getNbrLifes() > 0:
                    self.player.lessLifes()
                    hearts.refresh(self.player.getNbrLifes())

        if tokens :
            # Gestion des collisions avec les tokens
            tokens.move()
            # si collision entre le joueur et un des tokens
            token = tokens.isCollide(player)

            # si un token a été touché alors animer et programmer sa disparition
            # Si un jeton touché ajout d'une vie
            if token :
                self.destructionManager.addEntity(token,1, "DEAD")
                tokens.remove_entity(token)
                self.player.moreLifes()
                hearts.refresh(self.player.getNbrLifes())

        # Si le joueur sort de la scène vers le bas, et tombe hors du jeu
        if player.rect.y > Game2D.SIZE[1] :
            self.goToStartOfLevel() # le joueur repart au début de la scène
            self.player.lessLifes() # il perd une vie
            hearts.refresh(self.player.getNbrLifes())

        # Mouvement des indicateurs
        flags.move()
        flag = flags.isCollide(player)
        # Si l'indicateur est touché alors changement d'étape
        if flag and flag.getCurrentAnimation() == "FIXED":
            # Animation du FLAG
            flag.setAnimation("FLOATING")
            # Plus 1 dans les étapes du jeu
            self.setValidationStep(flag)
            chrono.stop()

        """
        Gestion du niveau 1
        """
        if self.level == 1 :
            """
            Génération de monstres au niveau 1 après 3 secondes de jeu
            """
            if monsters == None and self.getChronoLevel() > 3 :
                monster = self.generateMonster()
                monsters = EntitiesManager(monster, 10, 100, 150, Game2D.SIZE[0], Game2D.SIZE[1]-300)
                monsters.moveToTarget(player)
                self.gravity.addObject(monsters)
                self.collisionsManager.addMovingObject(monsters)
            """
            controle du temps du joueur sur le niveau 1
            """
            if self.getChronoStep() >= 10 and not(chrono.isStarted()) :
                chrono.start(10)
            if chrono.isFinished():
                chrono.stop()
                self.goToStartOfLevel() # le joueur repart au début de la scène
                self.player.lessLifes() # il perd une vie
                hearts.refresh(self.player.getNbrLifes())


    """
    Dessiner tous les objets de votre jeu
    """
    # en arrière
    def myDisplayBehind(self, camera, screen):
        pass


    # devant
    def myDisplayInFront(self, camera, screen):

        # Dessin des plateformes
        platform01.draw(camera)
        platform02.draw(camera)
        platform03.draw(camera)

        if tokens :
            # Dessin des jetons
            tokens.draw(camera)
        """
        if flag:
            # Dessin du flag de niveau
            flag.draw(camera)
        """

        # Dessin des monstres
        if monsters :
            monsters.draw(camera)

        # Dessin des monstres
        if flags :
            flags.draw(camera)

        # Dessin du joueur
        player.draw(camera)

        # Affichage du niveau
        if levelDisplay :
            levelDisplay.draw(screen, "Level : " + str(self.level) + " step : " + str(self.step))

        # Affichage des nombre de vies
        hearts.draw(screen)

        chrono.draw(screen)


    """
    Initialisation du jeu
    Initialiser tous les objets dont vous aurez besoin pour votre jeu
    """
    def myInitialization(self):
        global player
        global platform01
        global platform02
        global platform03
        global wall01
        global levelDisplay
        global hearts
        global tokens
        global monsters
        global chrono
        global flags

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

        levelDisplay = Text("", (Game2D.SCREEN_SIZE[0]/2)-40 , Game2D.SCREEN_SIZE[1]-40, Color.RED)

        monsters = None
        tokens = None
        flags = None

        # Déclaration des objets soumis à la gravité
        self.gravity.addObject(player)

        # Déclaration des objets en mouvement qui peuvent rentrer en collision
        self.collisionsManager.addMovingObject(player)

        # Gestion de la force du saut du joueur
        Event.JUMP = 150

        # Gestion de la vitesse de déplacement du joueur
        Event.VELOCITY = 3
        Event.VELOCITY_UP = 1.1
        Event.VELOCITY_MAX = 20

        # Création d'un chronmètre pour indiquer au joueur le temps restant sur une étape du jeu
        chrono = Chronometer(Text("Step finished at : ", Game2D.SCREEN_SIZE[0]/2-180,10))

        # génération de la barre des vies
        hearts = LifeBar(self.player.getNbrLifes(), "heart.png", "images/token", 10, Game2D.SCREEN_SIZE[1]-40)

        DEBUG.active = False

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
