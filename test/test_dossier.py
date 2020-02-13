# -*-coding:Utf-8 -*

"""
Ce module contient la classe ``DossierTest``.

Les tests unitaires de la classe ``Dossier`` utilisent les fichiers du dossier *test dossier*.
"""

from typing import Final, List, Set
from lib.dossier import Dossier
import os
import unittest

dossier_courant: Final[str] = os.path.dirname(__file__)
dossier_de_test: Final[str] = os.path.join(dossier_courant, "test dossier")
dossier_vide: Final[str] = os.path.join(dossier_courant, "test dossier/dossier vide")
fichier_introuvable: Final[str] = "-"
fichier_vide: Final[str] = os.path.join(dossier_courant, "test dossier/vide.txt")
extension_introuvable: Final[str] = "."


class EstTrue:
    """
    Classe transmise à la classe ``Dossier`` pour créer une instance ``dossier``.
    '*if EstTrue*' renvoie True.
    """

    def __init__(self, *args, **kwargs) -> None:
        pass

    def __bool__(self) -> bool:
        """
        :return: True
        """

        return True


class EstFalse:
    """
    Classe transmise à la classe ``Dossier`` pour créer une instance ``dossier``.
    '*if EstFalse*' renvoie False.
    """

    def __init__(self, *args, **kwargs) -> None:
        pass

    def __bool__(self) -> bool:
        """
        :return: False
        """

        return False


class DossierTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions du module **dossier**.
    """

    def setUp(self) -> None:
        """
        Avant chaque test, charge le jeu de fichiers du dossier *test dossier*.
        Charge les extensions des fichiers du dossier *test dossier*.
        """

        self.liste_fichiers = self.__parcourir_dossier(dossier_de_test)
        self.extensions = self.__parcourir_extensions()

    def __parcourir_dossier(self, dossier: str) -> List[str]:
        """
        Liste les fichiers et sous-dossiers d'un dossier de manière récursive.

        :param dossier: dossier de recherche des cartes.
        :return: liste des fichiers.
        """

        liste_fichiers = []
        for fichier in os.listdir(dossier):
            chemin = os.path.join(dossier, fichier)
            if os.path.isdir(chemin):
                liste_fichiers.extend(self.__parcourir_dossier(chemin))
            elif os.path.isfile(chemin) and os.path.getsize(chemin):
                liste_fichiers.append(chemin)
        return liste_fichiers

    def __parcourir_extensions(self) -> Set[str]:
        """
        Extrait les extensions de ``liste_fichiers``.

        :return: liste des extensions des fichiers.
        """

        extensions = set()
        for chemin in self.liste_fichiers:
            _, extension = os.path.splitext(chemin)
            extensions.add(extension)
        return extensions

    def test_lister_les_fichiers_par_dossier(self) -> None:
        """
        En passant un chemin de dossier en paramètre, teste si l'instance de la classe ``Dossier`` liste tous les fichiers
        d'un dossier, et si elle renvoie le nombre juste de fichiers.
        """

        for extension in self.extensions:
            fichiers = []
            for chemin in self.liste_fichiers:
                if chemin.endswith(extension):
                    fichiers.append(chemin)
            fichiers.sort()
            dossier = Dossier(chemin=dossier_de_test, extension=extension)
            fichiers_test = dossier.chemins
            fichiers_test.sort()
            self.assertEqual(fichiers, fichiers_test)
            self.assertEqual(len(fichiers), len(dossier))

    def test_lister_les_fichiers_par_fichier(self) -> None:
        """
        En passant un chemin de fichier en paramètre, teste si l'instance de la classe ``Dossier`` liste le fichier indiqué.
        """

        for fichier in self.liste_fichiers:
            _, extension = os.path.splitext(fichier)
            fichier_test = Dossier(chemin=fichier, extension=extension).chemins
            self.assertEqual(fichier, *fichier_test)

    def test_fichier_introuvable(self) -> None:
        """
        A l'instanciation de la classe ``Dossier``, une exception ``FileNotFoundError`` est levée si un fichier est inexistant.
        """

        with self.assertRaises(FileNotFoundError):
            Dossier(chemin=fichier_introuvable)

    def test_extension_introuvable(self) -> None:
        """
        A l'instanciation de la classe ``Dossier``, une exception ``FileNotFoundError`` est levée si aucun fichier ne comporte
        l'extension passée en paramètre.
        """

        with self.assertRaises(FileNotFoundError):
            Dossier(chemin=dossier_de_test, extension=extension_introuvable)

    def test_fichier_vide(self) -> None:
        """
        A l'instanciation de la classe ``Dossier``, une exception ``EOFError`` est levée si le fichier indiqué est vide.
        """

        with self.assertRaises(EOFError):
            Dossier(chemin=fichier_vide)

    def test_dossier_vide(self) -> None:
        """
        A l'instanciation de la classe ``Dossier``, une exception ``FileNotFoundError`` est levée si le dossier indiqué est
        vide.
        """

        with self.assertRaises(FileNotFoundError):
            Dossier(chemin=dossier_vide)

    def test_lire_les_fichiers(self) -> None:
        """
        La classe ``EstTrue`` passée en paramètre est instanciée pour chaque fichier du ``dossier_de_test``.
        La classe ``EstFalse`` passée en paramètre est instanciée pour chaque fichier du ``dossier_de_test``. Une exception
        ``FileNotFoundError`` est levée car aucun fichier ne passe le test '*if EstFalse*'.
        """

        for extension in self.extensions:
            dossier = Dossier(chemin=dossier_de_test, extension=extension, classe=EstTrue)
            for contenu in dossier.contenus:
                self.assertIsInstance(contenu, EstTrue)
            with self.assertRaises(FileNotFoundError):
                Dossier(chemin=dossier_de_test, extension=extension, classe=EstFalse)
