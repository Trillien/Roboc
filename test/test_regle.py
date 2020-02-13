# -*-coding:Utf-8 -*

"""
Ce module contient la classe ``RegleTest``.
"""

from typing import Tuple, Dict, cast, Type, List, Any
from lib.joueur import Joueur
from lib.element import Obstacle, Element, Elements, Decryptable, Traversable, Transformable, Gagnable
from lib.regle import Etat, HorsRegles, PartieGagnee, traverser_un_obstacle, rencontrer_un_adversaire,\
    transformer_un_obstacle, gagner_une_partie
import unittest

# Alias de types
Coordonnees = Tuple[int, int]
Grille = Dict[Coordonnees, Obstacle]


def construire_grille(chaine: str) -> Grille:
    """
    Crée une grille de labyrinthe à partir d'une chaîne de caractères.

    :param chaine: chaîne de caractères.
    :return: grille de labyrinthe.
    """

    grille: Grille = {}
    for ordonnee, ligne in enumerate(chaine.splitlines()):
        for abscisse, caractere in enumerate(ligne):
            grille[(abscisse, ordonnee)] = cast(Obstacle, Elements.get_decryptable(caractere))
    return grille


class RegleTest(unittest.TestCase):
    """
    Test case utilisé pour tester les règles ``traverser_un_obstacle()``, ``rencontrer_un_adversaire()``,
    ``transformer_un_obstacle()`` et ``gagner_une_partie()``.
    """

    def setUp(self) -> None:
        """
        Avant chaque test:

        - Sauvegarde les éléments initialisés par le module **element**.
        - Efface les listes d'éléments ``Decryptable`` et ``Gagnable`` de la métaclasse ``Elements``.
        - Définit les nom, classe d'héritage et attributs des éléments nécessaires aux tests.
        - Crée et stocke les classes dans ``elements``.
        - Crée l'élément ``ElementTransformable``.
        - Instancie la classe ``Joueur`` pour créer un joueur aux coordonées (0, 0).
        - Instancie la classe ``Joueur`` pour créer un adversaire aux coordonnées (1, 0).
        """

        self.decryptable = Elements.decryptable.copy()
        self.gagnable = Elements.gagnable.copy()
        self.obstacle_par_defaut = Elements.obstacle_par_defaut
        Elements.decryptable.clear()
        Elements.gagnable.clear()

        nom = 'MixInTransformation'
        base = (Transformable,)
        dictionnaire = {'description': "transformer"}

        self.MixInTransformation = cast(Type[Transformable], type(nom, base, dictionnaire))

        noms: List[str] = ['ElementObstacle',
                           'ElementSol',
                           'ElementSortie',
                           'ElementTransformable']
        bases: List[Tuple[type, ...]] = [(Element, Decryptable,),
                                         (Element, Decryptable, Traversable,),
                                         (Element, Gagnable,),
                                         (Element, Decryptable, self.MixInTransformation,)]
        dictionnaires: List[Dict[str, Any]] = \
            [{'symbole_affichage': 'X', 'symbole_carte': 'X', 'description': "l'obstacle"},
             {'symbole_affichage': ' ', 'symbole_carte': ' ', 'description': "l'espace"},
             {'symbole_affichage': 'F', 'symbole_carte': 'F', 'description': "la fin"},
             {'symbole_affichage': 'T', 'symbole_carte': 'T', 'description': "l'obstacle transformable"}]
        elements = {}
        for indice in range(len(noms)):
            elements[noms[indice]] = type(noms[indice], bases[indice], dictionnaires[indice])

        # Pour éviter les références circulaires, le membre ``transformee`` de MixInTransformation est défini après les classes
        # d'éléments
        self.MixInTransformation.transformee = elements['ElementTransformable']

        self.joueur = Joueur('identifiant_client', 'Joueur')
        self.joueur.coordonnees = (0, 0)
        self.adversaire = Joueur('identifiant_client', 'Adversaire')
        self.adversaire.coordonnees = (1, 0)

    def tearDown(self) -> None:
        """
        Après chaque test, restaure les listes initiales dans la métaclasse ``Elements``.
        """

        Elements.decryptable = self.decryptable.copy()
        Elements.gagnable = self.gagnable.copy()
        Elements.obstacle_par_defaut = self.obstacle_par_defaut

    def test_traverser_un_obstacle(self) -> None:
        """
        - Crée une grille avec un obstacle aux coordonnées (0, 1).
        - Crée un état de labyrinthe avec un déplacement du Joueur en (1, 0).
        - Teste si la règle retourne une exception.
        - Crée un état de labyrinthe avec un déplacement du Joueur en (0, 1).
        - Teste si la règle retourne une exception.
        """

        grille = construire_grille("  \n"
                                   "X ")
        direction = (1, 0)
        instantane = Etat(direction, None, grille, self.joueur, [])
        traverser_un_obstacle(instantane)

        direction = (0, 1)
        instantane = Etat(direction, None, grille, self.joueur, [])
        with self.assertRaises(HorsRegles):
            traverser_un_obstacle(instantane)

    def test_rencontrer_un_adversaire(self) -> None:
        """
        - Crée une grille sans obstacle.
        - Crée un état de labyrinthe avec un déplacement du Joueur en (1, 0).
        - Teste si la règle retourne une exception.
        - Crée un état de labyrinthe avec un déplacement du Joueur en (0, 1).
        - Teste si la règle retourne une exception.
        """

        grille = construire_grille("  \n"
                                   "  ")
        direction = (1, 0)
        instantane = Etat(direction, None, grille, self.joueur, [self.adversaire])
        with self.assertRaises(HorsRegles):
            rencontrer_un_adversaire(instantane)

        direction = (0, 1)
        instantane = Etat(direction, None, grille, self.joueur, [self.adversaire])
        rencontrer_un_adversaire(instantane)

    def test_transformer_un_adversaire(self) -> None:
        """
        - Crée une grille sans obstacle.
        - Crée un état de labyrinthe avec une transformation de l'élément en (1, 0).
        - Teste si la règle retourne une exception.
        - Crée un état de labyrinthe avec une transformation de l'élément en (0, 1).
        - Teste si la règle retourne une exception.
        """

        grille = construire_grille("  \n"
                                   "  ")
        transformation = self.MixInTransformation
        direction = (1, 0)
        instantane = Etat(direction, transformation, grille, self.joueur, [self.adversaire])
        with self.assertRaises(HorsRegles):
            rencontrer_un_adversaire(instantane)

        direction = (0, 1)
        instantane = Etat(direction, transformation, grille, self.joueur, [self.adversaire])
        rencontrer_un_adversaire(instantane)

    def test_transformer_un_obstacle(self) -> None:
        """
        - Crée une grille avec un obstacle transformable en (1, 0) et un obstacle en (0, 1).
        - Crée un état de labyrinthe avec une transformation de l'élément en (1, 0).
        - Teste si la règle retourne une exception.
        - Crée un état de labyrinthe avec une transformation de l'élément en (0, 1).
        - Teste si la règle retourne une exception.
        """

        grille = construire_grille(" T\n"
                                   "X ")
        transformation = self.MixInTransformation
        direction = (1, 0)
        instantane = Etat(direction, transformation, grille, self.joueur, [])
        transformer_un_obstacle(instantane)

        direction = (0, 1)
        instantane = Etat(direction, transformation, grille, self.joueur, [])
        with self.assertRaises(HorsRegles):
            transformer_un_obstacle(instantane)

    def test_gagner_une_partie(self) -> None:
        """
        - Crée une grille avec une sortie en (0, 1).
        - Crée un état de labyrinthe avec un déplacement du Joueur en (1, 0).
        - Teste si la règle retourne une exception.
        - Crée un état de labyrinthe avec un déplacement du Joueur en (0, 1).
        - Teste si la règle retourne une exception.
        """

        grille = construire_grille("  \n"
                                   "F ")
        direction = (1, 0)
        instantane = Etat(direction, None, grille, self.joueur, [])
        gagner_une_partie(instantane)

        direction = (0, 1)
        instantane = Etat(direction, None, grille, self.joueur, [])
        with self.assertRaises(PartieGagnee):
            gagner_une_partie(instantane)
