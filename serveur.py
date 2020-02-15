# -*-coding:Utf-8 -*

"""
Ce fichier contient le Serveur du jeu.
Exécutez-le avec Python pour lancer le jeu.
"""

from typing import Final
import argparse
from lib.interface_serveur import ThreadedTCPServer, Adresse
from lib.messagerie import Messagerie
from lib.dossier import Dossier
from lib.carte import Carte
from lib.labyrinthe import Labyrinthe


def validateur_port(saisie: str) -> int:
    """
    Valide le port de connexion passer en paramètre à l'appel du programme:

    - Convertis la saisie en nombre
    - Vérifie qu'il est compris entre ``port_mini`` et ``port_maxi``.

    :param saisie: saisie passer en paramètre à l'appel du programme.
    :return: le port de connexion du Serveur validé.
    :raises ArgumentTypeError: si la saisie n'est pas un nombre compris entre ``port_mini`` et ``port_maxi``.
    """

    port_mini, port_maxi = 0, 65535
    message_erreur = "Le port est un nombre compris entre " + str(port_mini) + " et " + str(port_maxi) + "."
    try:
        port = int(saisie)
    except ValueError:
        raise argparse.ArgumentTypeError(message_erreur)
    else:
        if port < port_mini or port > port_maxi:
            raise argparse.ArgumentTypeError(message_erreur)
        return port


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-p", "--port", type=validateur_port, default=12800,
                    help="Le port d'écoute du Serveur.")
args = parser.parse_args()

# Adresse et port de connexion du serveur
adresse: Final[Adresse] = ('localhost', args.port)

# Dossier de recherche des cartes
dossier_des_cartes: Final[str] = "cartes"
# Extension des cartes
extension_des_cartes: Final[str] = ".txt"

# Touche saisie par un client réseau pour commencer la partie de labyrinthe
touche_commencer: Final[str] = 'C'

"""
Initialise la classe ``Carte`` avec:

- la liste des éléments connus pour la lecture d'une carte.
- la Liste des éléments qui font gagner la partie.

Extrait dans ``fichiers`` la liste des cartes du ``dossier_des_cartes``.
Affiche la liste des cartes.
Demande le numéro de la carte qui sera jouée.
Crée le labyrinthe depuis la carte sélectionnée et libère la mémoire de la liste cartes.
"""

Carte.elements_connus = Labyrinthe.get_symboles_connus()
Carte.elements_obligatoires = Labyrinthe.get_symboles_obligatoire()

fichiers = None
try:
    fichiers = Dossier(chemin=dossier_des_cartes, extension=extension_des_cartes, classe=Carte)
except (FileNotFoundError, EOFError, OSError) as e:
    print(e)
    exit()
print("Labyrinthes existants :")
for indice, carte in enumerate(fichiers.noms):
    print("  {} - {}".format(indice + 1, carte))
print()

numero_carte = -1
while numero_carte == -1:
    try:
        numero_carte = int(input("Entrez un numéro de labyrinthe pour commencer à jouer :")) - 1
        assert numero_carte in range(len(fichiers))
    except ValueError:
        print("Vous n'avez pas saisi de nombre")
        numero_carte = -1
        continue
    except AssertionError:
        print("Ce labyrinthe n'existe pas")
        numero_carte = -1
print()

carte_selectionnee = fichiers.contenus[numero_carte]
if not isinstance(carte_selectionnee, Carte):
    exit()
