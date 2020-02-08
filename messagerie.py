# -*-coding:Utf-8 -*

"""
Ce module contient les classes Transmission et Messagerie.
"""

from typing import Any, List, ClassVar
from socket import socket
import pickle
import threading


class ConnectionFermee(BaseException):
    """
    Exception levée quand le client distant a fermé la connexion
    """

    pass


class Transmission:
    """
    Utilisé pour envoyer et recevoir des messages entre le Client et le Serveur.
    Le message comporte:
    - une entête de longueur fixe LONGUEUR_ENTETE qui indique la taille de l'objet transmis
    - l'objet sérialisé avec 'pickle'

    Lève l'exception TypeError quand l'objet ne peut pas être sérialisé
    Lève l'exception OverflowError quand la taille du message ne peut être contenu dans LONGUEUR_ENTETE
    Lève l'exception ConnectionFermee quand le client distant a fermé la connexion
    Lève l'exception ConnectionResetError quand le client distant a réinitialisé la connexion
    Lève l'exception ConnectionAbortedError quand la socket depuis laquelle le message est reçue est close
    Lève l'exception OSError quand la socket utilisée par la fonction est close

    Idée originale détaillée sur:
    https://pythonprogramming.net/pickle-objects-sockets-tutorial-python-3/

    """

    longueur_entete: ClassVar[int] = 3     # 3 octets = 24 bits

    def __init__(self, request: socket) -> None:
        """
        Stocke la socket,
        nécessaire pour envoyer et recevoir des messages entre Client et Serveur

        :param socket request: connexion client
        """

        self.request = request

    def envoyer(self, objet: Any) -> None:
        """
        Sérialise l'objet avec 'pickle'
        Détermine la taille du message à transmettre et l'indique dans l'entête
        Envoie le message en utilisant la socket

        :param Any objet: objet à transmettre
        :raises TypeError: si l'objet ne peut pas être sérialisé
        :raises OverflowError: si la taille du message ne peut être contenu dans LONGUEUR_ENTETE
        """

        # Lève TypeError si l'objet ne peut pas être sérialisé
        objet_serialise = pickle.dumps(objet)
        longueur = len(objet_serialise)
        # Lève OverflowError si longueur dépasse LONGUEUR_ENTETE
        entete = longueur.to_bytes(length=self.longueur_entete, byteorder='big')
        # Lève ConnectionAbortedError si la socket a été fermée par le destinataire
        try:
            self.request.send(entete + objet_serialise)
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            pass

    def recevoir(self) -> Any:
        """
        Reçoit l'entête de taille LONGUEUR_ENTETE
        Puis reçoit la quantité d'octets indiquée dans l'entête
        Dé-sérialise le message avec 'pickle' et retourne l'objet

        :return: objet reçu
        :rtype: Any
        :raises TypeError: si l'objet ne peut pas être sérialisé
        :raises ConnectionFermee: si le client distant a fermé la connexion
        :raises ConnectionResetError: si le client distant a réinitialisé la connexion
        :raises ConnectionAbortedError: si la socket depuis laquelle le message est reçue est close
        :raises OSError: si la socket utilisée par la fonction est close
        """

        entete = self.request.recv(self.longueur_entete)
        if not entete:
            raise ConnectionFermee
        longueur = int.from_bytes(entete, byteorder='big')
        objet_serialise = self.request.recv(longueur)
        try:
            message = pickle.loads(objet_serialise)
        except (pickle.UnpicklingError, EOFError):
            raise TypeError
        return message


class Messagerie:
    """
    Permet aux différents Threads d'ajouter et de récuperer des messages
    Averti les Threads de l'arrivée d'un message grâce à l'Event 'nouveau_message'
    Les messages sont stockés sur une unique liste 'messages'
    """

    nouveau_message: ClassVar[threading.Condition] = threading.Condition()
    messages: ClassVar[List[Any]] = []

    @classmethod
    def ajouter(cls, message: Any) -> None:
        """
        Utilise un verrou pour accéder à la liste des messages
        Ajoute le message à la liste
        Indique l'arriver d'un message avec 'nouveau_message'

        :param Any message: message à ajouter à la Messagerie
        """

        with cls.nouveau_message:
            cls.messages.append(message)
            cls.nouveau_message.notify()

    @classmethod
    def obtenir(cls) -> Any:
        """
        Utilise un verrou pour accéder à la liste des messages
        Attend l'arriver d'un nouveau message
        Retire le message le plus ancien de la liste

        :return: premier message de la Messagerie
        :rtype: Any
        """

        with cls.nouveau_message:
            while not len(cls.messages):
                cls.nouveau_message.wait()
            return cls.messages.pop(0)

    @classmethod
    def effacer(cls) -> None:
        """
        Réinitialise les variables de la classe
        """

        cls.messages.clear()
