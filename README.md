# Roboc
![Jeu du labyrinthe](./docs/screenshots/01%20-%20Labyrinth%20game.png "Jeu du labyrinthe")

Code d'un jeu de labyrinthe pour le cours "Apprenez à programmer en Python" d'OpenClassrooms.

## Prérequis
Python 3.8

## Règle du jeu
Le joueur doit atteindre le premier la sortie du labyrinthe

## Symboles du labyrinthe
### 1. Eléments de la grille du labyrinthe
Symbole|Elément|Caractéristiques
:---:|---|---
O|Mur|Le joueur ne peut pas le traverser. Il peut le percer.
.|Porte|Le joueur peut la traverser. Il peut la murer.
U|Sortie|Le joueur doit l'atteindre pour gagner la partie.

Exemple de grille de labyrinthe:
```
OOOOOOOOOO
O O    O O
O . OO   O
O O O    O
O OOOO O.O
O O O    U
O OOOOOO.O
O O      O
O O OOOOOO
O . O    O
OOOOOOOOOO
```

### 2. Autres symboles
Symbole|Elément|Caractéristiques
:---:|---|---
X|Joueur|C'est vous !
x|Adversaire|Un autre joueur

Exemple de grille de labyrinthe avec la position de 5 joueurs :
```
OOOOOOOOOO
O O    O O
O . OOx  O
O O Ox   O
O OOOO O.O
O O O    U
O OOOOOO.O
O O x    O
O O OOOOOO
O . O  XxO
OOOOOOOOOO
```

## Contrôles
Touche|Définition|Exemple de saisie
:---:|---|---
N|Se déplacer vers le Nord|'N' effectue un déplacement vers le Nord
S|Se déplacer vers le Sud|'S1' effectue un déplacement vers le Sud
E|Se déplacer vers l'Est|'E13' effectue 13 déplacements vers l'Est
O|Se déplacer vers l'Ouest|'O5' effectue 5 déplacements vers l'Ouest
P|Percer un mur|'PN' perce le mur juste au Nord du joueur
M|Murer une porte|'ME' mure la porte juste à l'Est du joueur
C|Commencer une partie|'C' empêche la connexion de nouveau joueur et débute la partie
Q|Quitter le jeu|'Q' quitte la partie et ferme le client

Exemple de saisie du joueur : "N5MEO13PO"
```
C'est à Joueur 1 de jouer
N5MEO13PO
Commandes :N N N N N ME O O O O O O O O O O O O O PO
```

## Début d'une partie
Les joueurs utilisent une application Client pour se connecter à un Serveur.

### 1. Démarrer le serveur
Démarrer le serveur en tapant *serveur.py* dans une console.
```
serveur.py
```
Le serveur liste les cartes des labyrinthes disponibles dans le dossier *cartes*.
Entrer le numéro de la carte pour charger le labyrinthe.
```
Labyrinthes existants :
  1 - base
  2 - facile
  3 - prison
  4 - sans_bord

Entrez un numéro de labyrinthe pour commencer à jouer :
```
Le labyrinthe ouvre une socket réseau et attend les clients.
```
On attend les clients.
```
### 2. Connecter les clients
Chaque démarre son client en tapant *client.py* dans une console.
```
client.py
```
Le client se connecte au serveur et affiche la carte du labyrinthe.
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
### 3. Le client n'affiche pas de message de bienvenue
Chaque carte de labyrinthe admet un nombre limité de clients. Lorsque ce nombre est atteint, les nouveaux clients sont rejetés par le serveur.
```
On tente de se connecter au serveur...
Connexion établie avec le serveur.
Tapez Q pour quitter
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
Pour générer la documentation, dans le dossier ``./docs`` taper les commandes suivantes :
```
pip install Sphinx
pip install sphinx-rtd-theme
make clean
make html
```
