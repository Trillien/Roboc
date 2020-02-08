# -*-coding:Utf-8 -*

"""
Ce module contient
    - les classes d'exception ExceptionLabyrinthe, HorsRegles, PartieGagnee
    - la classe Etat
    - les fonctions verifier_regles(), lister_regles()
      traverser_un_obstacle(), rencontrer_un_adversaire(), gagner_une_partie()
      transformer_un_adversaire(), transformer_un_obstacle()
"""

from typing import Set, Callable, Tuple, Dict, List, Optional, Type, cast
from abc import ABCMeta
from element import Obstacle, Elements, Element, Traversable, Gagnable
from controle import Transformer
from joueur import Joueur

# Alias de types
Coordonnees = Tuple[int, int]
Grille = Dict[Coordonnees, Obstacle]
Regle = Callable[['Etat'], None]


class ExceptionLabyrinthe(BaseException, metaclass=ABCMeta):
    """
    Classe d'exceptions liées aux règles du labyrinthe
    """

    pass


class HorsRegles(ExceptionLabyrinthe):
    """
    Exception levée quand le joueur enfreint une règle du labyrinthe
    """

    pass


class PartieGagnee(ExceptionLabyrinthe):
    """
    Exception levée quand le joueur gagne la partie
    """

    pass


class Etat:
    """
    Représente l'état du labyrinthe à un instant t,
        basé sur la grille d'éléments, le joueur en cours et les adversaires
        et incluant le prochain mouvement à vérifier (la direction et la transformation)

    L'objet instancié est transmis aux fonctions de règles pour valider le mouvement.
    """

    def __init__(self, direction: Coordonnees, transformation: Optional[Transformer],
                 grille: Grille, joueur: Joueur, adversaires: List[Joueur]) -> None:
        """
        Construit les variables nécessaires aux règles à partir de l'état du labyrinthe
        ('grille', 'joueur' et 'adversaires') et du mouvement du joueur ('direction', 'transformation')

        :param Coordonnees direction: vecteur déplacement
        :param transformation: classe dérivée de Transformation
        :type transformation: Transformer ou None
        :param Grille grille: grille d'éléments du labyrinthe
        :param Joueur joueur: joueur en cours
        :param adversaires: liste d'adversaires
        :type adversaires: List[Joueur]
        """

        self.coordonnees_obstacle = (joueur.coordonnees[0] + direction[0], joueur.coordonnees[1] + direction[1])
        try:
            self.obstacle = cast(Type[Element], grille[self.coordonnees_obstacle])
        except KeyError:
            self.obstacle = Elements.obstacle_par_defaut
        self.transformation = transformation
        self.coordonnees_adversaires = [adversaire.coordonnees for adversaire in adversaires]


# Les sets de regles contiennent les références des fonctions de règles
regles_mouvement: Set[Regle] = set()
regles_transformation: Set[Regle] = set()


def verifier_regles(etat: Etat) -> None:
    """
    Définit le set de règles à utiliser selon si le controle est un Mouvement ou une Transformation
    Appelle les règles en leur passant l'état du labyrinthe

    :param Etat etat: état du labyrinthe
    """

    if etat.transformation:
        regles = regles_transformation
    else:
        regles = regles_mouvement
    for regle in regles:
        regle(etat)


def lister_regles(set_de_regles: Set[Regle]) -> Callable[[Regle], Regle]:
    """
    Construit un décorateur qui stocke une règle dans 'set_de_regles'

    :param set_de_regles: le set de règle à utiliser
    :type set_de_regles: Set[Regle]
    :return: décorateur
    :rtype: Callable[[Regle], Regle]
    """

    def decorateur(regle: Regle) -> Regle:
        """
        Décorateur qui stocke une règles dans un set de regles

        :param Regle regle: règle à stocker
        :return: règle sotckée
        :rtype: Regle
        """

        set_de_regles.add(regle)
        return regle
    return decorateur


@lister_regles(regles_mouvement)
def traverser_un_obstacle(self: Etat) -> None:
    """
    Test si l'élément sur lequel le joueur se déplace est traversable.

    :param Etat self: état du labyrinthe
    :raises HorsRegles: si l'élément n'est pas traversable
    """

    if not issubclass(self.obstacle, Traversable):
        raise HorsRegles("Vous ne pouvez pas traverser " + self.obstacle.description + " !")


@lister_regles(regles_mouvement)
@lister_regles(regles_transformation)
def rencontrer_un_adversaire(self: Etat) -> None:
    """
    Test si un autre joueur occupe la position sur laquelle le joueur se déplace
    Test si un autre joueur se trouve sur l'élément à transformer

    :param Etat self: état du labyrinthe
    :raises HorsRegles: si un autre joueur occupe la position
    """

    for coordonnees in self.coordonnees_adversaires:
        if self.coordonnees_obstacle == coordonnees:
            raise HorsRegles("Un joueur occupe déjà " + self.obstacle.description + " !")


@lister_regles(regles_mouvement)
def gagner_une_partie(self: Etat) -> None:
    """
    Test si l'élément sur lequel le joueur se déplace est 'gagnable'.

    :param Etat self: état du labyrinthe
    :raises PartieGagnee: si l'élément est 'gagnable'
    """

    if issubclass(self.obstacle, Gagnable):
        raise PartieGagnee()


@lister_regles(regles_transformation)
def transformer_un_obstacle(self: Etat) -> None:
    """
    Test si l'élément à transformer dérive de la transformation.

    :param Etat self: état du labyrinthe
    :raises HorsRegles: si l'élément ne dérive pas de la transformation
    """

    if self.transformation:
        if not issubclass(self.obstacle, self.transformation):
            raise HorsRegles("Vous ne pouvez pas " + self.transformation.description
                             + " " + self.obstacle.description + " !")
