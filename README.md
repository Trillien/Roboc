# Roboc
![Jeu du labyrinthe](./docs/screenshots/01%20-%20Labyrinth%20game.png "Jeu du labyrinthe")

Coder un jeu de labyrinthe en réseau pour le cours "Apprenez à programmer en Python" d'OpenClassrooms.

## Prérequis
Python 3.8

## Règle du jeu
Le joueur doit atteindre le premier la sortie du labyrinthe.

## Symboles du labyrinthe
### 1. Eléments de la grille du labyrinthe
Symbole|Elément|Détails
:---:|---|---
O|Mur|Le joueur ne peut pas le traverser. Il peut le percer.
.|Porte|Le joueur peut la traverser. Il peut la murer.
U|Sortie|Le joueur doit l'atteindre pour gagner la partie.

>**Exemple** - Grille de labyrinthe :
>```
>OOOOOOOOOO
>O O    O O
>O . OO   O
>O O O    O
>O OOOO O.O
>O O O    U
>O OOOOOO.O
>O O      O
>O O OOOOOO
>O . O    O
>OOOOOOOOOO
>```

### 2. Joueur et Adversaires
Symbole|Elément|Détails
:---:|---|---
X|Joueur|C'est vous !
x|Adversaire|Un autre joueur

>**Exemple** - Grille de labyrinthe avec les positions de 5 joueurs :
>```
>OOOOOOOOOO
>O O    O O
>O . OOx  O
>O O Ox   O
>O OOOO O.O
>O O O    U
>O OOOOOO.O
>O O x    O
>O O OOOOOO
>O . O  XxO
>OOOOOOOOOO
>```

## Contrôles
Touche|Définition|Détails
:---:|---|---
N|Se déplacer vers le Nord|'N' effectue un déplacement vers le Nord
S|Se déplacer vers le Sud|'S1' effectue un déplacement vers le Sud
E|Se déplacer vers l'Est|'E13' effectue 13 déplacements vers l'Est
O|Se déplacer vers l'Ouest|'O5' effectue 5 déplacements vers l'Ouest
P|Percer un mur|'PN' perce le mur juste au Nord du joueur
M|Murer une porte|'ME' mure la porte juste à l'Est du joueur
C|Commencer une partie|'C' empêche la connexion de nouveau joueur et débute la partie
Q|Quitter le jeu|'Q' quitte la partie et ferme le Client

>**Exemple** - Saisie du joueur : "N5MEO13PO"
>```
>C'est à Joueur 1 de jouer
>N5MEO13PO
>Commandes :N N N N N ME O O O O O O O O O O O O O PO
>```


>**Remarque** - Si la saisie est invalide, un message d'erreur s'affiche.
>```
>C'est à Joueur 1 de jouer
>F18
>Cette saisie n'est pas valide !
>```

## Début d'une partie

### 1. Démarrer le Serveur
Démarrer le Serveur en tapant *serveur.py* dans une console.
```
serveur.py
```
Le Serveur liste les cartes des labyrinthes disponibles dans le dossier *cartes*.
```
Labyrinthes existants :
  1 - base
  2 - facile
  3 - prison
  4 - sans_bord

Entrez un numéro de labyrinthe pour commencer à jouer :
```

Entrer le numéro de la carte pour charger le labyrinthe.
Le Serveur ouvre une socket réseau et écoute les connexions entrantes sur ``localhost:12800``.
```
On attend les Clients sur l'adresse ('localhost', 12800).
```

>**Remarque** - Le port d'écoute du Serveur peut être personnalisé avec le paramètre ``-p`` ou ``--port`` à l'appel du
>programme.
>```
>serveur.py -p 9999
>```

### 2. Connecter les Clients
Chaque démarre son Client en tapant *client.py* dans une console.
```
client.py
```

>**Remarque** - L'adresse et le port de connexion du Client peuvent être personnalisés avec les paramètres ``-a`` et ``-p``
>(ou ``--adresse`` et ``--port``) à l'appel du programme.
>```
>client.py -a 192.168.0.15 -p 9999
>```

Le Client se connecte au Serveur et affiche la carte du labyrinthe.
```
On tente de se connecter au serveur...
Connexion établie avec le serveur.
Tapez Q pour quitter

Bienvenue, Joueur 1.
Vous jouez sur le labyrinthe 'base'
OOOO
O  O
O  U
OOOO

Entrez C pour commencer à jouer :
```
Lorsque tous les joueurs sont connectés, un des joueurs saisit 'C' pour commencer la partie.
```
La partie commence! Vous êtes 2 joueurs
N - Se déplacer vers le Nord - Usage: N[0-99]
S - Se déplacer vers le Sud - Usage: S[0-99]
E - Se déplacer vers l'Est - Usage: E[0-99]
O - Se déplacer vers l'Ouest - Usage: O[0-99]
M - Murer un obstacle - Usage: M<NSEO>
P - Percer un obstacle - Usage: P<NSEO>
OOOO
O XO
Ox U
OOOO
```
>**Remarque** - Chaque carte de labyrinthe admet un nombre limité de Clients. Lorsque ce nombre est atteint, les nouveaux
>Clients sont rejetés par le Serveur.
>```
>On tente de se connecter au serveur...
>Connexion établie avec le serveur.
>Tapez Q pour quitter
>```

### 3. Premier tour de jeu
A tout moment du jeu, les joueurs peuvent saisir des contrôles. A chaque tour, le premier contrôle saisi est utilisé pour
déplacer le joueur ou transformer un élément de la grille.

>**Remarque** - Si le contrôle induit une action interdite (par exemple, traverser un Mur), un message d'erreur est affiché.
>Le contrôle est ignoré et le contrôle suivant est utilisé pour jouer le tour.
>```
>C'est à Joueur-1 de jouer
>ES
>Commandes :E S
>Vous ne pouvez pas traverser le mur !
>```

Pendant le jeu, le Serveur affiche l'activité des joueurs :
```
Joueur-1 est connecté.
Joueur-2 est connecté.
Joueur-3 est connecté.
Joueur-4 est connecté.
Joueur-1 a saisie 'C'.
Début de la partie.
Joueur-2 a saisie 'O'.
Joueur-4 a saisie 'E15'.
Joueur-4 a quitté la partie.
```

## Fonctionalités


## Test du code
### 1. flake8
Pour vérifier le style du code avec **flake8**, dans le dossier racine ``./`` taper les commandes :
```
pip install flake8
flake8 . --max-line-length=127
```

### 2. mypy
Pour vérifier les types (type checking) avec **mypy**, dans le dossier racine ``./`` taper les commandes :
```
pip install mypy
mypy . --strict
```

### 3. pytest ou unittest
Pour jouer les tests unitaires avec **unittest**, dans le dossier racine ``./`` taper la commande :
```
python -m unittest
```
Pour jouer les tests unitaires avec **pytest**, dans le dossier racine ``./`` taper les commandes :
```
pip install pytest
pytest
```

## Documentation
[Documentation](./docs/_build/html/index.html)

Pour générer la documentation, dans le dossier ``./docs`` taper les commandes suivantes :
```
pip install Sphinx
pip install sphinx-rtd-theme
make clean
make html
```
