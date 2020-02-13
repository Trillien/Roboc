# -*-coding:Utf-8 -*

"""
Ce module contient les classes d'exception ``ValidationErreur``, ``Quitter`` et les classes ``ValidateurTexte``,
``InterfaceClient``, ``InterfaceServeur``.
"""

from typing import Pattern, ClassVar, Final
from socket import socket
import threading
import re
from lib.messagerie import Messagerie, Transmission, ConnectionFermee


class ValidationErreur(BaseException):
    """
    Exception levée quand la saisie de l'utilisateur ne correspond pas au schéma de validation.
    """

    pass


class Quitter(BaseException):
    """
    Exception levée quand l'utilisateur saisie ``touche`` pour quitter le jeu.
    """

    touche: ClassVar[str] = "Q"


class ValidateurTexte:
    """
    Utilisé pour valider la saisie utilisateur.
    Elle est basée sur les expressions régulières.

    - La classe reçoit les paramètres de validation ``(validation_schema, validation_erreur)``.
    - La classe est instanciée avec la saisie à valider en paramètre.
    - L'instance retourne True au test '*if instance*' si la saisie est valide.

    Lorsque la partie est terminée, seule la correspondance avec la chaîne ``Quitter.touche`` est testée.

    :param saisie: saisie utilisateur.
    :raises Quitter: si ``saisie`` contient ``Quitter.touche``.
    :raises ValidationErreur: si ``validation_schema`` n'est pas défini.
    """

    validation_schema: ClassVar[Pattern[str]]
    schema_parametre: ClassVar[bool] = False
    validation_erreur: ClassVar[str] = str()
    jeu_en_cours: Final[int] = 1
    fin_de_partie: Final[int] = 2
    mode: ClassVar[int] = jeu_en_cours

    def __init__(self, saisie: str) -> None:
        """
        A l'instanciation de la classe, teste la saisie avec le schéma de validation.

        :param saisie: saisie utilisateur.
        :raises Quitter: si ``saisie`` contient ``Quitter.touche``.
        :raises ValidationErreur: si ``validation_schema`` n'est pas défini.
        """

        self.valide = False
        try:
            if Quitter.touche in saisie:
                raise Quitter
        except TypeError:
            pass
        if self.mode == self.jeu_en_cours:
            try:
                if not self.schema_parametre:
                    raise TypeError
                if self.validation_schema.fullmatch(saisie):
                    self.valide = True
            except TypeError:
                raise ValidationErreur("Aucun schéma de validation reçu du serveur")

    @classmethod
    def parametrer(cls, parametre: str, valeur: str) -> None:
        """
        Si le paramètre reçu est ``validation_schema``, compile l'expression regulière et la stocke.
        Si le paramètre reçu est ``validation_erreur``, stocke la valeur.

        :param parametre: ``validation_schema`` ou ``validation_erreur``.
        :param valeur: expression régulière ou message en cas d'erreur de saisie.
        :raises TypeError: si ``parametre`` contient une autre valeur.
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
        Lors d'un test '*if instance*',

        :return: True si la saisie est valide. False sinon.
        """

        return self.valide

    @classmethod
    def effacer(cls) -> None:
        """
        Réinitialise les variables de la classe ``ValidateurTexte``.
        """

        cls.schema_parametre = False
        cls.validation_erreur = str()
        cls.mode = cls.jeu_en_cours


class InterfaceClient(threading.Thread):
    """
    Crée un Thread dédié à la saisie utilisateur.
    La saisie est transmise au *Main Thread* par la classe ``Messagerie``.
    """

    jeu_en_cours: Final[int] = 1
    fin_de_partie: Final[int] = 2

    def __init__(self) -> None:
        """
        Instancie le Thread *Interface Client*.
        """

        super().__init__()
        self.name = 'Interface Client'
        self.saisie_suivante = threading.Event()
        self.mode = self.jeu_en_cours

    def run(self) -> None:
        """
        Recupère la saisie utilisateur et l'ajoute à la liste de la classe ``Messagerie``.
        Quand il rencontre une erreur, le Thread transmet l'erreur et s'arrête.
        Synchronise le Thread avec *Main Thread* : attend l'évènement ``saisie_suivante`` pour relancer la boucle.
        """

        while self.mode < self.fin_de_partie:
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
    Crée un Thread dédié à l'écoute réseau.
    Le message du serveur est transmis au *Main Thread* par la classe ``Messagerie``.

    :param request: la requête.
    """

    def __init__(self, request: socket) -> None:
        """
        Instancie le Thread *Interface Serveur*.
        Hérite de la classe ``Transmission`` qui nécessite une socket pour recevoir les messages réseau.

        :param request: la requête.
        """

        super().__init__()
        self.name = 'Interface Serveur'
        self.request = request

    def run(self) -> None:
        """
        Recupère le message du serveur et l'ajoute à la liste de la classe ``Messagerie``.
        Quand il rencontre une erreur réseau, le Thread transmet l'erreur et s'arrête.
        """

        while True:
            try:
                Messagerie.ajouter(self.recevoir())
            except TypeError:
                continue
            except (ConnectionFermee, ConnectionResetError, ConnectionAbortedError, OSError) as e:
                Messagerie.ajouter(('erreur', e))
                break
