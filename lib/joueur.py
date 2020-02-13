# -*-coding:Utf-8 -*

"""
Ce module contient la classe ``Joueur``.
"""

from typing import Any, List, Tuple, Iterable

# Alias de types
Commande = Any
Coordonnees = Tuple[int, int]


class Joueur:
    """
    Représente un joueur et ses coordonnées.
    Stocke les commandes saisies par le client réseau.

    :param identifiant_client: variable qui associe le joueur au client réseau.
    :param nom: nom du joueur.
    """

    def __init__(self, identifiant_client: Any, nom: str) -> None:
        """
        Créer un joueur depuis un identifiant et initialise les coordonnées et les commandes.

        :param identifiant_client: variable qui associe le joueur au client réseau.
        :param nom: nom du joueur.
        """

        self.identifiant_client = identifiant_client
        self.nom = nom
        self.coordonnees: Coordonnees = (0, 0)
        self.commandes: List[Commande] = []

    def ajouter_commande(self, saisie: Iterable[Commande]) -> None:
        """
        Ajoute des commandes à la liste de commande du joueur.

        :param saisie: saisie valide du client réseau.
        """

        self.commandes.extend(saisie)

    def retirer_commande(self) -> Commande:
        """
        Retourne la première commande de la liste.

        :return: première commande.
        """

        return self.commandes.pop(0)
