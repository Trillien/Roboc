# -*-coding:Utf-8 -*

"""
Ce module contient les classes ``RequestHandler`` et ``ThreadedTCPServer`` et la fonction ``creer_un_compteur()``.
"""

from typing import Tuple, Generator, Type, Final
from socket import socket
import socketserver
import threading
from messagerie import Messagerie, Transmission, ConnectionFermee

# Alias de type pour les adresses des clients
Adresse = Tuple[str, int]


def creer_un_compteur(nombre_initial: int) -> Generator[int, None, None]:
    """
    Crée un générateur pour compter depuis ``nombre_initial``.

    :param nombre_initial: c'est le nombre de départ.
    :return: compteur initialisé sur ``nombre_initial``.
    """

    while True:
        yield nombre_initial
        nombre_initial += 1


# Générateur qui compte depuis 1
compter: Final = creer_un_compteur(1)


class RequestHandler(socketserver.BaseRequestHandler, Transmission):
    """
    Après acceptation d'une connexion par le serveur (via la classe ``ThreadedTCPServer``),
    un nouveau Thread instancie ``RequestHandler`` avec les informations liées au client ``(requete, adresse_client)``.

    L'instance communique auprès de *Main Thread* par la classe ``Messagerie``. Elle permet de :

    - informer *Main Thread* d'un nouveau joueur.
    - écouter et transmettre les messages du client.
    - prévenir *Main Thread* de la déconnexion du client.

    Les messages transmis à *Main Thread* sont des tuples ``(emetteur, categorie, message)``

    :param requete: connexion du client.
    :param adresse_client: adresse du client.
    :param serveur: instance du serveur qui a créé la ``RequestHandler``.
    """

    def __init__(self, requete: socket, adresse_client: Adresse, serveur: socketserver.TCPServer) -> None:
        """
        Définit le nom du Joueur en incrémentant ``compter``.
        Génère une erreur mypy relative au bug décrit sur : https://github.com/python/mypy/issues/5887

        :param requete: connexion du client.
        :param adresse_client: adresse du client.
        :param serveur: instance du serveur qui a créé la ``RequestHandler``.
        """

        self.nom_joueur = "Joueur-" + str(next(compter))
        super().__init__(requete, adresse_client, serveur)  # type: ignore

    def setup(self) -> None:
        """
        Informe *Main Thread* d'un nouveau joueur par la classe ``Messagerie``.
        Exécute ensuite ``handle()``.
        """

        Messagerie.ajouter((self, 'nouveau_joueur', None))

    def handle(self) -> None:
        """
        Recupère le message du client.
        Ajoute la référence à l'instance ``RequestHandler`` liée au client émetteur.
        Et transmet le message à la liste de la classe ``Messagerie``.

        En cas d'erreur réseau, le Thread sort de la boucle infinie et exécute ``finish()``.
        """

        while True:
            try:
                Messagerie.ajouter((self, *self.recevoir()))
            except TypeError:
                continue
            except (ConnectionFermee, ConnectionResetError, ConnectionAbortedError, OSError):
                break

    def finish(self) -> None:
        """
        Informe *Main Thread* que le client s'est déconnecté.
        """

        Messagerie.ajouter((self, 'quitte', None))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Ouvre une socket et crée un Thread *Serveur* qui attend de nouvelles connexions.
    Quand un client se connecte, lance un Thread qui instancie ``classe_gestionnaire`` pour échanger avec le client.

    Si ``connexion_autorisee`` est à False, le *Serveur* refuse toute nouvelle connexion.

    :param adresse_serveur: adresse du serveur.
    :param classe_gestionnaire: classe qui permet d'instancier les ``RequestHandler``.
    """

    def __init__(self, adresse_serveur: Adresse,
                 classe_gestionnaire: Type[socketserver.BaseRequestHandler] = RequestHandler) -> None:
        """
        Initie le Thread *Serveur* qui attendra de nouvelles connexions.
        Transmet l'``adresse_serveur`` et la ``classe_gestionnaire`` à ``ThreadingMixIn``.

        :param adresse_serveur: adresse du serveur.
        :param classe_gestionnaire: classe qui permet d'instancier les ``RequestHandler``.
        """

        self.thread = threading.Thread(name="Serveur", target=self.serve_forever)
        self.connexion_autorisee = False
        super().__init__(adresse_serveur, classe_gestionnaire)

    def verify_request(self, requete: bytes, client_address: Adresse) -> bool:
        """
        Pour chaque demande de connexion, le *Serveur* accepte si ``verify_request()`` retourne True.

        :param requete: connexion client.
        :param client_address: adresse du client.
        :return: retourne True si la requête est acceptée. False si elle est rejetée.
        """

        return self.connexion_autorisee

    def __enter__(self) -> 'ThreadedTCPServer':
        """
        Utilisé avec le gestionnaire de contexte ``with``.
        Surcharge la méthode de ``BaseServer`` pour éviter une erreur mypy.

        :return: retourne l'instance en cours.
        """

        return self
