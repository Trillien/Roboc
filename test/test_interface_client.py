# -*-coding:Utf-8 -*

"""
Ce module contient la classe ``ValidateurTexteTest``.
"""

from interface_client import ValidateurTexte, ValidationErreur, Quitter
import unittest


class ValidationTexteTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions de la classe ``ValidateurTexte``.
    """

    def tearDown(self) -> None:
        """
        Après chaque test, réinitialise la classe ``ValidateurTexte``.
        """

        ValidateurTexte.effacer()

    def test_bons_parametres(self) -> None:
        """
        Transmet les paramètres ``"validation_schema"`` et ``"validation_erreur"`` à la classe ``ValidateurTexte``.
        Instancie la classe avec ``message`` qui contient une chaîne de caractères valide.
        """

        message = 'test'
        liste_categorie = {
            'validation_schema': message,
            'validation_erreur': 'test_erreur'
        }
        for cle, valeur in liste_categorie.items():
            ValidateurTexte.parametrer(cle, valeur)
        self.assertTrue(ValidateurTexte(message))

    def test_pas_de_parametre(self) -> None:
        """
        Sans paramétrage préalable, instancie la classe avec ``message`` qui contient une chaîne de caractères.
        L'instance de ``ValidateurTexte`` lève l'exception ``ValidationErreur``.
        """

        message = 'test'
        with self.assertRaises(ValidationErreur):
            ValidateurTexte(message)

    def test_mauvais_message(self) -> None:
        """
        Transmet les paramètres ``"validation_schema"`` et ``"validation_erreur"`` à la classe ``ValidateurTexte``.
        Instancie la classe avec ``message`` dont la chaîne de caractères n'est pas valide.
        """

        message = 'tes*'
        liste_categorie = {
            'validation_schema': r'test',
            'validation_erreur': 'test_erreur'
        }
        for cle, valeur in liste_categorie.items():
            ValidateurTexte.parametrer(cle, valeur)
        self.assertFalse(ValidateurTexte(message))

    def test_quitter(self) -> None:
        """
        Instancie la classe ``ValidateurTexte`` avec ``Quitter.touche``. L'instance lève l'exception ``Quitter``.
        """

        message = Quitter.touche
        with self.assertRaises(Quitter):
            ValidateurTexte(message)