else:
    labyrinthe = Labyrinthe(chaine=carte_selectionnee.contenu, nom=carte_selectionnee.nom)
    del fichiers, carte_selectionnee

    """
    Instanciation et démarrage des Threads:

    - *Main Thread* reçoit les informations des Threads *RequestHandler*. C'est le seul à envoyer des messages aux clients,
      c'est le seul à afficher des informations.
    - *Serveur* écoute le réseau pour accepter de nouvelles connexions.
    - Les Threads *RequestHandler* reçoivent les messages des clients et les transmettent à *Main Thread*.
    """

    with ThreadedTCPServer(adresse) as serveur:
        serveur.connexion_autorisee = labyrinthe.est_ouvert()
        serveur.thread.start()
        print("On attend les Clients sur l'adresse {}.".format(adresse))

        """
        Première boucle avant le début de partie qui autorise de nouveaux joueurs.
        *Main Thread* récupère un message de la liste de la classe ``Messagerie`` qui contient un tuple
        ``(émetteur, categorie, message)``.

        Catégories reçues des Threads *RequestHandler*:

        - ``"nouveau_joueur"``, ajoute un joueur au labyrinthe et transmet le message d'accueil.
        - ``"quitte"``, supprime le joueur du labyrinthe.

        Catégorie reçue des Clients (transmis par les Threads *RequestHandler*):

        - ``"commande"``, quitte la boucle si la saisie du client est ``touche_commencer``.
        """

        while True:
            try:
                emetteur, categorie, message = Messagerie.obtenir()
            except (ValueError, TypeError):
                continue
            if categorie == 'nouveau_joueur':
                labyrinthe.ajouter_joueur(emetteur, emetteur.nom_joueur)
                for _emetteur, categorie, message in labyrinthe.get_datagrammes():
                    _emetteur.envoyer((categorie, message))
                emetteur.envoyer(('validation_schema', r"[" + touche_commencer + "]"))
                emetteur.envoyer(('validation_erreur', "Erreur dans la saisie."))
                emetteur.envoyer(('affichage', "Entrez " + touche_commencer + " pour commencer à jouer :"))
                serveur.connexion_autorisee = labyrinthe.est_ouvert()
                print(emetteur.nom_joueur + " est connecté.")
            elif categorie == 'quitte':
                labyrinthe.effacer_joueur(emetteur)
                print(emetteur.nom_joueur + " a quitté la partie.")
            elif categorie == 'commande':
                if message == touche_commencer:
                    print(emetteur.nom_joueur + " a saisie '" + touche_commencer + "'.")
                    break

        """
        Le Labyrinthe n'admet plus de nouveau joueur.
        Transmet le schéma de validation des commandes et le message d'erreur en cas de mauvaise saisie.
        Transmet le plateau du labyrinthe avec la position des joueurs.
        """

        serveur.connexion_autorisee = False
        print("Début de la partie.")
        labyrinthe.demarrer()
        for _emetteur, categorie, message in labyrinthe.get_datagrammes():
            _emetteur.envoyer((categorie, message))

        """
        Boucle principale:

        *Main Thread* récupère un message de la liste de la classe ``Messagerie`` qui contient un tuple
        ``(émetteur, categorie, message)``.

        Catégorie reçue des Threads *RequestHandler*:
        - ``"quitte"``, supprime le joueur du labyrinthe, informe les autres joueurs et renvoie le plateau.

        Catégorie reçue des Clients (transmis par les Threads *RequestHandler*):
        - ``"commande"``, ajoute les commandes au joueur, renvoie la liste des commandes au client réseau puis joue les
          commandes des joueurs à tour de rôle jusqu'à leur épuisement.
        """

        while labyrinthe.mode < Labyrinthe.fin_de_partie:
            try:
                emetteur, categorie, message = Messagerie.obtenir()
            except (ValueError, TypeError):
                continue
            if categorie == 'quitte':
                labyrinthe.effacer_joueur(emetteur)
                for _emetteur, categorie, message in labyrinthe.get_datagrammes():
                    _emetteur.envoyer((categorie, message))
                print(emetteur.nom_joueur + " a quitté la partie.")

            elif categorie == 'commande':
                commandes = labyrinthe.ajouter_commande(emetteur, message)
                print(emetteur.nom_joueur + " a saisie '" + message + "'.")
                labyrinthe.jouer()
                for _emetteur, categorie, message in labyrinthe.get_datagrammes():
                    _emetteur.envoyer((categorie, message))

        """
        Le programme quitte la boucle principale:

        - un joueur a atteint une sortie.
        - ou, après le départ d'un joueur, le nombre de joueur en lice est passé à 1 ou moins.

        Transmet à chaque joueur le vainqueur de la partie et envoie ``"fin"`` aux clients réseau pour se déconnecter du
        serveur.

        Le Thread *Serveur* n'accepte plus de connexion et attend que les Thread *RequestHandler* se terminent pour s'arrêter.
        """

        print("Fin de la partie.")
        labyrinthe.terminer()
        for _emetteur, categorie, message in labyrinthe.get_datagrammes():
            _emetteur.envoyer((categorie, message))
        print("Fermeture de la connexion")
        serveur.shutdown()
        serveur.thread.join()
