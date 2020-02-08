# -*-coding:Utf-8 -*

"""
Ce module contient la classe CarteTest

Les tests unitaires de la classe Carte utilisent deux jeux de fichiers:
- un jeu de fichiers valides contenant les éléments obligatoires et connus
- un jeu de fichiers invalides avec des éléments absents ou inconnus
"""

from typing import List, Final
from carte import Carte
import os
import unittest

dossier_courant: Final[str] = os.path.dirname(__file__)
dossier_cartes_valides: Final[str] = os.path.join(dossier_courant, "test dossier/cartes valides")
dossier_cartes_invalides: Final[str] = os.path.join(dossier_courant, "test dossier/cartes invalides")
fichier_introuvable: Final[str] = ""


class CarteTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions du module 'carte'.
    """

    def setUp(self) -> None:
        """
        Charge les jeux de cartes valides et invalides
        Définit les éléments connus et obligatoires (ces éléments sont repris du module labyrinthe)
        """

        self.liste_cartes_valides = self.parcourir_dossier(dossier_cartes_valides)
        self.liste_cartes_invalides = self.parcourir_dossier(dossier_cartes_invalides)
        Carte.elements_connus = {" ", "O", ".", "U"}
        Carte.elements_obligatoires = {"U"}
            
    def parcourir_dossier(self, dossier: str) -> List[str]:
        """
        Liste les fichiers et les sous-dossiers (fonction récursive) d'un dossier

        :param str dossier: dossier de recherche des cartes
        :return: liste des fichiers
        :rtype: List[str]
        """

        liste_fichiers = []
        for fichier in os.listdir(dossier):
            chemin = os.path.join(dossier, fichier)
            if os.path.isdir(chemin):
                liste_fichiers.extend(self.parcourir_dossier(chemin))
            elif os.path.isfile(chemin):
                liste_fichiers.append(chemin)
        return liste_fichiers
    
    def test_cartes_valides(self) -> None:
        """
        Carte doit renvoyer True pour chaque fichier du jeu valide
        Carte.contenu doit être le contenu du fichier
        """

        for chemin in self.liste_cartes_valides:
            with open(chemin, "r") as fichier:
                contenu = fichier.read()
            carte = Carte(chemin=chemin)
            self.assertTrue(carte)
            self.assertEqual(contenu, carte.contenu)
            
    def test_cartes_invalides(self) -> None:
        """
        Carte doit renvoyer False pour chaque fichier du jeu invalide
        Carte.contenu doit être le contenu du fichier
        """

        for chemin in self.liste_cartes_invalides:
            with open(chemin, "r") as fichier:
                contenu = fichier.read()
            carte = Carte(chemin=chemin)
            self.assertFalse(carte)
            self.assertEqual(contenu, carte.contenu)

    def test_fichier_introuvable(self) -> None:
        """
        Carte doit renvoyer l'exception FileNotFoundError pour un fichier inexistant
        """

        with self.assertRaises(FileNotFoundError):
            Carte(chemin=fichier_introuvable)
