# -*-coding:Utf-8 -*

"""
Ce module définit les règles du labryinthe.

- les classes d'exception ``ExceptionLabyrinthe``, ``HorsRegles``, ``PartieGagnee``
- la classe ``Etat``
- les fonctions ``verifier_regles()``, ``lister_regles()``, ``traverser_un_obstacle()``, ``rencontrer_un_adversaire()``,
  ``gagner_une_partie()``, ``transformer_un_obstacle()``
"""

from typing import Set, Callable, Tuple, Dict, List, Optional, Type, cast
from abc import ABCMeta
from lib.element import Obstacle, Elements, Element, Traversable, Gagnable
from lib.controle import Transformer
from lib.joueur import Joueur

# Alias de types
Coordonnees = Tuple[int, int]
Grille = Dict[Coordonnees, Obstacle]
Regle = Callable[['Etat'], None]


class ExceptionLabyrinthe(BaseException, metaclass=ABCMeta):
    """
    Classe d'exceptions liées aux règles du labyrinthe.
    """

    pass


class HorsRegles(ExceptionLabyrinthe):
    """
    Exception levée si le joueur enfreint une règle du labyrinthe.
    """

    pass


class PartieGagnee(ExceptionLabyrinthe):
    """
    Exception levée si le joueur gagne la partie.
    """

    pass


class Etat:
    """
    Représente l'état du labyrinthe à un instant.
    Basé sur la grille d'éléments, le joueur en cours et les adversaires, et incluant le prochain mouvement à vérifier
    (la direction et la transformation).

    L'objet instancié est transmis aux fonctions de règles pour valider le mouvement.

    :param direction: vecteur déplacement.
    :param transformation: classe dérivée de ``Transformation``.
    :param grille: grille d'éléments du labyrinthe.
    :param joueur: joueur en cours.
    :param adversaires: liste d'adversaires.
    """

    def __init__(self, direction: Coordonnees, transformation: Optional[Transformer], grille: Grille, joueur: Joueur,
                 adversaires: List[Joueur]) -> None:
        """
        Construit les variables nécessaires aux règles à partir de l'état du labyrinthe (``grille``, ``joueur`` et
        ``adversaires``) et du mouvement du joueur (``direction``, ``transformation``).

        :param direction: vecteur déplacement.
        :param transformation: classe dérivée de ``Transformation``.
        :param grille: grille d'éléments du labyrinthe.
        :param joueur: joueur en cours.
        :param adversaires: liste d'adversaires.
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
    Définit le set de règles à utiliser selon si le controle est un ``Mouvement`` ou une ``Transformation``.
    Appelle les règles en leur passant l'état du labyrinthe.

    :param etat: état du labyrinthe.
    """

    if etat.transformation:
        regles = regles_transformation
    else:
        regles = regles_mouvement
    for regle in regles:
        regle(etat)


def lister_regles(set_de_regles: Set[Regle]) -> Callable[[Regle], Regle]:
    """
    Construit un décorateur qui stocke une règle dans ``set_de_regles``

    :param set_de_regles: le set de règle à utiliser.
    :return: décorateur.
    """

    def decorateur(regle: Regle) -> Regle:
        """
        Décorateur qui stocke une règles dans un set de regles.

        :param regle: règle à stocker.
        :return: règle sotckée.
        """

        set_de_regles.add(regle)
        return regle
    return decorateur


@lister_regles(regles_mouvement)
def traverser_un_obstacle(etat: Etat) -> None:
    """
    Test si l'élément sur lequel le joueur se déplace est traversable.

    :param etat: état du labyrinthe.
    :raises HorsRegles: si l'élément n'est pas ``Traversable``.
    """

    if not issubclass(etat.obstacle, Traversable):
        raise HorsRegles("Vous ne pouvez pas traverser " + etat.obstacle.description + " !")


@lister_regles(regles_mouvement)
@lister_regles(regles_transformation)
def rencontrer_un_adversaire(etat: Etat) -> None:
    """
    Test si un autre joueur occupe la position sur laquelle le joueur se déplace.
    Test si un autre joueur se trouve sur l'élément à transformer.

    :param etat: état du labyrinthe.
    :raises HorsRegles: si un autre joueur occupe la position.
    """

    for coordonnees in etat.coordonnees_adversaires:
        if etat.coordonnees_obstacle == coordonnees:
            raise HorsRegles("Un joueur occupe déjà " + etat.obstacle.description + " !")


@lister_regles(regles_mouvement)
def gagner_une_partie(etat: Etat) -> None:
    """
    Test si l'élément sur lequel le joueur se déplace est ``Gagnable``.

    :param etat: état du labyrinthe.
    :raises PartieGagnee: si l'élément est ``Gagnable``.
    """

    if issubclass(etat.obstacle, Gagnable):
        raise PartieGagnee()


@lister_regles(regles_transformation)
def transformer_un_obstacle(etat: Etat) -> None:
    """
    Test si l'élément à transformer dérive de la transformation.

    :param etat: état du labyrinthe.
    :raises HorsRegles: si l'élément ne dérive pas de la transformation.
    """

    if etat.transformation:
        if not issubclass(etat.obstacle, etat.transformation):
            raise HorsRegles("Vous ne pouvez pas " + etat.transformation.description
                             + " " + etat.obstacle.description + " !")
