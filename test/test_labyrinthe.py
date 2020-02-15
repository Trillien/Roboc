# -*-coding:Utf-8 -*

"""
Ce module contient la classe ``LabyrintheTest``.
"""

from typing import Tuple, Set, List, Dict, cast, ClassVar, Any, Optional, Type
from os import path
from lib.element import Obstacle, Element, Elements, Decryptable, Decrypte, Gagnable, Defaut, Demarrable, Transformable,\
    Traversable
from lib.labyrinthe import Labyrinthe, Coordonnees, Grille
from lib.joueur import Joueur
import unittest


def construire_grille(chaine: str) -> Tuple[Grille, List[Coordonnees], Set[str]]:
    """
    - Crée une grille de labyrinthe à partir d'une chaîne de caractères.
    - Identifie les caractères qui ne peuvent pas être décodés (qui n'hérite pas de ``Decryptage``).
    - Enlève les éléments qui ne sont pas hérités de ``Decrypte``.
    - Identifie les éléments qui hérite de ``Gagnable``.

    :param chaine: chaîne de caractères.
    :return: grille de labyrinthe, liste de coordonnées des éléments gagnable, set des caractères inconnus.
    """

    grille: Grille = {}
    sorties: List[Coordonnees] = []
    caracteres_inconnus: Set[str] = set()
    for ordonnee, ligne in enumerate(chaine.splitlines()):
        for abscisse, caractere in enumerate(ligne):
            if caractere not in Elements.decryptable:
                caracteres_inconnus.add(caractere)
            grille[(abscisse, ordonnee)] = cast(Obstacle, Elements.get_decryptable(caractere))
    for coordonnees, element in grille.copy().items():
        if issubclass(element, Gagnable):
            sorties.append(coordonnees)
        if not issubclass(element, Decrypte):
            grille.pop(coordonnees)
    return grille, sorties, caracteres_inconnus


def determiner_min_max(mini: Coordonnees, maxi: Coordonnees, point: Coordonnees) -> Tuple[Coordonnees, Coordonnees]:
    """
    ``mini`` et ``maxi`` sont deux points extrêmes d'un rectangle.
    Calcule les deux nouveaux extrêmes ``mini`` et ``maxi`` en comparant les coordonnées avec ``point``.

    :param mini: point extrême dont les coordonnées sont les plus petites.
    :param maxi: point extrême dont les coordonnées sont les plus grandes.
    :param point: coordonnées à comparer.
    :return: les coordonnées des nouveaux points extrêmes.
    """

    min_abscisse = min(mini[0], point[0])
    max_abscisse = max(maxi[0], point[0])
    min_ordonnee = min(mini[1], point[1])
    max_ordonnee = max(maxi[1], point[1])
    return (min_abscisse, min_ordonnee), (max_abscisse, max_ordonnee)


class LabyrintheTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions de la classe ``Labyrinthe``.
    """

    def setUp(self) -> None:
        """
        Avant chaque test:

        - Sauvegarde les éléments initialisés par le module **element**.
        - Efface les listes d'éléments ``Decryptable`` et ``Gagnable`` de la métaclasse ``Elements``.
        - Définit les nom, classe d'héritage et attributs des éléments nécessaires aux tests.
        - Crée et stocke les classes dans ``elements``.
        - Crée la classe ``Debutable`` et l'élément ``ElementTransformable``.
        """

        self.decryptable = Elements.decryptable.copy()
        self.gagnable = Elements.gagnable.copy()
        self.obstacle_par_defaut = Elements.obstacle_par_defaut
        Elements.decryptable.clear()
        Elements.gagnable.clear()

        noms: List[str] = ['ElementDecryptable',
                           'ElementDecrypte',
                           'ElementGagnable',
                           'ElementDefaut',
                           'ElementDebut',
                           'ElementFin',
                           'ElementTraversable']
        bases: List[Tuple[type, ...]] = [(Element, Decryptable,),
                                         (Element, Decrypte,),
                                         (Element, Gagnable,),
                                         (Element, Defaut,),
                                         (Element, Decrypte, Demarrable,),
                                         (Element, Decrypte, Gagnable,),
                                         (Element, Decrypte, Traversable,)]
        dictionnaires: List[Dict[str, Any]] = \
            [{'symbole_affichage': 'X', 'symbole_carte': 'X', 'description': 'décryptable'},
             {'symbole_affichage': 'K', 'symbole_carte': 'K', 'description': 'décrypté'},
             {'symbole_affichage': 'G', 'symbole_carte': 'G', 'description': 'gagnable'},
             {'symbole_affichage': 'O', 'symbole_carte': 'O', 'description': 'défaut'},
             {'symbole_affichage': 'D', 'symbole_carte': 'D', 'description': 'début'},
             {'symbole_affichage': 'F', 'symbole_carte': 'F', 'description': 'fin'},
             {'symbole_affichage': 'R', 'symbole_carte': 'R', 'description': 'traversable'}]
        elements = {}
        for indice in range(len(noms)):
            elements[noms[indice]] = type(noms[indice], bases[indice], dictionnaires[indice])

        class Debutable(Transformable):
            """
            Désigne un élément qui peut être transformé en ``ElementDebut``.
            """

            description = "débuter"
            transformee = elements['ElementDebut']

        nom = 'ElementTransformable'
        base = (Element, Decrypte, Debutable,)
        dictionnaire = {'symbole_affichage': 'T', 'symbole_carte': 'T', 'description': 'transformable'}
        elements[nom] = Elements(nom, base, dictionnaire)

    def tearDown(self) -> None:
        """
        Après chaque test, restaure les listes initiales dans la métaclasse ``Elements``.
        """

        Elements.decryptable = self.decryptable.copy()
        Elements.gagnable = self.gagnable.copy()
        Elements.obstacle_par_defaut = self.obstacle_par_defaut

    def test_creer_labyrinthe(self) -> None:
        """
        Pour chaque chaîne de caractères détaillée:

        - Définit la grille, les coordonnées des sorties et les éléments inconnus.
        - Crée un labyrinthe sur cette chaîne de caractères.
        - Compare ``grille``, ``sorties`` et ``caracteres_inconnus`` avec les attributs du labyrinthe.
        """

        chaines: List[str] = ["XX\nXX",  # Grille 2x2 d'éléments décryptables
                              "KK\nKK",  # Grille 2x2 d'éléments décryptés
                              "GG\nGG",  # Grille 2x2 d'éléments gagnable
                              "OO\nOO",  # Grille 2x2 d'éléments défaut
                              "II\nII",  # Grille 2x2 d'éléments inconnus
                              "XK\nGI"]  # Grille 2x2 d'éléments mix
        for chaine in chaines:
            grille, sorties, caracteres_inconnus = construire_grille(chaine)
            labyrinthe = Labyrinthe(chaine)
            self.assertEqual(caracteres_inconnus, labyrinthe.caracteres_inconnus)
            self.assertEqual(sorties, labyrinthe.sorties)
            self.assertEqual(grille, labyrinthe.grille)

    def test_ajouter_effacer_joueur(self) -> None:
        """
        - Crée un labyrinthe contenant un nombre de positions de départ suffisant pour accueillir de nouveaux joueurs.
        - Ajoute les joueurs au labyrinthe.
        - Teste si les joueurs ajoutés sont inclus dans ``liste_joueurs`` et ``dict_client_joueurs`` du labyrinthe.
        - Teste si le labyrinthe crée de nouveaux joueurs bien qu'il n'y ait plus de position de départ disponible.
        - Efface les joueurs du labyrinthe.
        - Teste si les joueurs sont retirés de ``liste_joueurs`` et ``dict_client_joueurs`` du labyrinthe.
        """

        nombre_joueurs: int = 10
        liste_joueurs: Dict[int, Optional[Joueur]] = {}
        labyrinthe = Labyrinthe("D" * nombre_joueurs + "F")
        for identifiant in range(nombre_joueurs):
            liste_joueurs[identifiant] = labyrinthe._ajouter_joueur(identifiant, "Joueur" + str(identifiant))
            self.assertIs(liste_joueurs[identifiant], labyrinthe.dict_client_joueur[identifiant])
            self.assertIn(liste_joueurs[identifiant], labyrinthe.liste_joueurs)
        self.assertIs(None, labyrinthe._ajouter_joueur("ultime", "Dernier Joueur"))

        for identifiant, joueur in liste_joueurs.items():
            labyrinthe._effacer_joueur(identifiant)
            self.assertNotIn(identifiant, labyrinthe.dict_client_joueur)
            self.assertNotIn(joueur, labyrinthe.liste_joueurs)

    def test_ajouter_effacer_joueur_fin_de_partie(self) -> None:
        """
        - Crée un labyrinthe contenant un nombre de positions de départ suffisant pour accueillir de nouveaux joueurs.
        - Ajoute les joueurs au labyrinthe.
        - Teste si les joueurs ajoutés sont inclus dans ``liste_joueurs`` et ``dict_client_joueurs`` du labyrinthe.
        - Change le mode du labyrinthe par ``jeu_en_cours``.
        - Teste si le labyrinthe crée de nouveaux joueurs.
        - Efface les joueurs du labyrinthe, sauf le dernier.
        - Teste si le labyrinthe est dans le mode ``fin_de_partie``.
        - Teste si le vainqueur est le dernier joueur resté en lice.
        """

        nombre_joueurs: int = 10
        liste_joueurs: Dict[int, Optional[Joueur]] = {}
        labyrinthe = Labyrinthe("D" * nombre_joueurs * 2 + "F")
        for identifiant in range(nombre_joueurs):
            liste_joueurs[identifiant] = labyrinthe._ajouter_joueur(identifiant, "Joueur" + str(identifiant))
            self.assertIs(liste_joueurs[identifiant], labyrinthe.dict_client_joueur[identifiant])
            self.assertIn(liste_joueurs[identifiant], labyrinthe.liste_joueurs)
        labyrinthe.mode = Labyrinthe.jeu_en_cours
        self.assertIs(None, labyrinthe._ajouter_joueur("ultime", "Dernier Joueur"))

        for identifiant, joueur in liste_joueurs.copy().items():
            labyrinthe._effacer_joueur(identifiant)
            liste_joueurs.pop(identifiant)
            self.assertNotIn(identifiant, labyrinthe.dict_client_joueur)
            self.assertNotIn(joueur, labyrinthe.liste_joueurs)
            if len(liste_joueurs) > 1:
                self.assertEqual(Labyrinthe.jeu_en_cours, labyrinthe.mode)
            else:
                break
        _, joueur = liste_joueurs.popitem()
        self.assertEqual(Labyrinthe.fin_de_partie, labyrinthe.mode)
        self.assertIs(joueur, labyrinthe.vainqueur)

    def test_dimensionner(self) -> None:
        """
        Pour chaque chaîne de caractères:

        - Construit une grille et détermine les points extrêmes de la grille.
        - Crée un labyrinthe basé sur la chaîne de caractère et ajoute un joueur.

        Pour chaque ``joueur_coordonnees``, assigne les coordonnnées au joueur:

        - Détermine les points extrêmes du plateau de jeu en tenant compte des coordonnées du joueur.
        - Compare les coordonnées au retour de ``dimensionner()`` dans les deux modes ``debut_de_partie`` et ``jeu_en_cours``.

        :raises AttributeError: si la labyrinthe n'a pas créé de joueur.
        """

        chaines: List[str] = ["D\nF",   # Grille 1x2 avec 1 départ et 1 fin
                              "DF",     # Grille 2x1 avec 1 départ et 1 fin
                              "DF\nD",  # Grille 2x2 avec 2 départs et 1 fin
                              "F\nDF"]  # Grille 2x2 avec 1 départ et 2 fins
        joueur_coordonnees: List[Coordonnees] = [(-1, 1),
                                                 (1, 10),
                                                 (0, 0)]
        for chaine in chaines:
            grille, _, _ = construire_grille(chaine)
            mini_debut_de_partie, maxi_debut_de_partie = (0, 0), (0, 0)
            for coordonnees in grille:
                mini_debut_de_partie, maxi_debut_de_partie = \
                    determiner_min_max(mini_debut_de_partie, maxi_debut_de_partie, coordonnees)
            labyrinthe = Labyrinthe(chaine)
            joueur = labyrinthe._ajouter_joueur("Joueur", "Joueur")

            for joueur_coordonnee in joueur_coordonnees:
                if joueur:
                    joueur.coordonnees = joueur_coordonnee
                else:
                    raise AttributeError
                mini_jeu_en_cours, maxi_jeu_en_cours = \
                    determiner_min_max(mini_debut_de_partie, maxi_debut_de_partie, joueur.coordonnees)
                labyrinthe.mode = Labyrinthe.debut_de_partie
                self.assertEqual((mini_debut_de_partie, maxi_debut_de_partie), labyrinthe._dimensionner())
                labyrinthe.mode = Labyrinthe.jeu_en_cours
                self.assertEqual((mini_jeu_en_cours, maxi_jeu_en_cours), labyrinthe._dimensionner())

    def test_determiner_departs(self) -> None:
        """
        Pour chaque chaîne de caractères:

        - Construit une grille et crée un labyrinthe.

        Pour chaque coordonnées ``departs`` du labyrinthe:

        - Détermine l'élément associé aux coordonnées.
        - Teste si l'élément associé est ``Demarrable``.
        - Teste si les coordonnées du départ sont dans la grille.
        """

        chaines: List[str] = ["FD\nDF",         # Grille 2x2 avec 2 départs et 2 fins
                              "DDD\nDTT\nDTF",  # Grille 3x3 avec 5 départs, 3 transformables et 1 fin
                              "FDTD",           # Grille 1x4 avec 1 fin, 2 départs (dont 1 séparé par un transformables)
                              "FDKD",           # Grille 1x4 avec 1 fin, 2 départs (dont 1 séparé par un obstacle)
                              "FDRD"]           # Grille 1x4 avec 1 fin, 2 départs (dont 1 séparé par un traversable)
        for chaine in chaines:
            grille, _, _ = construire_grille(chaine)
            labyrinthe = Labyrinthe(chaine)

            for coordonnees in labyrinthe.departs:
                try:
                    element = grille[coordonnees]
                except IndexError:
                    element = cast(Type[Decrypte], Elements.obstacle_par_defaut)
                self.assertTrue(issubclass(element, Demarrable))
                self.assertIn(coordonnees, grille)

    def test_afficher_plateau(self) -> None:
        """
        A partir de la chaîne de caractère:

        - Construit une ``grille_reference`` et crée un labyrinthe.
        - Construit une ``grille_obtenue`` depuis la chaîne générée par ``afficher_plateau()``.
        - Compare les deux ``grille_reference`` et ``grille_obtenue``.
        - Ajoute deux joueurs et leur assigne des coordonnées.
        - Change le mode du labyrinthe en ``jeu_en_cours``.
        - Compare la ``chaine_reference`` à la chaîne générée par ``afficher_plateau()``.

        :raises AttributeError: si la labyrinthe n'a pas créé de joueur.
        """

        # Grille 3x2 | Fin    / Départ / Transformable
        #            | Départ / Défaut / Défaut
        chaine: str = "FDT\nD"
        grille_reference, _, _ = construire_grille(chaine)
        labyrinthe = Labyrinthe(chaine)
        grille_obtenue, _, _ = construire_grille(labyrinthe._afficher_plateau())
        self.assertEqual(grille_reference, grille_obtenue)

        # Grille 3x2 | Fin    / Départ / Transformable
        #            | Joueur / Défaut / Adversaire
        chaine_reference = "FDT\nXOx"
        joueur = labyrinthe._ajouter_joueur("Joueur", "Joueur")
        adversaire = labyrinthe._ajouter_joueur("Adversaire", "Adversaire")
        if joueur and adversaire:
            joueur.coordonnees = (0, 1)
            adversaire.coordonnees = (2, 1)
        else:
            raise AttributeError
        labyrinthe.mode = Labyrinthe.jeu_en_cours
        self.assertEqual(chaine_reference + "\n", labyrinthe._afficher_plateau(joueur))

    def test_ajouter_commande(self) -> None:
        """
        Crée un labyrinthe et ajoute un joueur. Pour chaque saisie dans la liste ``saisie``:

        - Ajoute les commandes au joueur.
        - Compare les commandes en ``reference`` à la liste ``commandes`` du joueur.

        :raises AttributeError: si la labyrinthe n'a pas créé de joueur.
        """

        chaine: str = "FD"  # Grille 1x2 avec 1 fin et 1 départ
        labyrinthe = Labyrinthe(chaine)
        joueur = labyrinthe._ajouter_joueur("Joueur", "Joueur")
        if not joueur:
            raise AttributeError
        saisies: List[str] = ["N2", "ES"]
        reference: List[str] = ["N", "N", "E", "S"]
        for saisie in saisies:
            labyrinthe.ajouter_commande("Joueur", saisie)
        self.assertEqual(reference, joueur.commandes)


class AffichageTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions d'affichage de la classe ``Labyrinthe``.
    """

    dossier_courant: ClassVar[str] = path.dirname(__file__)
    extension: ClassVar[str] = ".txt"
    carte: ClassVar[str] = "sans_bord"
    chemin: ClassVar[str] = path.join(dossier_courant, "test labyrinthe/" + carte + extension)

    def setUp(self) -> None:
        """
        Avant chaque test, crée un labyrinthe depuis la ``carte``.
        """
        self.chaine: str = str()
        with open(self.chemin, "r") as fichier:
            self.chaine = fichier.read()
        self.labyrinthe = Labyrinthe(self.chaine, self.carte)

    def test_placement_aleatoire_des_joueurs(self) -> None:
        """
        - Ajoute un nombre de joueurs égal aux positions de départ disponibles.
        - Stocke les identifiants des joueurs dans ``liste_joueurs``.
        - Débute une partie pour affecter une position à chaque joueur.
        - Collecte les coordonnées de chaque joueur dans ``liste_coordonnees``.
        - Teste si la liste triée des coordonnées est égale à la liste triée des positions de départ possibles.
        """

        liste_identifiants: List[Any] = []
        for indice in range(len(self.labyrinthe.departs)):
            self.labyrinthe.ajouter_joueur("identifiant" + str(indice), "Joueur" + str(indice))
            liste_identifiants.append("identifiant" + str(indice))
        self.labyrinthe.demarrer()
        liste_coordonnees = []
        for identifiant in liste_identifiants:
            liste_coordonnees.append(self.labyrinthe.dict_client_joueur[identifiant].coordonnees)
        self.assertEqual(sorted(liste_coordonnees), sorted(self.labyrinthe.departs))

    def test_deroulement_du_jeu(self) -> None:
        """
        - Définit trois positions de départ et les suites de mouvements associés pour gagner la partie.
        - Ajoute trois joueurs et débute une partie.
        - "Triche" et redéfinit les coordonnées des joueurs, le premier joueur (indice 0) sera vainqueur.
        - Ajoute les commandes de chaque joueur et fait ``jouer()`` le labyrinthe.
        - En sortie de ``jouer()``, le premier joueur a atteint la sortie, et le jeu se termine.
        - Teste si le labyrinthe est en mode ``fin_de_partie`` et si le vainqueur est le premier joueur.
        - Appelle ``terminer()`` pour annoncer le vainqueur.
        """

        vainqueur: Optional[Joueur] = None
        departs: List[Coordonnees] = [(7, 0), (3, 7), (3, 9)]
        commandes: List[List[str]] = [['PS', 'S3', 'PS', 'SE2', 'S'],   # 9 mouvements, Vainqueur !
                                      ['PN', 'N2', 'PE', 'E6'],         # 10 mouvements
                                      ['N2', 'E6', 'N2']]               # 10 mouvements

        for indice in range(len(departs)):
            self.labyrinthe.ajouter_joueur("identifiant" + str(indice), "Joueur" + str(indice))
        self.labyrinthe.demarrer()

        for indice, joueur in enumerate(self.labyrinthe.liste_joueurs):
            joueur.coordonnees = departs[indice]
            if indice == 0:
                vainqueur = joueur

        for indice, joueur in enumerate(self.labyrinthe.liste_joueurs):
            for commande in commandes[indice]:
                self.labyrinthe.ajouter_commande(joueur.identifiant_client, commande)

        self.labyrinthe.jouer()

        self.assertEqual(Labyrinthe.fin_de_partie, self.labyrinthe.mode)
        self.assertIs(vainqueur, self.labyrinthe.vainqueur)

        self.labyrinthe.terminer()
