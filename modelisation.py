"""Simulation pédagogique d'un écosystème forestier en quatre zones.

Les paramètres des zones illustrent des facteurs abiotiques (humidité,
fertilité, lumière), des interactions biotiques (maladie, compétition) et
un facteur anthropique (fragmentation de l'habitat).
"""

import random
import tkinter as tk
from dataclasses import dataclass


TAILLE = 12
# La succession écologique commence sur un sol nu.
DENSITE_ARBRES = 0.0

CASE_VIDE = 0
ARBRE_SAIN = 1
ARBRE_MALADE = 2
RIVIERE = 3
ROCHER = 4
ARBRE_MORT = 5


@dataclass(frozen=True)
class ContexteEcologique:
    nom: str
    description: str
    humidite: float
    fertilite: float
    pression_maladie: float
    mortalite: float
    regeneration: float
    couleur_zone: str
    lumiere: float = 1.0
    competition: float = 0.04


ZONES = (
    ContexteEcologique("Forêt humide", "Humidité élevée et sol fertile", .90, .85, .30, .03, .22, "#d5f5e3", .80, .03),
    ContexteEcologique("Milieu sec", "Faible pluie : facteur limitant", .25, .45, .10, .18, .06, "#fdebd0", 1.00, .07),
    ContexteEcologique("Montagne", "Froid, relief et croissance lente", .45, .55, .08, .11, .08, "#d6eaf8", .45, .05),
    ContexteEcologique("Zone anthropisée", "Fragmentation et perturbations humaines", .50, .35, .24, .14, .04, "#f5eef8", .70, .10),
)


def zone_de_case(ligne: int, colonne: int, taille: int) -> int:
    """Retourne le quadrant écologique d'une case."""
    milieu = taille // 2
    return (0 if ligne < milieu else 2) + (0 if colonne < milieu else 1)


def creer_damier(taille: int, densite: float) -> list[list[int]]:
    """Crée un damier avec des arbres répartis aléatoirement."""
    return [
        [ARBRE_SAIN if random.random() < densite else CASE_VIDE for _ in range(taille)]
        for _ in range(taille)
    ]


def ajouter_decors(damier: list[list[int]], nombre_rochers: int = 8) -> None:
    """Ajoute une rivière centrale et des rochers sur les cases vides."""
    taille = len(damier)
    colonne_riviere = taille // 2
    for ligne in range(taille):
        for colonne in range(max(0, colonne_riviere - 1), min(taille, colonne_riviere + 1)):
            damier[ligne][colonne] = RIVIERE

    cases_vides = [
        (ligne, colonne)
        for ligne in range(taille)
        for colonne in range(taille)
        if damier[ligne][colonne] == CASE_VIDE
    ]
    for ligne, colonne in random.sample(cases_vides, min(nombre_rochers, len(cases_vides))):
        damier[ligne][colonne] = ROCHER


def propager_maladie(
    damier: list[list[int]],
    contexts: tuple[ContexteEcologique, ...] = ZONES,
) -> list[list[int]]:
    """Fait progresser la maladie, avec une pression propre à chaque zone."""
    nouveau = [ligne[:] for ligne in damier]
    taille = len(damier)
    for ligne in range(taille):
        for colonne in range(len(damier[ligne])):
            if damier[ligne][colonne] != ARBRE_MALADE:
                continue
            zone = contexts[zone_de_case(ligne, colonne, taille)]
            for dl, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                lv, cv = ligne + dl, colonne + dc
                if not (0 <= lv < taille and 0 <= cv < len(damier[lv])):
                    continue
                # La fragmentation crée quatre populations distinctes dans le modèle.
                if zone_de_case(lv, cv, taille) != zone_de_case(ligne, colonne, taille):
                    continue
                if damier[lv][cv] == ARBRE_SAIN and random.random() < zone.pression_maladie:
                    nouveau[lv][cv] = ARBRE_MALADE
    return nouveau


