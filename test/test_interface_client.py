# -*-coding:Utf-8 -*

"""
Ce module contient la classe ValidateurTexteTest
"""

from interface_client import ValidateurTexte, ValidationErreur, Quitter
import unittest


class ValidationTexteTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions de la classe 'ValidateurTexte'.
    """

    def tearDown(self) -> None:
        """
        Réinitialise la classe ValidateurTexte après chaque test
        """

        ValidateurTexte.effacer()

    def test_bons_parametres(self) -> None:
        """
        Paramètre la classe ValidateurTexte
        Instancie la classe avec 'message' avec un texte qui correspond au schéma
        """

        message = 'test'
        liste_categorie = {
            'validation_schema': message,
            'validation_erreur': 'test_erreur'
        }
        for cle, valeur in liste_categorie.items():
            ValidateurTexte.parametrer(cle, valeur)
        self.assertTrue(ValidateurTexte(message))

    def test_pas_de_parametres(self) -> None:
        """
        Sans paramétrage préalable,
        Instancie la classe avec 'message'
        """

        message = 'test'
        with self.assertRaises(ValidationErreur):
            ValidateurTexte(message)

    def test_mauvais_message(self) -> None:
        """
        Paramètre la classe ValidateurTexte
        Instancie la classe avec 'message' avec un texte qui ne correspond pas au schéma
        """

        message = 'tes*'
        liste_categorie = {
            'validation_schema': r'test',
            'validation_erreur': 'test_erreur'
        }
        for cle, valeur in liste_categorie.items():
            ValidateurTexte.parametrer(cle, valeur)
        with self.assertRaises(ValidationErreur):
            self.assertFalse(ValidateurTexte(message))

    def test_quitter(self) -> None:
        """
        Instancie la classe avec 'Quitter.touche'
        """

        message = Quitter.touche
        with self.assertRaises(Quitter):
            ValidateurTexte(message)
