from classes.Game2D import Game2D
from classes.common import Color

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


    """
    Organiser tous les déplacements des objets de votre jeu
    """
    def myUpdate(self):
        pass

    """
    Dessiner tous les objets de votre jeu
    """
    # en arrière
    def myDisplayBehind(self, camera, screen):
        pass

    # devant
    def myDisplayInFront(self, camera, screen):

        pass


    """
    Initialisation du jeu
    Initialiser tous les objets dont vous aurez besoin pour votre jeu
    """
    def myInitialization(self):

        pass

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

