# -*-coding:Utf-8 -*

"""
Ce module contient les classes RequestHandler et ThreadedTCPServer
et la fonction creer_un_compteur()
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
    Crée un générateur pour compter depuis 'nombre_initial"

    :param int nombre_initial: nombre de départ
    :return: compteur initialisé sur nombre_initial
    :rtype: Generator[int, None, None]
    """

    while True:
        yield nombre_initial
        nombre_initial += 1


# Générateur qui compte depuis 1
compter: Final = creer_un_compteur(1)


class RequestHandler(socketserver.BaseRequestHandler, Transmission):
    """
    Après acceptation d'une connexion par le serveur (via la classe ThreadedTCPServer),
    un nouveau Thread instancie RequestHandler avec les informations liées au client ('requete', 'adresse_client')

    L'instance communique auprès de Main Thread par la Messagerie. Elle permet de
    - informer Main Thread d'un nouveau joueur
    - écouter et transmettre les messages du client
    - prévenir Main Thread de la déconnexion du client

    Les messages transmis à Main Thread sont des tuples (emetteur, categorie, message)
    """

    def __init__(self, requete: socket, adresse_client: Adresse, serveur: socketserver.TCPServer) -> None:
        """
        Définit le nom du Joueur en incrémentant 'compter'

        :param socket requete: connexion du client
        :param Adresse adresse_client: adresse du client
        :param serveur: instance du serveur qui a créé la RequestHandler
        :type serveur: TCPServer
        """

        self.nom_joueur = "Joueur " + str(next(compter))
        # Erreur mypy relative au bug décrit sur https://github.com/python/mypy/issues/5887
        super().__init__(requete, adresse_client, serveur)  # type: ignore

    def setup(self) -> None:
        """
        Informe Main Thread d'un nouveau joueur par la Messagerie
        Exécute ensuite 'handle()'
        """

        Messagerie.ajouter((self, 'nouveau_joueur', None))

    def handle(self) -> None:
        """
        Recupère le message du client
        ajoute la référence à l'instance RequestHandler liée au client émetteur
        et transmet le message à la liste Messagerie

        En cas d'erreur réseau, le Thread sort de la boucle infinie et exécute 'finish()'
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
        Informe Main Thread que le client s'est déconnecté
        """

        Messagerie.ajouter((self, 'quitte', None))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Ouvre une socket et crée un Thread Serveur qui attend de nouvelles connexions
    Quand un client se connecte, lance un Thread qui instancie 'classe_gestionnaire' pour échanger avec le client

    Si 'connxion_autorisee' est à False, le Serveur refuse toute nouvelle connexion
    """

    def __init__(self, adresse_serveur: Adresse,
                 classe_gestionnaire: Type[socketserver.BaseRequestHandler] = RequestHandler) -> None:
        """
        Initie le Thread Serveur qui attendra de nouvelles connexions
        Transmet l'adresse et la 'classe_gestionnaire' à ThreadingMixIn

        :param Adresse adresse_serveur: adresse du serveur
        :param classe_gestionnaire: classe qui permet d'instancier les RequestHandler
        :type classe_gestionnaire: Type[BaseRequestHandler]
        """

        self.thread = threading.Thread(name="Serveur", target=self.serve_forever)
        self.connexion_autorisee = False
        super().__init__(adresse_serveur, classe_gestionnaire)

    def verify_request(self, requete: bytes, client_address: Adresse) -> bool:
        """
        Pour chaque demande de connexion, le Serveur accepte si 'verify_request()' retourne True

        :param bytes requete: connexion client
        :param Adresse client_address: adresse du client
        :return: si la requête est acceptée ou rejetée
        :rtype: bool
        """

        return self.connexion_autorisee

    def __enter__(self) -> 'ThreadedTCPServer':
        """
        Utilisé avec le gestionnaire de contexte 'with'

        :return: retourne l'instance en cours
        :rtype: ThreadedTCPServer
        """

        # Surcharge la méthode de BaseServer pour éviter une erreur mypy
        return self
