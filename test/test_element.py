# -*-coding:Utf-8 -*

"""
Ce module contient la classe ``ElementTest``.
"""

from typing import List, Any, Dict, Tuple
from element import Decryptable, Decrypte, Defaut, Traversable, Gagnable, Demarrable, Transformable, Murable, Percable,\
    Elements, Element
import unittest


class ElementTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions de la classe ``Elements``.
    """

    def setUp(self) -> None:
        """
        Avant chaque test:

        - Sauvegarde les éléments initialisés par le module **element**.
        - Efface les listes d'éléments ``Decryptable`` et ``Gagnable`` de la métaclasse ``Elements``.
        """

        self.decryptable = Elements.decryptable.copy()
        self.gagnable = Elements.gagnable.copy()
        self.obstacle_par_defaut = Elements.obstacle_par_defaut
        Elements.decryptable.clear()
        Elements.gagnable.clear()

    def tearDown(self) -> None:
        """
        Après chaque test, restaure les listes initiales dans la métaclasse ``Elements``.
        """

        Elements.decryptable = self.decryptable.copy()
        Elements.gagnable = self.gagnable.copy()
        Elements.obstacle_par_defaut = self.obstacle_par_defaut

    def test_lister_les_elements(self) -> None:
        """
        Pour chaque classe *Mix-In*, crée une classe dérivée sur le modèle de la métaclasse ``Elements``.

        Pour chaque classe créée:

        - Si elle dérive de ``Decryptable``, teste si le dictionnaire ``decryptable`` associe le ``symbole_carte`` à la classe.
        - si elle dérive de ``Gagnable``, teste si le dictionnaire ``gagnable`` associe le ``symbole_carte`` à la classe.
        - si elle dérive de ``Defaut``, teste si l'attribut ``obstacle_par_defaut`` contient la classe.
        """

        liste_bases: List[type] = [Decryptable,
                                   Decrypte,
                                   Defaut,
                                   Traversable,
                                   Gagnable,
                                   Demarrable,
                                   Transformable,
                                   Murable,
                                   Percable]
        liste_classes: List[type] = []
        for indice, bases in enumerate(liste_bases):
            nom: str = 'classe' + str(indice)
            base: Tuple[type, ...] = (Element, bases, )
            dictionnaire: Dict[str, Any] = {'symbole_carte': str(indice)}
            liste_classes.append(type(nom, base, dictionnaire))

        for classe in liste_classes:
            if issubclass(classe, Decryptable):
                self.assertIs(classe, Elements.decryptable[classe.symbole_carte])
            if issubclass(classe, Gagnable):
                self.assertIs(classe, Elements.gagnable[classe.symbole_carte])
            if issubclass(classe, Defaut):
                self.assertIs(classe, Elements.obstacle_par_defaut)
