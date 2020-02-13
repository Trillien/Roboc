# -*-coding:Utf-8 -*

"""
Ce module contient les classes ``RequestHandlerTest`` et ``ThreadedTCPServerTest``.
"""

from typing import Dict, Tuple, List, ClassVar, Final
from lib.interface_serveur import RequestHandler, ThreadedTCPServer
from lib.messagerie import Messagerie
import socketserver
import socket
import threading
import unittest

# Alias de type pour les adresses des clients et serveurs
Adresse = Tuple[str, int]
adresse: Final[Adresse] = ('localhost', 12800)


class Serveur:
    """
    Crée un serveur.
    """

    def __init__(self) -> None:
        """
        Définit une socket.
        Stocke la socket des clients dans un dictionnaire ``{socket: adresse}``.
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[socket.socket, Adresse] = {}

    def demarrer_serveur(self) -> None:
        """
        Démarre le serveur sur l'adresse de connexion.
        """

        self.socket.bind(adresse)
        self.socket.listen(5)

    def accepter_connexion(self) -> Tuple[socket.socket, Adresse]:
        """
        Accepte une connexion et stocke les informations du client.

        :return: adresse du client.
        """

        client, adresse_client = self.socket.accept()
        self.clients[client] = adresse_client
        return client, adresse_client

    def fermer_connexion(self, client: socket.socket) -> None:
        """
        Ferme la connexion du client et efface le client du dictionnaire.

        :param client: socket client à fermer.
        """

        client.close()
        del self.clients[client]

    def arreter_serveur(self) -> None:
        """
        Pour toutes les connexions clientes actives, ferme la connexion.
        Puis ferme la socket du serveur.
        """

        for client in self.clients.copy():
            self.fermer_connexion(client)
        self.socket.close()


class Client:
    """
    Crée un client.
    """

    def __init__(self) -> None:
        """
        Définit une socket client.
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connecter(self) -> None:
        """
        Etablit une connexion sur l'adresse du serveur.
        """

        self.socket.connect(adresse)

    def fermer_connexion(self) -> None:
        """
        Ferme la socket du client.
        """

        self.socket.close()


class SimpleHandler(socketserver.BaseRequestHandler):
    """
    Classe *gestionnaire* instanciée par le serveur après chaque connexion client acceptée.
    Stocke les sockets des clients dans la liste ``clients``.
    Initialise une ``barriere`` qui se lève lorsque tous les Threads l'ont atteinte.
    Initialise un ``signal`` qui bloque le Thread dans ``handle()``.
    """

    clients: ClassVar[List[socket.socket]] = []
    barriere: ClassVar[threading.Barrier]
    signal: ClassVar[threading.Event] = threading.Event()

    def setup(self) -> None:
        """
        Ajoute la socket du client à la liste ``clients``.
        """

        self.clients.append(self.request)

    def handle(self) -> None:
        """
        Bloque le Thread tant que ``barriere`` n'est pas levée.
        Bloque ensuite le Thread tant que ``signal`` n'est pas reçu.
        """

        self.barriere.wait()
        self.signal.wait()

    @classmethod
    def effacer(cls) -> None:
        """
        Réinitialise les variables de la classe ``SimpleHandler``.
        """

        cls.clients = []
        cls.signal.clear()


class RequestHandlerTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions de la classe ``RequestHandler``.
    """

    def setUp(self) -> None:
        """
        Avant chaque test, crée et démarre un serveur.
        """

        self.serveur: Serveur = Serveur()
        self.serveur.demarrer_serveur()
        self.clients: List[Client] = []

    def tearDown(self) -> None:
        """
        Après chaque test, arrête le serveur.
        """

        self.serveur.arreter_serveur()

    def initier_connexion(self, nombre_de_connexions: int) -> None:
        """
        Pour le nombre de clients passé en paramètre:

        - Crée un client, le connecte et stocke la socket dans la liste ``clients``.
        - Le serveur accepte la connexion du client.
        - Crée et démarre un daemon Thread qui instancie la classe ``RequestHandler``.

        :param nombre_de_connexions: nombre de clients à créer et connecter au serveur.
        """

        for _ in range(nombre_de_connexions):
            client = Client()
            client.connecter()
            self.clients.append(client)
            socket_client, adresse_client = self.serveur.accepter_connexion()
            handler = threading.Thread(
                target=RequestHandler,
                args=(socket_client, adresse_client, socketserver.ThreadingMixIn()))
            handler.daemon = True
            handler.start()

    def test_connexion(self) -> None:
        """
        Crée les clients, les Threads et instancie la classe ``RequestHandler``.

        Pour chaque client, l'instance ajoute dans la liste de la classe ``Messagerie`` le message
        ``(self, "nouveau_joueur", None)``.

        Ferme les connexions côté clients.

        Pour chaque client déconnecté, l'instance ajoute dans la liste de la classe ``Messagerie`` le message
        ``(self, "quitte", None)``.
        """

        nombre_de_connexions = 10
        self.initier_connexion(nombre_de_connexions)
        for _ in range(nombre_de_connexions):
            handler, categorie, message = Messagerie.obtenir()
            self.assertEqual(('nouveau_joueur', None), (categorie, message))
            self.assertIsInstance(handler, RequestHandler)
        for client in self.clients:
            client.fermer_connexion()
        for indice in range(nombre_de_connexions):
            handler, categorie, message = Messagerie.obtenir()
            self.assertEqual(('quitte', None), (categorie, message))
            self.assertIsInstance(handler, RequestHandler)


class ThreadedTCPServerTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions de la classe ``ThreadedTCPServer``.
    """

    def setUp(self) -> None:
        """
        Avant chaque test, instancie ``ThreadedTCPServer`` avec la classe ``SimpleHandler`` en paramètre pour créer un
        serveur.
        Démarre le Thread *Serveur*.
        """

        self.clients: List[Client] = []
        self.serveur: ThreadedTCPServer = ThreadedTCPServer(adresse, classe_gestionnaire=SimpleHandler)
        self.serveur.thread.start()

    def tearDown(self) -> None:
        """
        Après chaque test, ferme les connexions clients et arrête le Thread *Serveur*.
        Réinitialise les variables de la classe ``SimpleHandler``.
        """

        for client in self.clients:
            client.fermer_connexion()
        self.serveur.shutdown()
        self.serveur.thread.join()
        self.serveur.server_close()
        SimpleHandler.effacer()

    def initier_connexion(self, nombre_de_connexions: int) -> None:
        """
        Pour le nombre de clients passé en paramètre,

        - Crée un client, le connecte et stocke la socket dans la liste ``clients``.
        - Le Thread *Serveur* crée un nouveau Thread et instancie ``SimpleHandler`` pour chaque client.

        :param nombre_de_connexions: nombre de clients à créer et à connecter au Thread *Serveur*.
        """

        for _ in range(nombre_de_connexions):
            client = Client()
            client.connecter()
            self.clients.append(client)

    def test_connexions(self) -> None:
        """
        Met l'attribut ``connexion_autorisee`` à True.

        Crée des clients. Le *Serveur* instancie la classe ``SimpleHandler``.
        Synchronise les Thread avec ``barriere``: la barrière est levée après la création de toutes les instances.

        Le nombre de clients est égal à ``nombre_de_connexions``.

        Libère les Threads avec l'évènement ``signal``.
        """

        nombre_de_connexions = 10
        SimpleHandler.barriere = threading.Barrier(nombre_de_connexions + 1)
        self.serveur.connexion_autorisee = True
        self.initier_connexion(nombre_de_connexions)
        SimpleHandler.barriere.wait()
        self.assertEqual(nombre_de_connexions, len(SimpleHandler.clients))
        SimpleHandler.signal.set()