def faire_evoluer_population(
    damier: list[list[int]],
    contexts: tuple[ContexteEcologique, ...] = ZONES,
) -> list[list[int]]:
    """Applique mortalité, régénération et compétition dans chaque zone."""
    nouveau = [ligne[:] for ligne in damier]
    taille = len(damier)
    for ligne in range(taille):
        for colonne in range(len(damier[ligne])):
            etat = damier[ligne][colonne]
            if etat in (RIVIERE, ROCHER):
                continue
            zone = contexts[zone_de_case(ligne, colonne, taille)]
            voisins_arbres = sum(
                0 <= ligne + dl < taille
                and 0 <= colonne + dc < len(damier[ligne + dl])
                and damier[ligne + dl][colonne + dc] in (ARBRE_SAIN, ARBRE_MALADE)
                for dl, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
            )
            pression_competition = max(0, voisins_arbres - 2) * zone.competition
            mortalite = min(.95, zone.mortalite + pression_competition)
            if etat == ARBRE_MALADE and random.random() < mortalite + .08:
                nouveau[ligne][colonne] = ARBRE_MORT
            elif etat == ARBRE_SAIN and random.random() < mortalite:
                nouveau[ligne][colonne] = ARBRE_MORT
            elif etat in (CASE_VIDE, ARBRE_MORT) and random.random() < zone.regeneration * zone.fertilite * zone.lumiere:
                nouveau[ligne][colonne] = ARBRE_SAIN
    return nouveau


def etape_ecologique(
    damier: list[list[int]],
    contexts: tuple[ContexteEcologique, ...] = ZONES,
) -> list[list[int]]:
    """Une étape : maladie puis dynamique de population, en parallèle."""
    return faire_evoluer_population(propager_maladie(damier, contexts), contexts)


def afficher_damier(damier: list[list[int]]) -> None:
    symboles = {CASE_VIDE: ".", ARBRE_SAIN: "#", ARBRE_MALADE: "X", RIVIERE: "~", ROCHER: "O", ARBRE_MORT: " "}
    for ligne in damier:
        print(" ".join(symboles[case] for case in ligne))


