# -*-coding:Utf-8 -*

"""
Ce fichier contient le serveur du jeu.
Exécutez-le avec Python pour lancer le jeu.
"""

from typing import Final
from interface_serveur import ThreadedTCPServer, Adresse
from messagerie import Messagerie
from dossier import Dossier
from carte import Carte
from labyrinthe import Labyrinthe

# Adresse et port de connexion du serveur
adresse: Final[Adresse] = ('localhost', 12800)

# Dossier de recherche des cartes
dossier_des_cartes: Final[str] = "cartes"
# Extension des cartes
extension_des_cartes: Final[str] = ".txt"

# Touche saisie par un client réseau pour commencer la partie de labyrinthe
touche_commencer: Final[str] = 'C'

"""
Initialise la classe 'Carte' avec
- la liste des éléments connus pour la lecture d'une carte
- la Liste des éléments qui font gagner la partie
Extrait dans 'fichiers' la liste des cartes du 'dossier_des_cartes'
Affiche la liste des cartes
Demande le numéro de la carte qui sera jouée
Crée le labyrinthe depuis la carte sélectionnée et libère la mémoire de la liste cartes
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
    - Main Thread reçoit les informations des Threads 'RequestHandler'.
      C'est le seul à envoyer des messages aux clients, c'est le seul à afficher des informations
    - Serveur écoute le réseau pour accepter de nouvelles connexions
    - Les Threads 'RequestHandler' reçoivent les messages des clients et les transmettent à Main Thread
    """

    with ThreadedTCPServer(adresse) as serveur:
        serveur.connexion_autorisee = labyrinthe.est_ouvert()
        serveur.thread.start()
        print("On attend les clients.")

        """
        Première boucle avant le début de partie qui autorise de nouveaux joueurs:
        Main Thread récupère un message de la liste Messagerie qui contient un tuple (émetteur, categorie, message)
    
        Categories reçues des Threads 'RequestHandler':
        - 'nouveau_joueur', ajoute un joueur au labyrinthe et transmet le message d'accueil
        - 'quitte', supprime le joueur du labyrinthe  
        
        Categorie reçue des Clients (transmis par les Threads 'RequestHandler'):
        - 'commande', quitte la boucle si la saisie du client est 'touche_commencer'
        """

        while True:
            try:
                emetteur, categorie, message = Messagerie.obtenir()
            except (ValueError, TypeError):
                continue
            if categorie == 'nouveau_joueur':
                for _emetteur, categorie, message in labyrinthe.accueillir(emetteur, emetteur.nom_joueur):
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
        Transmet le schéma de validation des commandes et le message d'erreur en cas de mauvaise saisie
        Transmet le plateau du labyrinthe avec la position des joueurs
        """

        serveur.connexion_autorisee = False
        print("Début de la partie.")
        for _emetteur in labyrinthe.dict_client_joueur:
            _emetteur.envoyer(('validation_schema', Labyrinthe.get_validation_controle()))
            _emetteur.envoyer(('validation_erreur', "Cette saisie n'est pas valide !"))
        for _emetteur, categorie, message in labyrinthe.demarrer():
            _emetteur.envoyer((categorie, message))

        """
        Boucle principale:
        Main Thread récupère un message de la liste Messagerie qui contient un tuple (émetteur, categorie, message)
    
        Categorie reçue des Threads 'RequestHandler':
        - 'quitte', supprime le joueur du labyrinthe, informe les autres joueurs et renvoie le plateau
        
        Categorie reçue des Clients (transmis par les Threads 'RequestHandler'):
        - 'commande', ajoute les commandes au joueur, renvoie la liste des commandes au client réseau
          puis joue les commandes des joueurs à tour de rôle jusqu'à leur épuisement        
        """

        while labyrinthe.mode < Labyrinthe.fin_de_partie:
            try:
                emetteur, categorie, message = Messagerie.obtenir()
            except (ValueError, TypeError):
                continue
            if categorie == 'quitte':
                labyrinthe.effacer_joueur(emetteur)
                for _emetteur, categorie, message in labyrinthe.afficher_jeu():
                    _emetteur.envoyer(('affichage', emetteur.nom_joueur + " a quitté la partie."))
                    _emetteur.envoyer((categorie, message))
                print(emetteur.nom_joueur + " a quitté la partie.")

            elif categorie == 'commande':
                commandes = labyrinthe.ajouter_commande(emetteur, message)
                if commandes:
                    emetteur.envoyer(('affichage', "Commandes :" + ' '.join(commandes)))
                    print(emetteur.nom_joueur + " a transmis une saisie. Liste des commandes :" + ' '.join(commandes))
                    for _emetteur, categorie, message in labyrinthe.jouer():
                        _emetteur.envoyer((categorie, message))

        """
        Le programme quitte la boucle principale:
        - un joueur a atteint une sortie
        - ou, après le départ d'un joueur, le nombre de joueur en lice est passé à 1 ou moins

        Transmet à chaque joueur le vainqueur de la partie
        et envoie 'fin' aux clients réseau pour se déconnecter du serveur
        
        Le Thread Serveur n'accepte plus de connexion
        et attend que les Thread 'RequestHandler' se terminent pour s'arrêter
        """

        print("Fin de la partie.")
        for _emetteur, categorie, message in labyrinthe.terminer():
            _emetteur.envoyer((categorie, message))
            _emetteur.envoyer(("fin", None))

        print("Fermeture de la connexion")
        serveur.shutdown()
        serveur.thread.join()
