# -*-coding:Utf-8 -*

"""
Ce module contient la classe ``Labyrinthe``.
"""

from typing import Tuple, Dict, List, Set, Any, Iterator, Optional, cast, Type, Final
from operator import itemgetter
from random import randint, sample, shuffle
import element
import controle
import regle
from joueur import Joueur

# Alias de types
Coordonnees = Tuple[int, int]
Grille = Dict[Coordonnees, element.Obstacle]
Categorie = str
Message = str
Datagramme = Tuple[Any, Categorie, Message]


class Labyrinthe:
    """
    Initialise un labyrinthe à partir d'une chaîne de caractères.
    Valide les mouvements des joueurs et actualise la grille de jeu.

    Pour ajouter ou retirer un joueur:

    - ``ajouter_joueur(identifiant, nom)``
    - ``effacer_joueur(identifiant)``

    Déroulement d'une partie:

    - ``accueillir(identifiant, nom)``, avant le début d'une partie, ajoute un joueur et retourne le message d'accueil.
    - ``demarrer()``, définit les positions des joueurs, transmet le plateau de jeu et débute la partie.
    - ``ajouter_commande(identifiant, saisie)``, traduit la chaîne de caractères en commandes.
    - ``jouer()``, extrait les commandes et les valide, puis actualise les nouvelles positions des joueurs.
    - ``afficher_jeu()``, transmet une chaîne de caractères représentant le plateau du labyrinthe.
    - ``terminer()``, en fin de partie, affiche le vainqueur.

    :param chaine: chaîne de caractères représentant les éléments d'un labyrinthe.
    :param nom: nom du labyrinthe.
    """

    debut_de_partie: Final[int] = 0
    jeu_en_cours: Final[int] = 1
    fin_de_partie: Final[int] = 2

    def __init__(self, chaine: str, nom: str = str()) -> None:
        """
        Initialise les variables du labyrinthe et appelle ``creer_labyrinthe()`` pour construire la grille des éléments.

        ``sorties`` stocke les positions gagnantes.
        ``departs`` stocke les positions possibles pour démarrer la partie.
        ``caracteres_inconnus`` liste les caractères qui n'ont pas pu être décodés à la lecture d'une carte.

        :param chaine: chaîne de caractères représentant les éléments d'un labyrinthe.
        :param nom: nom du labyrinthe.
        """

        self.nom_labyrinthe = nom
        self.grille: Grille = {}
        self.sorties: List[Coordonnees] = []
        self.departs: List[Coordonnees] = []
        self.caracteres_inconnus: Set[str] = set()
        self.dict_client_joueur: Dict[Any, Joueur] = {}
        self.liste_joueurs: List[Joueur] = []
        self.joueur_courant: Optional[Joueur] = None
        self.mode: int = self.debut_de_partie
        self.vainqueur: Optional[Joueur] = None

        self.creer_labyrinthe(chaine)
        self.determiner_departs()

    @classmethod
    def get_symboles_connus(cls) -> Set[element.SymboleCarte]:
        """
        Retourne la liste des éléments connus pour la lecture d'une carte.

        :return: set d'éléments connus.
        """

        return set(element.Elements.decryptable)

    @classmethod
    def get_symboles_obligatoire(cls) -> Set[element.SymboleCarte]:
        """
        Retourne la liste des éléments qui font gagner la partie.

        :return: set d'éléments *gagnables*.
        """

        return set(element.Elements.gagnable)

    @classmethod
    def get_validation_controle(cls) -> controle.Regex:
        """
        Retourne l'expression régulière de validation d'une saisie utilisateur.

        :return: expression régulière de validation.
        """

        return controle.validation_controle

    def creer_labyrinthe(self, chaine: str) -> None:
        """
        Crée une grille de labyrinthe à partir d'une chaîne de caractère.

        Décode les caractères d'une carte depuis les éléments connus.
        Identifie les caractères qui ne représentent pas d'élément connu.
        Identifie les 'sorties' et les stocke.
        Si l'élément est ``Decrypté``, ses coordonnées sont stockées en grille.

        :param chaine: chaîne de caractères représentant les éléments d'un labyrinthe.
        """

        for ordonnee, ligne in enumerate(chaine.splitlines()):
            for abscisse, caractere in enumerate(ligne):
                try:
                    obstacle = element.Elements.decryptable[caractere.upper()]
                except KeyError:
                    obstacle = element.Elements.obstacle_par_defaut
                    self.caracteres_inconnus.add(caractere.upper())
                if issubclass(obstacle, element.Gagnable):
                    self.sorties.append((abscisse, ordonnee))
                if issubclass(obstacle, element.Decrypte):
                    self.grille[(abscisse, ordonnee)] = obstacle

    def determiner_departs(self) -> None:
        """
        Identifie toutes les positions de départ dans la grille par ordre d'éloignement depuis les sorties.

        Depuis les sorties,
        liste les positions accessibles par recursion selon les déplacements définis dans la classe ``Mouvement``.
        Teste si la position atteinte ne l'a pas déjà été précédemment (présence dans ``liste_positions``).
        Identifie l'élément du labyrinthe dans la grille (ou utilise ``obstacle_par_defaut`` si absent de la grille).

        - si l'élément est ``Demarrable``, stocke ce départ possible et ajoute les coordonnées à une distance +1 de la position
          actuelle.
        - sinon, si l'élément est ``Traversable``, ajoute les coordonnées à une distance +1 de la position actuelle.
        - sinon, si l'élément est ``Transformable`` et sa transformée est ``Traversable``, ajoute les coordonnées à une
          distance +2 de la position actuelle.

        Mélange aléatoirement les départs possibles iso-distants des sorties et les ajoute dans ``departs``.
        """
        coordonnees_min, coordonnees_max = self.dimensionner()
        liste_positions = {sortie: 0 for sortie in self.sorties}
        distance = 0
        while [position for position, indice in liste_positions.items() if indice >= distance]:
            departs: List[Coordonnees] = []
            positions_testees = [position for position, indice in liste_positions.items() if indice == distance]
            for position_testee in positions_testees:
                for direction in controle.Mouvement.directions:
                    coordonnees = (position_testee[0] + direction[0], position_testee[1] + direction[1])
                    if coordonnees_min[0] <= coordonnees[0] <= coordonnees_max[0] \
                            and coordonnees_min[1] <= coordonnees[1] <= coordonnees_max[1]:
                        if coordonnees not in [*liste_positions]:
                            try:
                                terrain = cast(Type[element.Element], self.grille[coordonnees])
                            except KeyError:
                                terrain = element.Elements.obstacle_par_defaut
                            if issubclass(terrain, element.Demarrable):
                                liste_positions[coordonnees] = distance + 1
                                departs.append(coordonnees)
                            elif issubclass(terrain, element.Traversable):
                                liste_positions[coordonnees] = distance + 1
                            elif issubclass(terrain, element.Transformable):
                                if issubclass(terrain.transformee, element.Traversable):
                                    liste_positions[coordonnees] = distance + 2
            if departs:
                shuffle(departs)
                self.departs.extend(departs)
            distance += 1

    def dimensionner(self) -> Tuple[Coordonnees, Coordonnees]:
        """
        Détermine la taille du plateau du labyrinthe en considérant la grille d'éléments et les coordonnées des joueurs.
        La taille du plateau est variable car le joueur peut se déplacer au-delà de la grille d'éléments.

        Extrait les coordonnées des éléments de la grille.
        Si la partie a débuté, extrait les coordonnées des joueurs et extrait les plus petite et plus grande abscisses
        (respectivement les ordonnées).

        :return: coordonnées des deux extrêmes du plateau du labyrinthe.
        """

        liste_coordonnees = [*self.grille]
        if self.mode >= self.jeu_en_cours:
            liste_coordonnees += [joueur.coordonnees for joueur in self.liste_joueurs]
        if liste_coordonnees:
            liste_coordonnees = sorted(liste_coordonnees, key=itemgetter(0))
            min_abscisse = liste_coordonnees[0][0]
            max_abscisse = liste_coordonnees[-1][0]
            liste_coordonnees = sorted(liste_coordonnees, key=itemgetter(1))
            min_ordonnee = liste_coordonnees[0][1]
            max_ordonnee = liste_coordonnees[-1][1]
        else:
            min_abscisse, min_ordonnee = 0, 0
            max_abscisse, max_ordonnee = 0, 0
        return (min_abscisse, min_ordonnee), (max_abscisse, max_ordonnee)

    def afficher_plateau(self, joueur: Optional[Joueur] = None) -> str:
        """
        Représente le plateau du labyrinthe et la position des joueurs avec une chaîne de caractères.

        Pour chaque position (abscisse et ordonnée) du plateau, si la partie a débuté teste si les coordonnées sont celles du
        joueur ou d'un adversaire.
        Teste si les coordonnées sont celle d'un élément de la grille.
        Ajoute la représentation ``__str__()`` de la classe ``Joueur``, ``Adversaire`` ou ``Element`` au ``plateau``.

        :param joueur: joueur qui recevra la représentation du plateau.
        :return: chaîne de caractères représentant le plateau.
        """

        coordonnees_min, coordonnees_max = self.dimensionner()
        coordonnees_adversaires: List[Coordonnees] = []
        coordonnees_joueur: Optional[Coordonnees] = None
        if self.mode >= self.jeu_en_cours and joueur:
            liste_adversaires = self.liste_joueurs.copy()
            liste_adversaires.remove(joueur)
            coordonnees_adversaires = [adversaire.coordonnees for adversaire in liste_adversaires]
            coordonnees_joueur = joueur.coordonnees

        plateau = str()
        for ordonnee in range(coordonnees_min[1], coordonnees_max[1] + 1):
            for abscisse in range(coordonnees_min[0], coordonnees_max[0] + 1):
                if (abscisse, ordonnee) == coordonnees_joueur:
                    plateau += str(element.Robot)
                elif (abscisse, ordonnee) in coordonnees_adversaires:
                    plateau += str(element.Adversaire)
                else:
                    try:
                        piece = self.grille[abscisse, ordonnee]
                    except KeyError:
                        plateau += str(element.Elements.obstacle_par_defaut)
                    else:
                        plateau += str(piece)
            plateau += "\n"
        return plateau

    def ajouter_joueur(self, identifiant_client: Any, nom: str) -> Optional[Joueur]:
        """
        Si la partie n'a pas débuté, et s'il y a suffisamment de positions de départ, instancie un joueur et l'ajoute à la
        liste des joueurs du labyrinthe.

        :param  identifiant_client: variable qui associe le joueur au client réseau.
        :param  nom: nom du joueur.
        :return: le joueur ajouté à la liste.
        """
        if self.mode == self.debut_de_partie and self.est_ouvert():
            joueur = Joueur(identifiant_client, nom)
            self.dict_client_joueur[identifiant_client] = joueur
            self.liste_joueurs.append(joueur)
            return joueur
        else:
            return None

    def effacer_joueur(self, identifiant_client: Any) -> None:
        """
        Supprime le joueur identifié par ``identifiant_client`` de la liste des joueurs du labyrinthe.
        Si la partie a débuté, teste s'il reste plus d'un joueur en lice. Dans le cas contraire, termine la partie et désigne
        vainqueur le joueur restant.

        :param identifiant_client: variable qui associe le joueur au client réseau.
        :raises KeyError: si ``identifiant_client`` ne correspond à aucun joueur.
        """

        joueur = self.dict_client_joueur[identifiant_client]
        self.dict_client_joueur.pop(identifiant_client)
        self.liste_joueurs.remove(joueur)
        if self.mode >= self.jeu_en_cours:
            if len(self.liste_joueurs) <= 1:
                self.mode = self.fin_de_partie
                try:
                    self.vainqueur = self.liste_joueurs[0]
                except IndexError:
                    pass

    def est_ouvert(self) -> bool:
        """
        Teste si le labyrinthe peut accueillir de nouveaux joueurs en fonction du nombre restant de positions de départs.

        :return: True si le labyrinthe peut accueillir un nouveau joueur. False sinon.
        """

        return len(self.liste_joueurs) < len(self.departs)

    def accueillir(self, identifiant_client: Any, nom: str) -> Iterator[Datagramme]:
        """
        Ajoute un nouveau joueur à la partie.
        Si le joueur est ajouté, retourne les messages d'accueil et le plateau pour le nouveau joueur.

        :param identifiant_client: variable qui associe le joueur au client réseau.
        :param nom: nom du joueur.
        :return: messages pour le nouveau client réseau selon le format ``(client, categorie, message)``.
        """

        if self.ajouter_joueur(identifiant_client, nom):
            yield identifiant_client, 'affichage', ""
            yield identifiant_client, 'affichage', "Bienvenue, " + nom + "."
            yield identifiant_client, 'affichage', "Vous jouez sur le labyrinthe '" + self.nom_labyrinthe + "'"
            yield identifiant_client, 'affichage', self.afficher_plateau()

    def demarrer(self) -> Iterator[Datagramme]:
        """
        Définit les positions de départs des joueurs.
        Retourne pour chaque joueur les descriptions des contrôles autorisés et le plateau du labyrinthe.

        Choisit aléatoirement un entier compris entre 0 et *nombre de départs possibles* - *nombre de joueurs*.
        Mélange les joueurs, puis attribue les positions de départ à partir de l'indice.
        Les positions sont classées par distance croissante à une sortie du labyrinthe (voir ``creer_labyrinthe()``).
        L'attribution de positions consécutives répartit équitablement les joueurs sur le plateau.

        :return: messages pour les clients réseau.
        """

        self.mode = self.jeu_en_cours

        indice = randint(0, len(self.departs) - len(self.liste_joueurs))
        self.liste_joueurs = sample(self.liste_joueurs, len(self.liste_joueurs))
        for joueur in sample(self.liste_joueurs, len(self.liste_joueurs)):
            joueur.coordonnees = self.departs[indice]
            indice += 1

        for identifiant_client, joueur in self.dict_client_joueur.items():
            yield identifiant_client, 'affichage', "La partie commence! Vous êtes " \
                + str(len(self.liste_joueurs)) + " joueurs"
            for description in controle.Controle.descriptions:
                yield identifiant_client, 'affichage', description
            yield identifiant_client, 'affichage', self.afficher_plateau(joueur)
            yield identifiant_client, 'affichage', ""
            yield identifiant_client, 'affichage', "C'est à " + self.liste_joueurs[0].nom + " de jouer"

    def afficher_jeu(self) -> Iterator[Datagramme]:
        """
        Retourne pour chaque joueur le plateau du labyrinthe.

        :return: messages pour les clients réseau.
        """

        for identifiant_client, joueur in self.dict_client_joueur.items():
            yield identifiant_client, 'affichage', self.afficher_plateau(joueur)
            yield identifiant_client, 'affichage', ""

    def ajouter_commande(self, identifiant_client: Any, saisie: str) -> List[str]:
        """
        Extrait les commandes depuis la chaîne de caractères saisie par le joueur, et les ajoute à la liste de commandes
        pré-existantes.

        :param identifiant_client: variable qui associe le joueur au client réseau.
        :param saisie: saisie du client réseau.
        :return: commandes.
        """

        commandes = controle.extraire(saisie)
        joueur = self.dict_client_joueur[identifiant_client]
        joueur.ajouter_commande(commandes)
        return joueur.commandes

    def jouer(self) -> Iterator[Datagramme]:
        """
        Tant que les joueurs ont des commandes en attente et tant que la partie n'est pas terminée, pour chaque joueur à tour
        de rôle:

        - Extrait les composantes ``direction`` et ``transformation`` de la prochaine commande jouée.
        - Vérifie que la commande suit les règles du labyrinthe.
        - Déplace le joueur ou transforme l'élément de grille du labyrinthe.
        - Affiche le plateau du labyrinthe pour tous les joueurs.

        ``liste_joueurs`` définit l'ordre des joueurs. Le prochain à jouer est en début de liste.
        Pour vérifier que la commande suit les règles du labyrinthe, un ``instantane`` est créé et représente l'état du
        labyrinthe *(la commande, la grille d'éléments, le joueur et la liste des joueurs)*.

        Si une règle est violée, la raison est retournée au joueur et la prochaine commande du même joueur est testée.
        Si une partie est gagnée, le joueur est déclaré vainqueur.

        :return: messages pour les clients réseau.
        """

        while self.mode < self.fin_de_partie:
            self.joueur_courant = self.liste_joueurs.pop(0)
            try:
                commande = self.joueur_courant.retirer_commande()
            except IndexError:
                self.liste_joueurs.insert(0, self.joueur_courant)
                self.joueur_courant = None
                break
            else:
                direction, transformation = controle.obtenir_controle(commande)
                instantane = regle.Etat(direction, transformation, self.grille, self.joueur_courant, self.liste_joueurs)
                try:
                    regle.verifier_regles(instantane)
                except regle.HorsRegles as e:
                    yield self.joueur_courant.identifiant_client, 'affichage', str(e)
                    self.liste_joueurs.insert(0, self.joueur_courant)
                    self.joueur_courant = None
                    continue
                except regle.PartieGagnee:
                    self.mode = self.fin_de_partie
                    self.vainqueur = self.joueur_courant

                if instantane.transformation:
                    if issubclass(instantane.obstacle, element.Transformable) and\
                            issubclass(instantane.obstacle.transformee, element.Decrypte):
                        self.grille[instantane.coordonnees_obstacle] = instantane.obstacle.transformee
                    else:
                        try:
                            del self.grille[instantane.coordonnees_obstacle]
                        except KeyError:
                            pass
                else:
                    self.joueur_courant.coordonnees = instantane.coordonnees_obstacle

                self.liste_joueurs.append(self.joueur_courant)
                self.joueur_courant = None
                for identifiant_client, joueur in self.dict_client_joueur.items():
                    yield identifiant_client, 'affichage', self.afficher_plateau(joueur)
                    yield identifiant_client, 'affichage', ""
                    if self.mode < self.fin_de_partie:
                        yield identifiant_client, 'affichage', "C'est à " + self.liste_joueurs[0].nom + " de jouer"

    def terminer(self) -> Iterator[Datagramme]:
        """
        Retourne à chaque joueur le vainqueur de la partie.

        :return: messages pour les clients réseau.
        """
        for identifiant_client, joueur in self.dict_client_joueur.items():
            if self.vainqueur == joueur:
                yield identifiant_client, 'affichage', "Vous avez gagné la partie !"
            elif self.vainqueur:
                yield identifiant_client, 'affichage', self.vainqueur.nom + " a gagné la partie !"
