# -*-coding:Utf-8 -*

"""
Ce module contient les classes d'exception ValidationErreur Quitter
et les classes ValidateurTexte, InterfaceClient, InterfaceServeur.
"""

from typing import Pattern, ClassVar
from socket import socket
import threading
import re
from messagerie import Messagerie, Transmission, ConnectionFermee


class ValidationErreur(BaseException):
    """
    Exception levée quand la saisie de l'utilisateur ne correspond pas au schéma de validation
    """

    pass


class Quitter(BaseException):
    """
    Exception levée quand l'utilisateur saisie 'touche' pour quitter le jeu
    """

    touche: ClassVar[str] = "Q"


class ValidateurTexte:
    """
    Utilisé pour valider la saisie utilisateur
    Elle est basée sur les expressions régulières (module 're')
    - La classe reçoit les paramètres de validation (validation_schema, validation_erreur) avec 'parametrer()'
    - La classe est instanciée avec la saisie à valider en paramètre
    - L'instance retourne True au test 'if instance' si la saisie est valide

    Lève l'exception Quitter quand la saisie contient la chaine 'Quitter.touche'
    Lève l'exception ValidationErreur quand la classe est instanciée sans schéma de validation
    Lève l'exception TypeError quand la classe reçoit un mauvais schéma de validation

    Lorsque la partie est terminée, seule la correspondance avec la chaine 'Quitter.touche' est testée
    """

    validation_schema: ClassVar[Pattern]
    schema_parametre: ClassVar[bool] = False
    validation_erreur: ClassVar[str] = str()
    fin_de_partie: ClassVar[bool] = False

    def __init__(self, saisie: str) -> None:
        """
        A l'instanciation de la classe, teste la saisie avec le schéma de validation

        :param str saisie: saisie utilisateur
        :raises Quitte: si 'saisie' contient 'Quitter.touche'
        :raises ValidationErreur: si la saisie ne correspond pas au schéma, ou s'il n'y a pas schéma
        """

        self.valide = False
        try:
            if Quitter.touche in saisie:
                raise Quitter
        except TypeError:
            pass
        if not self.fin_de_partie:
            try:
                if not self.schema_parametre:
                    raise TypeError
                if self.validation_schema.fullmatch(saisie):
                    self.valide = True
                else:

                    raise ValidationErreur(self.validation_erreur)
            except TypeError:
                raise ValidationErreur("Aucun schéma de validation reçu du serveur")

    @classmethod
    def parametrer(cls, parametre: str, valeur: str) -> None:
        """
        Si le parametre reçu est 'validation_schema', compile l'expression regulière et la stocke
        si le paramètre reçu est 'validation_erreur', stocke la valeur

        :param str parametre: 'validation_schema' ou 'validation_erreur'
        :param str valeur: expression régulière ou message en cas d'erreur de saisie
        :raises TypeError: si parametre contient une autre valeur
        """

        if parametre == 'validation_schema':
            cls.validation_schema = re.compile(valeur)
            cls.schema_parametre = True
        elif parametre == 'validation_erreur':
            cls.validation_erreur = valeur
        else:
            raise TypeError("La catégorie n'est pas définie")

    def __bool__(self) -> bool:
        """
        Lors d'un test 'if instance',

        :return: si la saisie est valide
        :rtype: bool
        """

        return self.valide

    @classmethod
    def effacer(cls) -> None:
        """
        Réinitialise les variables de la classe
        """

        cls.schema_parametre = False
        cls.validation_erreur = str()
        cls.fin_de_partie = False


class InterfaceClient(threading.Thread):
    """
    Crée un thread dédié à la saisie utilisateur
    La saisie est transmise au Main Thread par la Messagerie
    """

    def __init__(self) -> None:
        """
        Instancie le Thread Interface Client
        """

        super().__init__()
        self.name = 'Interface Client'
        self.saisie_suivante = threading.Event()
        self.fin_de_partie = False

    def run(self) -> None:
        """
        Recupère la saisie utilisateur et l'ajoute à la liste Messagerie
        Quand il rencontre une erreur, le Thread transmet l'erreur et s'arrête
        Synchronise le Thread avec MainThread: attend l'évènement 'saisie_suivante' pour relancer la boucle
        """

        while not self.fin_de_partie:
            try:
                saisie = input().upper()
            except EOFError as e:
                Messagerie.ajouter(('erreur', e))
                break
            Messagerie.ajouter(('saisie', saisie))
            self.saisie_suivante.wait()
            self.saisie_suivante.clear()


class InterfaceServeur(threading.Thread, Transmission):
    """
    Crée un thread dédié à l'écoute réseau
    Le message du serveur est transmis au Main Thread par la Messagerie
    """

    def __init__(self, request: socket) -> None:
        """
        Instancie le Thread Interface Serveur
        Hérite de la classe Transmission qui nécessite une socket pour recevoir les messages réseau

        :param socket request: la requête
        """

        super().__init__()
        self.name = 'Interface Serveur'
        self.request = request

    def run(self) -> None:
        """
        Recupère le message du serveur et l'ajoute à la liste Messagerie
        Quand il rencontre une erreur réseau, le Thread transmet l'erreur et s'arrête
        """

        while True:
            try:
                Messagerie.ajouter(self.recevoir())
            except TypeError:
                continue
            except (ConnectionFermee, ConnectionResetError, ConnectionAbortedError, OSError) as e:
                Messagerie.ajouter(('erreur', e))
                break
