# -*-coding:Utf-8 -*

"""
Ce module contient la classe ``JoueurTest``.
"""

from typing import List
from lib.joueur import Joueur, Commande
import unittest


class JoueurTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions de la classe ``Joueur``.
    """

    def setUp(self) -> None:
        """
        Avant chaque test, instancie un objet de la classe ``Joueur`` et crée une liste d'objets variés.
        """

        self.joueur = Joueur('identifiant_client', 'Joueur')
        self.liste_objets = [
            None,           # None
            'test',         # Chaine de caractères
            1,              # entier
            True,           # booléen
            {'test': 1},    # dictionnaire
            ['test'],       # liste
            ('test', 1),    # tuple
        ]

    def test_ajouter_retirer_commande(self) -> None:
        """
        - Ajoute chaque objet à la liste de commandes de ``joueur`` en appelant ``ajouter_commande()``.
        - Teste si la liste de commandes de ``joueur`` est identique à la liste d'objets.
        - Extrait les commandes une à une de joueur en appelant ``retirer_commande()``.
        - Teste si ``liste_commandes_obtenues`` est identique à la liste d'objets.
        """

        liste_commandes_obtenues: List[Commande] = []

        for objet in self.liste_objets:
            self.joueur.ajouter_commande([objet])
        self.assertEqual(self.liste_objets, self.joueur.commandes)

        for _ in range(len(self.liste_objets)):
            liste_commandes_obtenues.append(self.joueur.retirer_commande())
        self.assertEqual(self.liste_objets, liste_commandes_obtenues)
