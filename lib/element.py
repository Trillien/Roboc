# -*-coding:Utf-8 -*

"""
Ce module définit les éléments de la grille du labyrinthe.

- les classes *Mix-In* ``Decryptable``, ``Decrypte``, ``Defaut``, ``Traversable``, ``Gagnable``, ``Demarrable``,
  ``Transformable``, ``Murable``, ``Percable``
- la metaclasse ``Elements``
- les classes ``Element``, ``Porte``, ``Mur``, ``Sortie``, ``Sol``, ``Robot``, ``Adversaire``
"""

from typing import Dict, Type, Tuple, Any, final, cast
from abc import ABCMeta

# Alias de types
SymboleCarte = str
SymboleAffichage = str
Transformee = Type['Element']
Obstacle = Type['Decrypte']


class Decryptable(metaclass=ABCMeta):
    """
    Désigne tous les éléments du labyrinthe reconnus à la lecture d'une carte.
    """

    symbole_carte: SymboleCarte


class Decrypte(Decryptable, metaclass=ABCMeta):
    """
    Désigne tous les éléments qui sont détaillés dans la grille du labyrinthe.
    Un élément reconnu n'est pas nécessairement renseigné dans la grille.
    """

    pass


class Defaut(metaclass=ABCMeta):
    """
    Désigne l'élément qui sera appelé si la grille du labyrinthe n'en définit aucun.
    Il ne doit y avoir qu'un seul élément défini par défaut.
    """

    pass


class Traversable(metaclass=ABCMeta):
    """
    Désigne un élément qui peut être traversé par le joueur.
    """

    pass


class Gagnable(Traversable, Decryptable):
    """
    Désigne un élément qui fait gagner la partie au joueur.
    """

    pass


class Demarrable(Traversable):
    """
    Désigne un élément sur lequel le joueur peut démarrer la partie.
    """

    pass


class Transformable(metaclass=ABCMeta):
    """
    Désigne un élément qui peut être changé en un autre.
    """

    transformee: Transformee
    description: str


class Murable(Transformable, metaclass=ABCMeta):
    """
    Désigne un élément qui peut être remplacé par un ``Mur``.
    """

    description = "murer"


class Percable(Transformable, metaclass=ABCMeta):
    """
    Désigne un élément qui peut être remplacé par une ``Porte``.
    """

    description = "percer"


class Elements(ABCMeta):
    """
    Métaclasse qui stocke les informations des classes créées dans:

    - ``decryptable``, caractères reconnus à la lecture d'une carte et associés aux classes d'éléments.
    - ``gagnable``, caractères et leurs éléments associés qui font gagner la partie.
    - ``obstacle_par_defaut``, élément appelé si la grille du labyrinthe n'en définit aucun.
    """

    decryptable: Dict[SymboleCarte, Type['Element']] = {}
    gagnable: Dict[SymboleCarte, Type['Element']] = {}
    obstacle_par_defaut: Type['Element']
    symbole_affichage: SymboleAffichage

    def __new__(mcs, nom: str, bases: Tuple[Any, ...], dictionnaire: Dict[str, Any]):
        """
        Crée la classe d'élément et ajoute ses informations aux variables de classe en fonction des classes héritées.

        :param nom: nom de la classe d'élément.
        :param bases: classes héritées.
        :param dictionnaire: méthodes de la classe d'élément.
        :return: classe d'élément créée.
        """

        classe = cast(Type['Element'], super().__new__(mcs, nom, bases, dictionnaire))
        for base in bases:
            if issubclass(base, Decryptable):
                mcs.decryptable[dictionnaire["symbole_carte"]] = classe
            if issubclass(base, Gagnable):
                mcs.gagnable[dictionnaire["symbole_carte"]] = classe
            if issubclass(base, Defaut):
                mcs.obstacle_par_defaut = classe
        return classe

    def __str__(self) -> SymboleAffichage:
        """
        Renvoie une représentation (un caractère) de l'élément du labyrinthe.
        Surchage de ``__str__()`` qui est appelé pour afficher une classe élément.

        :return: symbole_affichage
        """

        return self.symbole_affichage

    @classmethod
    def get_decryptable(mcs, symbole: SymboleCarte) -> Type['Element']:
        """
        Renvoie l'élément correspondant au caractère transmis.
        Si ``decryptable`` ne contient pas l'élément, renvoie ``obstacle_par_defaut``.

        :param symbole: caractère.
        :return: Elément.
        """

        try:
            element = mcs.decryptable[symbole]
        except KeyError:
            element = mcs.obstacle_par_defaut
        return element

    @classmethod
    def enlever(mcs, symbole: str) -> None:
        """
        Efface l'élément représenté par 'symbole' des dictionnaires de la classe 'Elements'
        """

        try:
            mcs.decryptable.pop(symbole)
        except KeyError:
            pass
        try:
            mcs.gagnable.pop(symbole)
        except KeyError:
            pass


class Element(metaclass=Elements):
    """
    Classe générique des éléments présents dans un labyrinthe.
    """

    symbole_affichage: SymboleAffichage = str()
    description: str


@final
class Porte(Element, Decrypte, Traversable, Murable):
    """
    Une ``Porte`` est un élément présent dans la grille du labyrinthe, traversable par le joueur, transformable en ``Mur``.
    """

    symbole_affichage = "."
    symbole_carte = "."
    description = "la porte"


@final
class Mur(Element, Decrypte, Percable):
    """
    Un ``Mur`` est un élément présent dans la grille du labyrinthe, transformable en ``Porte``.
    """

    symbole_affichage = "O"
    symbole_carte = "O"
    description = "le mur"


@final
class Sortie(Element, Decrypte, Gagnable):
    """
    Une ``Sortie`` est un élément présent dans la grille du labyrinthe, qui permet de gagner une partie.
    """

    symbole_affichage = "U"
    symbole_carte = "U"
    description = "la sortie"


@final
class Sol(Element, Decryptable, Defaut, Demarrable):
    """
    Le ``Sol`` est l'élément par défaut absent de la grille du labyrinthe, sur lequel le joueur peut débuter une partie.
    """

    symbole_affichage = " "
    symbole_carte = " "
    description = "le terrain"


@final
class Robot(Element):
    """
    Représente le joueur.
    """

    symbole_affichage = "X"


@final
class Adversaire(Element):
    """
    Représente les autres joueurs.
    """

    symbole_affichage = "x"


# Pour éviter les références circulaires, le membre ``transformee`` de ``Transformation`` est défini après les classes
# d'éléments.
Murable.transformee = Mur
Percable.transformee = Porte
