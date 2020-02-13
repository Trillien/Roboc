# -*-coding:Utf-8 -*

"""
Ce module contient la classe ``Carte``.
"""

from typing import Set, Optional, ClassVar


class Carte:
    """
    Objet de transition entre un ``Dossier`` et un ``labyrinthe``.

    La classe ``Carte``:

    - extrait le contenu du fichier désigné par ``chemin``
    - valide le contenu de ce fichier en vérifier la présence des caractères ``elements_connus`` et ``elements_obligatoires``

    :param chemin: chemin d'accès au fichier contenant la carte.
    :param nom: identifie la carte.
    """

    elements_connus: ClassVar[Set[str]] = set()
    elements_obligatoires: ClassVar[Set[str]] = set()

    def __init__(self, chemin: str, nom: Optional[str] = None) -> None:
        """
        Instancie une carte.

        ``contenu`` est la chaîne de caractère extraite du fichier. ``est_valide`` est à True si le fichier est valide, False
        sinon.

        :param chemin: chemin d'accès au fichier contenant la carte.
        :param nom: identifie la carte.
        """

        self.contenu = str()
        self.nom = nom
        self.est_valide = False

        self.extraire(chemin)
        self.verifier_contenu()

    def extraire(self, chemin: str) -> None:
        """
        Extrait le contenu du fichier défini par ``chemin`` et le stocke dans ``contenu``.

        :param chemin: chemin d'accès au fichier contenant la carte.
        """

        with open(chemin, "r") as fichier:
            try:
                self.contenu = fichier.read()
            except UnicodeDecodeError:
                pass

    def verifier_contenu(self) -> None:
        """
        Valide le contenu en vérifiant

        - la présence des ``elements_obligatoires``.
        - l'absence de caractère autres que les ``elements_connus``.
        """

        caracteres = str()
        for ligne in self.contenu.splitlines():
            caracteres += ligne
        try:
            for element_obligatoire in self.elements_obligatoires:
                if element_obligatoire not in caracteres:
                    raise ValueError
            for caractere in caracteres:
                if caractere not in self.elements_connus:
                    raise ValueError
        except ValueError:
            self.est_valide = False
        else:
            self.est_valide = True

    def __bool__(self) -> bool:
        """
        Lors d'un test '*if Carte*', le test porte sur la validation du contenu du fichier.

        :return: si la carte est valide.
        """

        return self.est_valide