class ApplicationForet:
    COULEURS = {
        CASE_VIDE: "white", ARBRE_SAIN: "forest green", ARBRE_MALADE: "firebrick",
        RIVIERE: "#5dade2", ROCHER: "#7f8c8d", ARBRE_MORT: "#d5d8dc",
    }
    SYMBOLES = {
        CASE_VIDE: "",
        ARBRE_SAIN: "●",
        ARBRE_MALADE: "✖",
        RIVIERE: "≈",
        ROCHER: "◆",
        ARBRE_MORT: "†",
    }

    def __init__(self, fenetre: tk.Tk) -> None:
        self.fenetre = fenetre
        self.fenetre.title("Dynamique de quatre écosystèmes forestiers")
        self.damier = creer_damier(TAILLE, DENSITE_ARBRES)
        self.etape = 0
        self.cases: list[list[tk.Button]] = []
        self.titre = tk.Label(fenetre, text="Étape 0", font=("Arial", 16, "bold"))
        self.titre.pack(pady=(12, 2))
        self.sous_titre = tk.Label(
            fenetre,
            text="Chaque quadrant évolue avec son propre contexte écologique.",
            font=("Arial", 10),
        )
        self.sous_titre.pack()
        self.grille = tk.Frame(fenetre)
        self.grille.pack(padx=12, pady=8)
        self.construire_grille()
        commandes = tk.Frame(fenetre)
        commandes.pack(pady=(4, 8))
        tk.Button(commandes, text="Étape suivante", command=self.etape_suivante, font=("Arial", 12, "bold"), bg="#d9ead3", padx=12, pady=6).pack(side=tk.LEFT, padx=5)
        tk.Button(commandes, text="Recommencer", command=self.recommencer, font=("Arial", 12), padx=12, pady=6).pack(side=tk.LEFT, padx=5)
        self.creer_legende(fenetre)
        self.information = tk.Label(fenetre, text="", font=("Arial", 10))
        self.information.pack(pady=(0, 12))
        self.actualiser_grille()

    def creer_legende(self, parent: tk.Tk) -> None:
        """Affiche les états et les paramètres qui donnent du sens aux couleurs."""
        cadre = tk.LabelFrame(parent, text="Légende et contextes", padx=8, pady=5)
        cadre.pack(padx=12, pady=(0, 8), fill=tk.X)
        for index, zone in enumerate(ZONES):
            texte = (
                f"{index + 1}. {zone.nom}\n"
                f"{zone.description} | humidité {zone.humidite:.0%} | "
                f"fertilité {zone.fertilite:.0%}"
            )
            tk.Label(cadre, text=texte, anchor="w", justify=tk.LEFT, bg=zone.couleur_zone).grid(
                row=index // 2, column=index % 2, padx=4, pady=2, sticky="ew"
            )
        cadre.columnconfigure(0, weight=1)
        cadre.columnconfigure(1, weight=1)
        tk.Label(
            parent,
            text="● sain   ✖ malade   † mort   ≈ rivière   ◆ rocher",
            font=("Arial", 9),
        ).pack(pady=(0, 5))

    def construire_grille(self) -> None:
        for ligne in range(TAILLE):
            boutons_ligne = []
            for colonne in range(TAILLE):
                bouton = tk.Button(self.grille, width=3, height=1, borderwidth=1,
                                   command=lambda l=ligne, c=colonne: self.cliquer_case(l, c))
                bouton.grid(row=ligne, column=colonne)
                boutons_ligne.append(bouton)
            self.cases.append(boutons_ligne)

    def actualiser_grille(self) -> None:
        compteurs = [[0, 0, 0] for _ in ZONES]
        for ligne in range(TAILLE):
            for colonne in range(TAILLE):
                etat = self.damier[ligne][colonne]
                zone = zone_de_case(ligne, colonne, TAILLE)
                if etat == ARBRE_SAIN:
                    compteurs[zone][0] += 1
                elif etat == ARBRE_MALADE:
                    compteurs[zone][1] += 1
                elif etat == ARBRE_MORT:
                    compteurs[zone][2] += 1
                couleur = self.COULEURS[etat]
                if etat == CASE_VIDE:
                    couleur = ZONES[zone].couleur_zone
                relief = tk.GROOVE
                if ligne in (TAILLE // 2 - 1, TAILLE // 2) or colonne in (TAILLE // 2 - 1, TAILLE // 2):
                    relief = tk.SOLID
                self.cases[ligne][colonne].configure(
                    text=self.SYMBOLES[etat],
                    fg="black" if etat in (CASE_VIDE, ARBRE_MORT, RIVIERE, ROCHER) else "white",
                    bg=couleur,
                    activebackground=couleur,
                    relief=relief,
                )
        resume = "   ".join(
            f"{ZONES[i].nom}: {sains} sains / {malades} malades / {morts} morts"
            for i, (sains, malades, morts) in enumerate(compteurs)
        )
        self.information.configure(text=resume)

    def cliquer_case(self, ligne: int, colonne: int) -> None:
        if self.damier[ligne][colonne] == ARBRE_SAIN:
            self.damier[ligne][colonne] = ARBRE_MALADE
            self.actualiser_grille()

    def etape_suivante(self) -> None:
        self.damier = etape_ecologique(self.damier)
        self.etape += 1
        self.titre.configure(text=f"Étape {self.etape}")
        self.actualiser_grille()

    def recommencer(self) -> None:
        self.damier = creer_damier(TAILLE, DENSITE_ARBRES)
        self.etape = 0
        self.titre.configure(text="Étape 0")
        self.actualiser_grille()


if __name__ == "__main__":
    fenetre = tk.Tk()
    ApplicationForet(fenetre)
    fenetre.mainloop()
