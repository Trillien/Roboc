# -*-coding:Utf-8 -*

"""
Ce fichier contient le Client du jeu.
Exécutez-le avec Python pour lancer le jeu.
"""

from typing import Union, Final, Tuple
import socket
from lib.interface_client import InterfaceClient, InterfaceServeur, ValidateurTexte, ValidationErreur, Quitter
from lib.messagerie import Messagerie, Transmission

# Alias de type pour les adresses des clients
Adresse = Tuple[str, int]
# Adresse et port de connexion au serveur
adresse: Final[Adresse] = ('localhost', 12800)

"""
Ouvre une socket et se connecte à ``adresse``
Si la connexion n'aboutit pas, demande si l'utilisateur souhaite se reconnecter:

- s'il accepte, tente une nouvelle connexion.
- s'il refuse, quitte le programme.
"""

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as requete:
    est_connecte: bool = False
    while not est_connecte:
        print("On tente de se connecter au serveur...")
        try:
            requete.connect(adresse)
        except ConnectionRefusedError:
            print("La connexion n'a pas pu être établie avec {}".format(adresse))
            essai: Union[str, None] = None
            while essai not in ['O', 'N', Quitter.touche]:
                essai = input("Voulez-vous réessayer (O/N) ? ").upper()
            if essai in ['N', Quitter.touche]:
                exit()
        else:
            est_connecte = True
            print("Connexion établie avec le serveur.")

    """
    Instanciation et démarrage des Threads:

    - *Main Thread* reçoit les informations des deux autres Threads.
      C'est le seul à envoyer des messages au serveur, c'est le seul à afficher des informations.
    - *Interface Client* écoute les saisies utilisateur et les transmet à *Main Thread*.
    - *Interface Serveur* reçoit les messages du serveur et les transmet à *Main Thread*.

    ``Tranmission`` permet d'envoyer des messages au serveur.
    """

    transmission = Transmission(requete)
    interface_client = InterfaceClient()
    interface_serveur = InterfaceServeur(requete)
    interface_client.start()
    interface_serveur.start()
    print("Tapez " + Quitter.touche + " pour quitter")

    """
    Boucle principale:

    *Main Thread* récupère un message de la liste de la classe ``Messagerie`` qui contient un tuple ``(categorie, message)``.

    Catégories reçues du Serveur (transmis par *Interface Serveur*):

    - ``"affichage"``, affiche le message.
    - ``"validation_schema"`` ou ``"validation_erreur"``, envoie les paramètres à la classe ``ValidateurTexte``.
    - ``"fin"``, change le mode de ``ValidateurTexte``.

    Catégorie reçue de *Interface Client*:

    - ``"saisie"``, instancie ``ValidateurTexte`` pour tester la saisie, et l'envoie au Serveur.

    Catégorie reçue de *Interface Client* ou *Interface Serveur*:

    - ``"erreur"``, affiche le message et quitte la boucle.
    """

    while True:
        try:
            categorie, message = Messagerie.obtenir()
        except (ValueError, TypeError):
            continue
        except KeyboardInterrupt:
            break
        if categorie == 'affichage':
            print(message)
        elif categorie == 'erreur':
            print(message)
            break
        elif categorie in ['validation_schema', 'validation_erreur']:
            try:
                ValidateurTexte.parametrer(categorie, message)
            except TypeError:
                pass
        elif categorie == 'saisie':
            try:
                valide = ValidateurTexte(message)
            except ValidationErreur as e:
                if ValidateurTexte.mode == ValidateurTexte.jeu_en_cours:
                    print(e)
            except Quitter:
                break
            finally:
                interface_client.saisie_suivante.set()

            if ValidateurTexte.mode == ValidateurTexte.jeu_en_cours:
                if valide:
                    transmission.envoyer(('commande', message))
                else:
                    print(ValidateurTexte.validation_erreur)

        elif categorie == 'fin':
            ValidateurTexte.mode = ValidateurTexte.fin_de_partie
            print("Tapez " + Quitter.touche + " pour quitter")

    """
    L'utilisateur a saisie la touche ``Quitter.touche`` ou une erreur s'est produite dans le Thread *Interface Client* ou le
    Thread *Interface Serveur*.

    Le programme quitte la boucle principale et sort le Thread *Interface Client* de sa boucle infinie.
    La connexion au serveur est fermée et le Thread *Interface Serveur* s'arrête.
    """

    interface_client.mode = InterfaceClient.fin_de_partie
    interface_client.saisie_suivante.set()
    interface_client.join()

    print("Fermeture de la connexion")
