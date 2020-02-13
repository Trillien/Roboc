# -*-coding:Utf-8 -*

"""
Ce module contient la classe ``Dossier``.
"""

from typing import List, Optional
import os


class Dossier:
    """
    Utilisé pour lister les cartes de labyrinthe dans un dossier.

    La classe ``Dossier``:

    - liste les fichiers contenus dans un dossier.
    - filtre les fichiers sur l'extension.
    - instancie la classe selon ``classe(chemin=chemin_de_fichier, nom=nom_de_fichier)`` et filtre les fichiers selon le test
      '*if objet*', ``objet`` étant une instance de la classe.

    :param chemin: chemin d'un fichier ou d'un dossier.
    :param extension: filtre sur l'extension des fichiers.
    :param classe: classe pour la validation du contenu d'un fichier.
    """

    def __init__(self, chemin: str = '.',
                 extension: str = '.txt',
                 classe: Optional[type] = None) -> None:
        """
        La classe ``Dossier`` stocke les ``chemins``, les ``noms``, les ``extensions``, les ``tailles`` et les ``contenus``
        des fichiers parcourus.

        ``contenus`` liste les instances de ``classe`` suite à l'appel
        ``classe(chemin=chemin_de_fichier, nom=nom_de_fichier)``.

        Si le chemin d'un dossier indiqué, le dossier est parcouru à l'instanciation de la classe. Si l'extension est indiqué,
        les fichiers sont filtrés sur l'extension. Si une classe est indiquée, les fichiers sont filtrés sur le test
        '*if classe*'.

        :param chemin: chemin d'un fichier ou d'un dossier.
        :param extension: filtre sur l'extension des fichiers.
        :param classe: classe pour la validation du contenu d'un fichier.
        """

        self.chemins: List[str] = []
        self.noms: List[str] = []
        self.extensions: List[str] = []
        self.tailles: List[int] = []
        self.contenus: List[Optional[type]] = []

        if chemin:
            self.ajouter(chemin, classe)
            if extension:
                self.filtrer_extension(extension)
            self.filtrer_fichiers_non_vide()
            if classe:
                self.filtrer_contenus()

    def __ajouter(self, chemin: str, classe: Optional[type] = None) -> None:
        """
        Extrait les informations du fichier désigné par ``chemin`` et les stocke dans les listes.
        Si une classe est passée en paramètre, l'instancie et stocke l'objet dans ``contenus``.

        :param  chemin: chemin d'un fichier ou d'un dossier.
        :param classe: classe pour la validation du contenu d'un fichier.
        """

        nom, extension = os.path.splitext(os.path.basename(chemin))
        self.chemins.append(chemin)
        self.noms.append(nom)
        self.extensions.append(extension)
        self.tailles.append(os.path.getsize(chemin))
        if not classe:
            self.contenus.append(None)
        else:
            self.contenus.append(classe(chemin=chemin, nom=nom))

    def __enlever(self, liste_indices: List[int]) -> None:
        """
        Pour chaque indice de la liste reçue,
        supprime les éléments des listes ``chemins``, ``noms``, ``extensions``, ``tailles``, ``contenus``.

        :param liste_indices: indices des éléments à supprimer des listes.
        """

        for indice in reversed(liste_indices):
            del self.chemins[indice]
            del self.noms[indice]
            del self.extensions[indice]
            del self.tailles[indice]
            del self.contenus[indice]

    def ajouter(self, chemin: str, classe: Optional[type] = None) -> None:
        """
        Teste si le chemin indiqué existe.
        Détermine si le chemin indiqué est celui d'un dossier ou d'un fichier.
        Parcourt les fichiers du dossier indiqué, et transmet le chemin de chaque fichier à ``_ajouter()``.

        :param chemin: chemin d'un fichier ou d'un dossier.
        :param classe: classe pour la validation du contenu d'un fichier.
        :raises FileNotFoundError: si le chemin n'existe pas.
        :raises OSError: si le chemin n'est ni un dossier ni un fichier.
        """

        if not os.path.exists(chemin):
            raise FileNotFoundError("Le chemin <{0}> n'existe pas".format(chemin))
        if os.path.isdir(chemin):
            for racine, _, fichiers in os.walk(chemin):
                for fichier in fichiers:
                    self.__ajouter(os.path.join(racine, fichier), classe)
        elif os.path.isfile(chemin):
            self.__ajouter(chemin, classe)
        else:
            raise OSError("Le chemin <{0}> n'est pas accessible".format(chemin))

    def filtrer_extension(self, extension: str) -> None:
        """
        Pour chaque fichier, teste si l'extension correspond à celle passée en paramètre.
        Si ce n'est pas le cas, l'indice du fichier est transmis à ``_enlever()``.

        :param extension: filtre sur l'extension des fichiers.
        :raises FileNotFoundError: si aucun fichier n'est valide.
        """

        liste_indices = []
        for indice, ext in enumerate(self.extensions):
            if ext != extension:
                liste_indices.append(indice)
        if liste_indices:
            self.__enlever(liste_indices)
        if not len(self):
            raise FileNotFoundError("Aucun fichier avec l'extension <{0}> n'a été trouvé".format(extension))

    def filtrer_fichiers_non_vide(self) -> None:
        """
        Pour chaque fichier, teste si la taille est nulle.
        Si c'est le cas, l'indice du fichier est transmis à ``_enlever()``.

        :raises EOFError: si aucun fichier non-vide n'a été trouvé.
        """

        liste_indices = []
        for indice, taille in enumerate(self.tailles):
            if not taille:
                liste_indices.append(indice)
        if liste_indices:
            self.__enlever(liste_indices)
        if not len(self):
            raise EOFError("Aucun fichier non-vide n'a été trouvé")

    def filtrer_contenus(self) -> None:
        """
        Pour chaque fichier, teste si le contenu (c'est à dire l'objet de ``classe`` instanciée) retourne True.
        Si ce n'est pas le cas, l'indice du fichier est transmis à ``_enlever()```.

        :raises FileNotFoundError: si aucun fichier n'est valide.
        """

        liste_indices = []
        for indice, contenu in enumerate(self.contenus):
            if not contenu:
                liste_indices.append(indice)
        if liste_indices:
            self.__enlever(liste_indices)
        if not len(self):
            raise FileNotFoundError("Aucun fichier n'a de contenu valide")

    def __len__(self) -> int:
        """
        ``len(dossier)`` retourne le nombre de fichiers filtrés.

        :return: nombre de fichiers valides contenus dans chemin.
        """

        return len(self.noms)
