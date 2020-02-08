# -*-coding:Utf-8 -*

"""
Ce module contient les classes TransmissionTest et MessagerieTest
"""

from typing import Optional, ClassVar
from messagerie import Transmission, Messagerie, ConnectionFermee
import socket
import threading
import unittest


class ClientServeur:
    """
    Contient les informations de connexion entre le client et le serveur
    """

    hote: ClassVar[str] = 'localhost'
    port: ClassVar[int] = 12800

    def __init__(self) -> None:
        """
        Définit une socket (client ou serveur)
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class Serveur(ClientServeur):
    """
    Crée un serveur
    """

    def __init__(self) -> None:
        """
        Stocke la socket du client
        """

        super().__init__()
        self.client: Optional[socket.socket] = None

    def demarrer_serveur(self) -> None:
        """
        Démarre le serveur sur l'adresse de connexion
        """

        self.socket.bind((self.hote, self.port))
        self.socket.listen(5)

    def accepter_connexion(self) -> socket.socket:
        """
        Accepte une connexion et stocke les informations du client

        :return: socket du client
        :rtype: socket
        """

        self.client, _ = self.socket.accept()
        return self.client

    def arreter_serveur(self) -> None:
        """
        Si une connexion client existe, ferme cette connexion
        Puis ferme la socket du serveur
        """

        try:
            if self.client:
                self.client.close()
        except AttributeError:
            pass
        self.socket.close()


class Client(ClientServeur):
    """
    Crée un client
    """

    def connecter(self) -> None:
        """
        Etablit une connexion sur l'adresse de connexion
        """

        self.socket.connect((self.hote, self.port))

    def fermer_connexion(self) -> None:
        """
        Ferme la socket du client
        """

        self.socket.close()


class TransmissionTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions de la classe 'Transmission'.
    """

    def setUp(self) -> None:
        """
        Crée un serveur et un client
        Charge une liste d'objet qui pourra être transmis du client au serveur
        """

        self.serveur = Serveur()
        self.client = Client()
        self.liste_objets = [
            None,           # None
            'test',         # Chaine de caractères
            1,              # entier
            True,           # booléen
            {'test': 1},    # dictionnaire
            ['test'],       # liste
            ('test', 1),    # tuple
        ]

    def tearDown(self) -> None:
        """
        Ferme les connexions client et serveur
        """

        self.client.fermer_connexion()
        self.serveur.arreter_serveur()

    def test_emission_trop_gros_objet(self) -> None:
        """
        Crée un objet dont l'entête ne peut pas stocker la taille
        Tente de transmettre l'objet (mais échoue à créer l'entête)
        """

        transmission_client = Transmission(self.client.socket)
        objet = 'a' * (2 ** (transmission_client.longueur_entete * 8))
        with self.assertRaises(OverflowError):
            transmission_client.envoyer(objet)
        del objet

    def test_emission_reception(self) -> None:
        """
        Démarre le serveur puis le client
        Accepte la connexion
        Transmet chaque objet de la liste, puis compare l'objet à transmettre avec l'objet transmis
        """

        self.serveur.demarrer_serveur()
        self.client.connecter()
        socket_serveur = self.serveur.accepter_connexion()
        transmission_client = Transmission(self.client.socket)
        transmission_serveur = Transmission(socket_serveur)
        for objet in self.liste_objets:
            transmission_client.envoyer(objet)
            self.assertEqual(objet, transmission_serveur.recevoir())

    def test_reception_serveur_clos(self) -> None:
        """
        Démarre le serveur puis le client
        Accepte la connexion
        Ferme le serveur
        Tente de recevoir un message
        """

        self.serveur.demarrer_serveur()
        self.client.connecter()
        socket_serveur = self.serveur.accepter_connexion()
        transmission_serveur = Transmission(socket_serveur)
        self.serveur.arreter_serveur()
        with self.assertRaises(OSError):
            transmission_serveur.recevoir()

    def test_reception_client_clos(self) -> None:
        """
        Démarre le serveur puis le client
        Accepte la connexion
        Ferme le client
        Tente de recevoir un message (reçoit une entête vide)
        """

        self.serveur.demarrer_serveur()
        self.client.connecter()
        socket_serveur = self.serveur.accepter_connexion()
        self.client.fermer_connexion()
        transmission_serveur = Transmission(socket_serveur)
        with self.assertRaises(ConnectionFermee):
            transmission_serveur.recevoir()

    def test_reception_mauvais_format(self) -> None:
        """
        Démarre le serveur puis le client
        Accepte la connexion
        Tente de recevoir un message "test" qui n'a pas d'entête
        """

        self.serveur.demarrer_serveur()
        self.client.connecter()
        socket_serveur = self.serveur.accepter_connexion()
        transmission_serveur = Transmission(socket_serveur)
        self.client.socket.send(b"test")
        with self.assertRaises(TypeError):
            transmission_serveur.recevoir()


class MessagerieTest(unittest.TestCase):
    """
    Test case utilisé pour tester les fonctions de la classe 'Messagerie'.
    """

    def tearDown(self) -> None:
        """
        Réinitialise les variables de Messagerie
        """

        Messagerie.effacer()

    def test_ajouter_obtenir(self) -> None:
        """
        Génère une liste d'objet à ajouter à la Messagerie
        Lance un thread pour ajouter les objets, et un thread pour les obtenir
        Compare les deux listes d'objets ajoutés et obtenus
        """

        nombre_objets = 100
        liste_objets_references = [nombre for nombre in range(nombre_objets)]
        liste_objets_obtenus = []

        def ajouter_message() -> None:
            """
            Ajoute les objets de liste_objets_references à la Messagerie
            """

            for objet in liste_objets_references:
                Messagerie.ajouter(objet)
                # print("ajouter " + str(objet))

        def obtenir_message() -> None:
            """
            Stocke les objets récupérés de Messagerie dans liste_objets_obtenus
            """

            for _ in range(nombre_objets):
                liste_objets_obtenus.append(Messagerie.obtenir())
                # print("obtenir " + str(liste_objets_obtenus[-1]))

        recepteur = threading.Thread(target=obtenir_message)
        emetteur = threading.Thread(target=ajouter_message)
        recepteur.start()
        emetteur.start()
        recepteur.join()
        emetteur.join()
        self.assertEqual(liste_objets_references, liste_objets_obtenus)
