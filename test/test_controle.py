# -*-coding:Utf-8 -*

"""
Ce module contient les classes ControleTest, ExtraireTest et ObtenirControleTest
"""

from typing import List, Tuple, Dict, Any
from controle import Controle, Mouvement, Transformation, extraire, obtenir_controle, Touche
from element import Transformable
import unittest


class ControleTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions des classes Controle, Mouvement et Transformation.
    """

    def setUp(self) -> None:
        """
        Sauvegarde les controles initialisés par le module 'controle'
        Efface les variables de classe pour supprimer les mouvements et transformations pré-existantes
        Définit le nom, la classe d'héritage et les méthodes de 'SimpleControle' nécessaire aux tests
        """

        # Sauve la liste des mouvements et transformations pré-existants (nécessaire pour ObtenirControleTest)
        self.controle_touches = Controle.touches.copy()
        self.controle_descriptions = Controle.descriptions.copy()
        self.controle_touche_controle = Controle.touche_controle.copy()
        self.mouvement_touches = Mouvement.touches.copy()
        self.mouvement_directions = Mouvement.directions.copy()
        self.transformation_touches = Transformation.touches.copy()
        Controle.effacer()
        Mouvement.effacer()
        Transformation.effacer()

        nom: str = 'SimpleControle'
        base: Tuple[type, ...] = (Controle,)

        def __init__(classe, touche: Touche, description: str = "", aide: str = "") -> None:
            """
            Transmet l'objet à la classe mère Controle pour stocker ses informations

            :param Touche touche: caractère du contrôle
            :param str description: courte description du contrôle
            :param str aide: détail sur l'usage du contrôle
            """

            Controle.__init__(classe, touche, description, aide)

        def action() -> None: ...
        def regex() -> str: ...

        dictionnaire: Dict[str, Any] = {'__init__': __init__,
                                        'action': action,
                                        'regex': classmethod(regex)}
        self.SimpleControle = type(nom, base, dictionnaire)

    def tearDown(self) -> None:
        """
        Restaure les listes initiales dans les classes 'Controle', 'Mouvement' et 'Transformation'
        """

        Controle.touches = self.controle_touches.copy()
        Controle.descriptions = self.controle_descriptions.copy()
        Controle.touche_controle = self.controle_touche_controle.copy()
        Mouvement.touches = self.mouvement_touches.copy()
        Mouvement.directions = self.mouvement_directions.copy()
        Transformation.touches = self.transformation_touches.copy()

    def test_lister_les_controles(self) -> None:
        """
        Instancie un nombre de controles et les stocke dans 'liste_controles'
        Pour chacun de ces controles,
        - teste si les attributs 'touche' et 'desciption' sont collectés par Controle
        - teste si le dictionnaire 'touche_controle' associe la 'touche' au controle
        """

        nombre_de_controles: int = 10
        liste_controles: List[Controle] = []
        for indice in range(nombre_de_controles):
            parametre = str(indice)
            liste_controles.append(self.SimpleControle(parametre, parametre, parametre))

        for ctrl in liste_controles:
            self.assertIn(ctrl.touche, Controle.touches)
            self.assertIn(ctrl.description, Controle.descriptions)
            self.assertIs(Controle.touche_controle[ctrl.touche], ctrl)

    def test_lister_les_mouvements(self) -> None:
        """
        Instancie un nombre de mouvements et les stocke dans 'liste_mouvements'
        Pour chacun de ces mouvements,
        - teste si les attributs 'touche' et 'direction' sont collectés par Mouvement
        - teste si l'attribut 'description' est collecté par Controle
        - teste si le dictionnaire 'touche_controle' associe la 'touche' au mouvement
        """

        nombre_de_mouvements: int = 10
        liste_mouvements: List[Mouvement] = []
        for indice in range(nombre_de_mouvements):
            parametre = str(indice)
            liste_mouvements.append(Mouvement(parametre, (indice, indice), parametre, parametre))

        for mouvement in liste_mouvements:
            self.assertIn(mouvement.touche, Mouvement.touches)
            self.assertIn(mouvement.direction, Mouvement.directions)
            self.assertIn(mouvement.description, Controle.descriptions)
            self.assertIs(Controle.touche_controle[mouvement.touche], mouvement)

    def test_lister_les_transformations(self) -> None:
        """
        Instancie un nombre de transformations et les stocke dans 'liste_transformations'
        Pour chacune de ces transformations,
        - teste si l'attribut 'touche' est collecté par Transformation
        - teste si l'attribut 'description' est collecté par Controle
        - teste si le dictionnaire 'touche_controle' associe la 'touche' à la transformation
        """

        nombre_de_transformations: int = 10
        liste_transformations: List[Transformation] = []
        for indice in range(nombre_de_transformations):
            parametre = str(indice)
            liste_transformations.append(Transformation(parametre, Transformable, parametre, parametre))

        for transformation in liste_transformations:
            self.assertIn(transformation.touche, Transformation.touches)
            self.assertIn(transformation.description, Controle.descriptions)
            self.assertIs(Controle.touche_controle[transformation.touche], transformation)


class ExtraireTest(unittest.TestCase):
    """
    Test case utilisé pour tester la fonction extraire().
    """

    def test_extraire_mouvement(self) -> None:
        """
        Construit la chaine de caractères 'saisie' sur le modèle NSEO
        Appelle la fonction 'extraire()' avec 'saisie' en argument
        Compare la 'liste_commandes_ajoutees' depuis saisie avec la 'liste_commande_obtenue'
        """

        saisie: str = ''.join(Mouvement.touches)
        liste_commandes_ajoutees: List[str] = Mouvement.touches
        liste_commandes_obtenues: List[str] = extraire(saisie)
        self.assertEqual(liste_commandes_ajoutees, liste_commandes_obtenues)

    def test_extraire_mouvement_repetition(self) -> None:
        """
        Construit la chaine de caractères 'saisie' sur le modèle N0S1E2O3...
        Ajoute les commandes liées à 'saisie' à la 'liste_commandes_ajoutees'
        Appelle la fonction 'extraire()' avec 'saisie' en argument
        Compare la 'liste_commandes_ajoutees' depuis saisie avec la 'liste_commande_obtenue'
        """

        saisie: str = str()
        repetition: int = 40
        liste_commandes_ajoutees: List[str] = []
        for indice in range(repetition):
            for touche in Mouvement.touches:
                saisie += touche + str(indice)
                for _ in range(indice):
                    liste_commandes_ajoutees.append(touche)
        liste_commandes_obtenues: List[str] = extraire(saisie)
        self.assertEqual(liste_commandes_ajoutees, liste_commandes_obtenues)

    def test_extraire_transformation(self) -> None:
        """
        Construit la chaine de caractères 'saisie' sur le modèle MNMSMEMO...
        Ajoute les commandes liées à 'saisie' à la 'liste_commandes_ajoutees'
        Appelle la fonction 'extraire()' avec 'saisie' en argument
        Compare la 'liste_commandes_ajoutees' depuis saisie avec la 'liste_commande_obtenue'
        """

        saisie: str = str()
        liste_commandes_ajoutees: List[str] = []
        for transformation in Transformation.touches:
            for direction in Mouvement.touches:
                saisie += transformation + direction
                liste_commandes_ajoutees.append(transformation + direction)
        liste_commandes_obtenues: List[str] = extraire(saisie)
        self.assertEqual(liste_commandes_ajoutees, liste_commandes_obtenues)


class ObtenirControleTest(unittest.TestCase):
    """
    Test case utilisé pour tester la fonction obtenir_controle().
    """

    def test_obtenir_controle_mouvement(self):
        """
        Instancie un mouvement dont la 'touche' est collectée par la classe Mouvement
        Appelle la fonction 'obtenir_controle()' avec la 'touche' du mouvement en argument
        Teste si la fonction renvoie la 'direction'
        """

        mouvement_touche = 'A'
        direction_ajoutee = (1, 1)
        Mouvement(mouvement_touche, direction_ajoutee)
        direction_obtenue, _ = obtenir_controle(mouvement_touche)
        self.assertEqual(direction_ajoutee, direction_obtenue)

    def test_obtenir_controle_transformation(self):
        """
        Instancie une transformation dont la 'touche' est collectée par la classe Transformation
        Instancie un mouvement dont la 'touche' est collectée par la classe Mouvement
        Appelle la fonction 'obtenir_controle()' avec les touches 'transformation + mouvement' en argument
        Teste si la fonction renvoie la 'direction' et la 'transformation'
        """

        transformation_touche = 'T'
        transformation_ajoutee = Transformable
        mouvement_touche = 'A'
        direction_ajoutee = (1, 1)
        Transformation(transformation_touche, Transformable)
        Mouvement(mouvement_touche, direction_ajoutee)
        direction_obtenue, transformation_obtenue = obtenir_controle(transformation_touche + mouvement_touche)
        self.assertEqual(direction_ajoutee, direction_obtenue)
        self.assertEqual(transformation_ajoutee, transformation_obtenue)
