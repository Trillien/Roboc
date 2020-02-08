# -*-coding:Utf-8 -*

"""
Ce module contient les classes Controle, Mouvement, Transformation
et les fonctions decompresser(), obtenir_controle()

"""

from typing import ClassVar, Dict, Type, Set, Tuple, List, Any, Final, Pattern, final, Optional
from abc import ABCMeta, abstractmethod
import re
from element import Transformable, Murable, Percable

# Alias de types
Touche = str
Coordonnees = Tuple[int, int]
Transformer = Type[Transformable]
Regex = str


class Controle(metaclass=ABCMeta):
    """
    Classe abstraite qui se dérive en Mouvement et Transformation
    Elle énumère les méthodes action() et regex() nécessaires à un Controle

    Pour chaque controle instancié, elle stocke ses informations dans:
     - 'touches', caractères reconnus pour jouer au labyrinthe
     - 'descriptions', courtes explications des Mouvements et Transformations
     - 'touche_controle', dictionnaire associant un Controle à un caractère
    """

    touches: ClassVar[List[Touche]] = []
    descriptions: ClassVar[List[str]] = []
    touche_controle: ClassVar[Dict[Touche, 'Controle']] = {}

    def __init__(self, touche: Touche, description: str = "", aide: str = "") -> None:
        """
        Initialise les variables d'objet d'un contrôle et ajoute les informations aux variables de classe

        :param Touche touche: caractère du contrôle
        :param str description: courte description du contrôle
        :param str aide: détail sur l'usage du contrôle
        """
        self.touche = touche
        self.description = touche + " - " + description + " - " + aide
        self.aide = aide
        self.touches.append(touche)
        self.descriptions.append(self.description)
        self.touche_controle[touche] = self

    @abstractmethod
    def action(self) -> Any: ...

    @classmethod
    @abstractmethod
    def regex(cls) -> Regex: ...

    @classmethod
    def effacer(cls) -> None:
        """
        Réinitialise les variables de la classe
        """

        cls.touches = []
        cls.descriptions = []
        cls.touche_controle = {}


class Mouvement(Controle):
    """
    Classe dérivée de Controle qui représente un Mouvement
    Indépendamment de Controle, elle stocke les information de ses objets instanciés dans:
     - 'touches', caractères reconnus pour jouer au labyrinthe
     - 'directions', vecteur déplacement associé au mouvement
    """

    touches: ClassVar[List[Touche]] = []
    directions: ClassVar[Set[Coordonnees]] = set()

    def __init__(self, touche: Touche, direction: Coordonnees, description: str = "", aide: str = "") -> None:
        """
        Créer un objet Mouvement, initialise le vecteur direction et le stocke dans une variable de classe.
        Transmet l'objet à la classe mère Controle pour stocker ses informations

        :param Touche touche: caractère du contrôle
        :param Coordonnees direction: vecteur déplacement
        :param str description: courte description du mouvement
        :param str aide: détail sur l'usage du contrôle
        """

        self.direction = direction
        self.directions.add(direction)
        super().__init__(touche, description, aide)

    def action(self) -> Coordonnees:
        """
        Retourne le vecteur déplacement du mouvement

        :return: vecteur déplacement
        :rtype: Coordonnees
        """

        return self.direction

    @classmethod
    @final
    def regex(cls) -> Regex:
        """
        Retourne un schéma de validation depuis les mouvements instanciés

        :return: expression régulière
        :rtype: Regex
        """

        return "([" + ''.join(cls.touches) + "])([0-9]*)"

    @classmethod
    def effacer(cls) -> None:
        """
        Réinitialise les variables de la classe
        """

        cls.touches = []
        cls.directions = set()


class Transformation(Controle):
    """
    Classe dérivée de Controle qui représente la transformation d'un obstacle
    Indépendamment de Controle, elle stocke les information de ses objets instanciés dans:
     - 'touches', caractères reconnus pour jouer au labyrinthe
    """

    touches: ClassVar[List[Touche]] = []

    def __init__(self, touche: Touche, transformer: Transformer, description: str = "", aide: str = "") -> None:
        """
        Créer un objet Transformation et initialise la transformation.
        Transmet l'objet à la classe mère Controle pour stocker ses informations

        :param Touche touche: caractère du contrôle
        :param Transformer transformer: transformation
        :param str description: courte description de la transformation
        :param str aide: détail sur l'usage du contrôle
        """

        self.transformer = transformer
        super().__init__(touche, description, aide)

    def action(self) -> Transformer:
        """
        Retourne la transformation

        :return: transformation
        :rtype: Transformer
        """

        return self.transformer

    @classmethod
    @final
    def regex(cls) -> Regex:
        """
        Retourne un schéma de validation depuis les transformations instanciées

        :return: expression régulière
        :rtype: Regex
        """

        return "([" + ''.join(cls.touches) + "])([" + ''.join(Mouvement.touches) + "])"

    @classmethod
    def effacer(cls) -> None:
        """
        Réinitialise les variables de la classe
        """

        cls.touches = []


"""
Instanciation des mouvements Nord, Sud, Est, Ouest et des transformations Percer et Murer
Création des expressions régulières pour:
    - valider la saisie du client réseau
    - extraire les commandes de la saisie du client réseau
"""

Mouvement("N", (0, -1), "Se déplacer vers le Nord", "Usage: N[0-99]")
Mouvement("S", (0, 1), "Se déplacer vers le Sud", "Usage: S[0-99]")
Mouvement("E", (1, 0), "Se déplacer vers l'Est", "Usage: E[0-99]")
Mouvement("O", (-1, 0), "Se déplacer vers l'Ouest", "Usage: O[0-99]")

Transformation("M", Murable, "Murer un obstacle", "Usage: M<" + ''.join(Mouvement.touches) + ">")
Transformation("P", Percable, "Percer un obstacle", "Usage: P<" + ''.join(Mouvement.touches) + ">")

validation_controle: Final[Regex] = r"((" + Mouvement.regex() + ")|(" + Transformation.regex() + "))+"
extraction_controle: Final[Regex] = r"(?:" + Mouvement.regex() + ")|(?:" + Transformation.regex() + ")"
extraction_controle_compile: Final[Pattern] = re.compile(extraction_controle)


def extraire(saisie: str) -> List[str]:
    """
    Extrait les commandes avec l'expression regulière extraction_controle_compile tel que:
        [mouvement repetition]|[transformation direction]
    Si 'mouvement' est suivi d'un nombre (répétition), répète la commande et la stocke
    Retourne la liste des commandes de mouvements et de transformations

    :param str saisie: saisie du client réseau
    :return: commandes
    :rtype: List[str]
    """

    extrait = extraction_controle_compile.findall(saisie)
    commandes: List[str] = []
    for mouvement, repetition, transformation, direction in extrait:
        if mouvement:
            if repetition:
                commandes.extend([mouvement] * int(repetition))
            else:
                commandes.append(mouvement)
        else:
            commandes.append(transformation + direction)
    return commandes


def obtenir_controle(commande: str) -> Tuple[Coordonnees, Optional[Transformer]]:
    """
    Execute action() de l'objet Mouvement ou Transformation lié à la commande
    Si c'est une commande de transformation, elle inclut également une direction

    :param str commande: commande à décoder
    :return: vecteur déplacement ou transformation et sa direction
    :rtype: Tuple[Coordonnees, None] ou Tuple[Coordonnees, Transformer]
    """

    coordonnees = Controle.touche_controle[commande[-1]].action()
    transformer: Optional[Transformer] = None
    if len(commande) == 2:
        transformer = Controle.touche_controle[commande[0]].action()
    return coordonnees, transformer
