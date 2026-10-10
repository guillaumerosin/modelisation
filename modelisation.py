"""Simulation pédagogique d'un écosystème forestier en quatre zones.

Les paramètres des zones illustrent des facteurs abiotiques (humidité,
fertilité, lumière), des interactions biotiques (maladie, compétition,
mutualisme, espèce invasive, espèce architecte) et un facteur anthropique
(fragmentation de l'habitat, coupes). Des perturbations aléatoires (feu,
tempête, sécheresse) relancent des successions secondaires.
"""

import random
import tkinter as tk
from collections import Counter
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
CENDRES = 6
EN_FEU = 7
CASTOR = 8
BOIS_POURRI = 9
ESPECE_GENERIC = 1
CHENE = 10
HETRE = 11
PIN = 12
SAULE = 13
BOULEAU = 14
ROBINIER = 15
MALADIE_BASE = 20
HUMUS = 30

# Cases où une graine peut germer ; un tronc mort doit d'abord se décomposer.
ETATS_COLONISABLES = (CASE_VIDE, CENDRES, HUMUS)

# Probabilité, à chaque étape, qu'un événement survienne spontanément.
PROBA_EVENEMENTS = {
    "feu": .03,
    "tempete": .02,
    "secheresse": .015,
    "coupe": .03,
    "invasion": .01,
    "castor": .02,
    "mycorhizes": .02,
}
DUREE_SECHERESSE = 6
BAISSE_SECHERESSE = .35


@dataclass(frozen=True)
class Espece:
    nom: str
    symbole: str
    couleur: str
    hydrometrie_ideale: float
    sols_favorables: tuple[str, ...]
    surmortalite: float = 0.0
    pionniere: bool = False
    invasive: bool = False


ESPECES = (
    Espece("Chêne", "C", "#176b2c", .55, ("argilo-calcaire", "limoneux")),
    Espece("Hêtre", "H", "#228b22", .75, ("limoneux", "humifère")),
    Espece("Pin", "P", "#356859", .25, ("sableux", "caillouteux")),
    Espece("Saule", "S", "#149c88", .95, ("alluvial", "humifère")),
    # Pionnier à durée de vie courte : il colonise les trouées puis cède la place.
    Espece("Bouleau", "B", "#7a9a3a", .60, ("limoneux", "humifère", "argilo-calcaire"), surmortalite=.06, pionniere=True),
    # Robinier faux-acacia : introduit par l'homme, il concurrence les espèces locales.
    Espece("Robinier", "R", "#8e44ad", .40, ("argilo-calcaire", "sableux", "limoneux"), surmortalite=-.06, invasive=True),
)
ESPECES_PAR_CODE = dict(zip((CHENE, HETRE, PIN, SAULE, BOULEAU, ROBINIER), ESPECES))


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
    type_sol: str = "limoneux"
    hydrometrie: float = .5
    exposition_vent: float = .5


ZONES = (
    ContexteEcologique("Forêt humide", "Sol humifère, très humide", .90, .85, .30, .03, .22, "#d5f5e3", .80, .03, "humifère", .90, .30),
    ContexteEcologique("Milieu sec", "Sol sableux, hydrométrie faible", .25, .45, .10, .18, .06, "#fdebd0", 1.00, .07, "sableux", .20, .50),
    ContexteEcologique("Montagne", "Sol caillouteux, hydrométrie moyenne", .45, .55, .08, .11, .08, "#d6eaf8", .45, .05, "caillouteux", .40, .90),
    ContexteEcologique("Zone anthropisée", "Sol argilo-calcaire perturbé", .50, .35, .24, .14, .04, "#f5eef8", .70, .10, "argilo-calcaire", .55, .40),
)


@dataclass
class Milieu:
    """Perturbations en cours, qui s'ajoutent aux paramètres fixes des zones."""
    secheresse: int
    humidite_bonus: list[list[float]]
    mycorhizes: list[list[bool]]


def creer_milieu(taille: int) -> Milieu:
    return Milieu(
        secheresse=0,
        humidite_bonus=[[0.0] * taille for _ in range(taille)],
        mycorhizes=[[False] * taille for _ in range(taille)],
    )


def zone_de_case(ligne: int, colonne: int, taille: int) -> int:
    """Retourne le quadrant écologique d'une case."""
    milieu = taille // 2
    return (0 if ligne < milieu else 2) + (0 if colonne < milieu else 1)


def cases_de_zone(index_zone: int, taille: int) -> list[tuple[int, int]]:
    return [
        (ligne, colonne)
        for ligne in range(taille)
        for colonne in range(taille)
        if zone_de_case(ligne, colonne, taille) == index_zone
    ]


def voisins(ligne: int, colonne: int, taille: int) -> list[tuple[int, int]]:
    """Les quatre voisins directs (nord, sud, ouest, est) situés dans la grille."""
    return [
        (ligne + dl, colonne + dc)
        for dl, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
        if 0 <= ligne + dl < taille and 0 <= colonne + dc < taille
    ]


def est_arbre_sain(etat: int) -> bool:
    return etat == ARBRE_SAIN or etat in ESPECES_PAR_CODE


def est_arbre_malade(etat: int) -> bool:
    return etat == ARBRE_MALADE or MALADIE_BASE <= etat < MALADIE_BASE + 10


def est_arbre(etat: int) -> bool:
    return est_arbre_sain(etat) or est_arbre_malade(etat)


def code_espece_malade(code_espece: int) -> int:
    return MALADIE_BASE + (code_espece - CHENE)


def code_espece(etat: int) -> int:
    """Code de l'espèce d'un arbre, qu'il soit sain ou malade."""
    if etat in ESPECES_PAR_CODE:
        return etat
    if MALADIE_BASE <= etat < MALADIE_BASE + 10:
        return etat - MALADIE_BASE + CHENE
    return CHENE


def espece_de(etat: int) -> Espece:
    return ESPECES_PAR_CODE[code_espece(etat)]


def hydrometrie_locale(milieu: Milieu, zone: ContexteEcologique, ligne: int, colonne: int) -> float:
    """Hydrométrie de la zone, modifiée par les barrages de castors et la sécheresse."""
    valeur = zone.hydrometrie + milieu.humidite_bonus[ligne][colonne]
    if milieu.secheresse > 0:
        valeur -= BAISSE_SECHERESSE
    return min(1.0, max(0.0, valeur))


def choisir_espece(
    zone: ContexteEcologique,
    hydrometrie: float | None = None,
    pionnier: bool = False,
) -> int:
    """Sélectionne une espèce selon l'hydrométrie, le sol et le voisinage."""
    hydrometrie = zone.hydrometrie if hydrometrie is None else hydrometrie
    poids = []
    for espece in ESPECES_PAR_CODE.values():
        adequation_eau = max(0.05, 1 - abs(hydrometrie - espece.hydrometrie_ideale))
        adequation_sol = 1.8 if zone.type_sol in espece.sols_favorables else .25
        p = adequation_eau * adequation_sol
        if espece.pionniere:
            # Favorisé sur cendres et dans les trouées, rare sous couvert forestier.
            p *= 2.5 if pionnier else .15
        if espece.invasive:
            # L'invasive ne se propage que par drageons, à partir de pieds installés.
            p = 0
        poids.append(p)
    return random.choices(list(ESPECES_PAR_CODE), weights=poids, k=1)[0]


def creer_damier(taille: int, densite: float) -> list[list[int]]:
    """Crée le damier initial, vide lorsque densite vaut zéro."""
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


def propager_feu(
    damier: list[list[int]],
    contexts: tuple[ContexteEcologique, ...],
    milieu: Milieu,
) -> list[list[int]]:
    """Les arbres en feu deviennent des cendres et enflamment leurs voisins.

    Le feu ignore les frontières de zone, mais il progresse mal dans les
    milieux humides.
    """
    nouveau = [ligne[:] for ligne in damier]
    taille = len(damier)
    for ligne in range(taille):
        for colonne in range(taille):
            if damier[ligne][colonne] != EN_FEU:
                continue
            nouveau[ligne][colonne] = CENDRES
            for lv, cv in voisins(ligne, colonne, taille):
                # Le bois mort au sol est aussi un combustible.
                if not (est_arbre(damier[lv][cv]) or damier[lv][cv] in (ARBRE_MORT, BOIS_POURRI)):
                    continue
                zone = contexts[zone_de_case(lv, cv, taille)]
                if random.random() < .45 + .5 * (1 - hydrometrie_locale(milieu, zone, lv, cv)):
                    nouveau[lv][cv] = EN_FEU
    return nouveau


def activite_castors(damier: list[list[int]], milieu: Milieu) -> list[list[int]]:
    """Les castors abattent des arbres voisins et rendent le milieu plus humide."""
    nouveau = [ligne[:] for ligne in damier]
    taille = len(damier)
    for ligne in range(taille):
        for colonne in range(taille):
            if damier[ligne][colonne] != CASTOR:
                continue
            # Le barrage élève progressivement l'humidité, même après le départ du castor.
            for lv, cv in voisins(ligne, colonne, taille) + [(ligne, colonne)]:
                milieu.humidite_bonus[lv][cv] = min(.4, milieu.humidite_bonus[lv][cv] + .05)
            arbres_voisins = [(lv, cv) for lv, cv in voisins(ligne, colonne, taille) if est_arbre(damier[lv][cv])]
            if arbres_voisins and random.random() < .4:
                lv, cv = random.choice(arbres_voisins)
                nouveau[lv][cv] = ARBRE_MORT
            if random.random() < .05:
                nouveau[ligne][colonne] = CASE_VIDE
    return nouveau


def propager_maladie(
    damier: list[list[int]],
    contexts: tuple[ContexteEcologique, ...] = ZONES,
    milieu: Milieu | None = None,
) -> list[list[int]]:
    """Fait progresser la maladie, avec une pression propre à chaque zone."""
    milieu = milieu or creer_milieu(len(damier))
    nouveau = [ligne[:] for ligne in damier]
    taille = len(damier)
    for ligne in range(taille):
        for colonne in range(len(damier[ligne])):
            if not est_arbre_malade(damier[ligne][colonne]):
                continue
            zone = contexts[zone_de_case(ligne, colonne, taille)]
            for lv, cv in voisins(ligne, colonne, taille):
                # La fragmentation crée quatre populations distinctes dans le modèle.
                if zone_de_case(lv, cv, taille) != zone_de_case(ligne, colonne, taille):
                    continue
                pression = zone.pression_maladie
                # Les mycorhizes renforcent les défenses de l'arbre hôte.
                if milieu.mycorhizes[lv][cv]:
                    pression *= .5
                if est_arbre_sain(damier[lv][cv]) and random.random() < pression:
                    nouveau[lv][cv] = code_espece_malade(code_espece(damier[lv][cv]))
    return nouveau


def faire_evoluer_population(
    damier: list[list[int]],
    contexts: tuple[ContexteEcologique, ...] = ZONES,
    milieu: Milieu | None = None,
) -> list[list[int]]:
    """Applique mortalité, régénération et compétition dans chaque zone."""
    milieu = milieu or creer_milieu(len(damier))
    nouveau = [ligne[:] for ligne in damier]
    taille = len(damier)
    for ligne in range(taille):
        for colonne in range(len(damier[ligne])):
            etat = damier[ligne][colonne]
            if etat in (RIVIERE, ROCHER, EN_FEU, CASTOR):
                continue
            zone = contexts[zone_de_case(ligne, colonne, taille)]
            hydrometrie = hydrometrie_locale(milieu, zone, ligne, colonne)
            etats_voisins = [damier[lv][cv] for lv, cv in voisins(ligne, colonne, taille)]
            voisins_arbres = sum(est_arbre(v) for v in etats_voisins)
            voisins_invasifs = sum(v == ROBINIER for v in etats_voisins)
            mortalite = zone.mortalite + max(0, voisins_arbres - 2) * zone.competition
            if est_arbre(etat):
                espece = espece_de(etat)
                mortalite += espece.surmortalite
                if not espece.invasive:
                    mortalite += .04 * voisins_invasifs
                if milieu.secheresse > 0:
                    # Stress hydrique : les espèces qui aiment l'eau souffrent le plus.
                    mortalite += .5 * max(0, espece.hydrometrie_ideale - hydrometrie)
                if milieu.mycorhizes[ligne][colonne]:
                    mortalite -= .03
            mortalite = min(.95, max(0, mortalite))
            if est_arbre_malade(etat) and random.random() < mortalite + .08:
                nouveau[ligne][colonne] = ARBRE_MORT
            elif est_arbre_sain(etat) and random.random() < mortalite:
                nouveau[ligne][colonne] = ARBRE_MORT
            elif etat in (ARBRE_MORT, BOIS_POURRI):
                # Les décomposeurs (champignons, bactéries, invertébrés) ont besoin d'eau.
                vitesse = .05 + .25 * hydrometrie
                if milieu.secheresse > 0:
                    vitesse *= .5
                if random.random() < vitesse:
                    nouveau[ligne][colonne] = BOIS_POURRI if etat == ARBRE_MORT else HUMUS
            elif etat == HUMUS and random.random() < .03:
                # Sans arbre pour les absorber, les nutriments finissent lessivés.
                nouveau[ligne][colonne] = CASE_VIDE
            elif etat in ETATS_COLONISABLES:
                proba = zone.regeneration * zone.fertilite * zone.lumiere
                if etat in (CENDRES, HUMUS):
                    # Cendres et humus libèrent des minéraux et fertilisent le sol.
                    proba *= 1.5
                if milieu.secheresse > 0:
                    proba *= .5
                # Le robinier drageonne : ses racines font pousser de nouveaux pieds autour de lui.
                if random.random() < .06 * voisins_invasifs:
                    nouveau[ligne][colonne] = ROBINIER
                elif random.random() < proba:
                    nouveau[ligne][colonne] = choisir_espece(
                        zone,
                        hydrometrie,
                        pionnier=etat == CENDRES or voisins_arbres == 0,
                    )
    return nouveau


def etape_ecologique(
    damier: list[list[int]],
    contexts: tuple[ContexteEcologique, ...] = ZONES,
    milieu: Milieu | None = None,
) -> list[list[int]]:
    """Une étape : feu, castors, maladie puis dynamique de population."""
    milieu = milieu or creer_milieu(len(damier))
    damier = propager_feu(damier, contexts, milieu)
    damier = activite_castors(damier, milieu)
    damier = propager_maladie(damier, contexts, milieu)
    damier = faire_evoluer_population(damier, contexts, milieu)
    if milieu.secheresse > 0:
        milieu.secheresse -= 1
    return damier


# --- Événements : ils modifient directement le damier et le milieu. ---

def declencher_feu(damier: list[list[int]], milieu: Milieu, contexts: tuple[ContexteEcologique, ...] = ZONES) -> str:
    """Enflamme un arbre, de préférence dans un milieu sec."""
    taille = len(damier)
    candidats = [(l, c) for l in range(taille) for c in range(taille) if est_arbre(damier[l][c])]
    if not candidats:
        return "Feu : aucun arbre à enflammer."
    poids = [1.1 - hydrometrie_locale(milieu, contexts[zone_de_case(l, c, taille)], l, c) for l, c in candidats]
    ligne, colonne = random.choices(candidats, weights=poids, k=1)[0]
    damier[ligne][colonne] = EN_FEU
    return f"Feu de forêt déclaré ({contexts[zone_de_case(ligne, colonne, taille)].nom})."


def declencher_tempete(damier: list[list[int]], milieu: Milieu, contexts: tuple[ContexteEcologique, ...] = ZONES) -> str:
    """Abat les arbres sur une bande de deux lignes, surtout dans les zones exposées."""
    taille = len(damier)
    premiere = random.randrange(taille - 1)
    abattus = 0
    for ligne in (premiere, premiere + 1):
        for colonne in range(taille):
            zone = contexts[zone_de_case(ligne, colonne, taille)]
            if est_arbre(damier[ligne][colonne]) and random.random() < zone.exposition_vent:
                damier[ligne][colonne] = ARBRE_MORT
                abattus += 1
    return f"Tempête : {abattus} arbre(s) abattu(s), lignes {premiere + 1}-{premiere + 2}."


def declencher_secheresse(damier: list[list[int]], milieu: Milieu, contexts: tuple[ContexteEcologique, ...] = ZONES) -> str:
    milieu.secheresse = DUREE_SECHERESSE
    return f"Sécheresse : hydrométrie réduite pendant {DUREE_SECHERESSE} étapes."


def declencher_coupe(damier: list[list[int]], milieu: Milieu, contexts: tuple[ContexteEcologique, ...] = ZONES) -> str:
    """Coupe rase du bloc de 3 × 3 cases le plus boisé d'une zone.

    L'homme exploite là où il y a du bois, avec une préférence pour la zone
    anthropisée.
    """
    taille = len(damier)
    moitie = taille // 2
    arbres_par_zone = [sum(est_arbre(damier[l][c]) for l, c in cases_de_zone(i, taille)) for i in range(len(contexts))]
    poids = [n * (3 if i == 3 else 1) for i, n in enumerate(arbres_par_zone)]
    if not any(poids):
        return "Coupe humaine : aucun arbre à couper."
    index_zone = random.choices(range(len(contexts)), weights=poids, k=1)[0]
    origine_ligne = 0 if index_zone < 2 else moitie
    origine_colonne = 0 if index_zone % 2 == 0 else moitie
    debut_ligne, debut_colonne = max(
        ((origine_ligne + dl, origine_colonne + dc) for dl in range(moitie - 2) for dc in range(moitie - 2)),
        key=lambda coin: sum(
            est_arbre(damier[l][c])
            for l in range(coin[0], coin[0] + 3)
            for c in range(coin[1], coin[1] + 3)
        ),
    )
    coupes = 0
    for ligne in range(debut_ligne, debut_ligne + 3):
        for colonne in range(debut_colonne, debut_colonne + 3):
            if est_arbre(damier[ligne][colonne]):
                damier[ligne][colonne] = ARBRE_MORT
                coupes += 1
    return f"Coupe humaine : {coupes} arbre(s) abattu(s) ({contexts[index_zone].nom})."


def declencher_invasion(damier: list[list[int]], milieu: Milieu, contexts: tuple[ContexteEcologique, ...] = ZONES) -> str:
    """L'homme introduit deux robiniers dans la zone anthropisée."""
    taille = len(damier)
    candidats = [
        (l, c) for l, c in cases_de_zone(3, taille)
        if damier[l][c] in ETATS_COLONISABLES + (ARBRE_MORT, BOIS_POURRI)
    ]
    if not candidats:
        return "Invasion : aucune place libre en zone anthropisée."
    for ligne, colonne in random.sample(candidats, min(2, len(candidats))):
        damier[ligne][colonne] = ROBINIER
    return "Espèce invasive : robinier faux-acacia introduit en zone anthropisée."


def declencher_castor(damier: list[list[int]], milieu: Milieu, contexts: tuple[ContexteEcologique, ...] = ZONES) -> str:
    """Un castor s'installe, de préférence là où l'eau est abondante."""
    taille = len(damier)
    candidats = [
        (l, c) for l in range(taille) for c in range(taille)
        if damier[l][c] in (CASE_VIDE, HUMUS, ARBRE_MORT, BOIS_POURRI) and contexts[zone_de_case(l, c, taille)].hydrometrie >= .4
    ]
    if not candidats:
        return "Castor : aucun site favorable."
    poids = [hydrometrie_locale(milieu, contexts[zone_de_case(l, c, taille)], l, c) for l, c in candidats]
    ligne, colonne = random.choices(candidats, weights=poids, k=1)[0]
    damier[ligne][colonne] = CASTOR
    return f"Un castor construit un barrage ({contexts[zone_de_case(ligne, colonne, taille)].nom})."


def declencher_mycorhizes(damier: list[list[int]], milieu: Milieu, contexts: tuple[ContexteEcologique, ...] = ZONES) -> str:
    """Un réseau mycorhizien colonise un carré de 3 × 3 cases dans une zone."""
    taille = len(damier)
    ligne, colonne = random.randrange(taille), random.randrange(taille)
    zone = zone_de_case(ligne, colonne, taille)
    for lv in range(ligne - 1, ligne + 2):
        for cv in range(colonne - 1, colonne + 2):
            if 0 <= lv < taille and 0 <= cv < taille and zone_de_case(lv, cv, taille) == zone:
                milieu.mycorhizes[lv][cv] = True
    return f"Mycorhizes installées ({contexts[zone].nom})."


EVENEMENTS = {
    "feu": ("Feu", declencher_feu),
    "tempete": ("Tempête", declencher_tempete),
    "secheresse": ("Sécheresse", declencher_secheresse),
    "coupe": ("Coupe", declencher_coupe),
    "invasion": ("Invasive", declencher_invasion),
    "castor": ("Castor", declencher_castor),
    "mycorhizes": ("Mycorhizes", declencher_mycorhizes),
}


def evenements_aleatoires(
    damier: list[list[int]],
    milieu: Milieu,
    contexts: tuple[ContexteEcologique, ...] = ZONES,
) -> list[str]:
    """Tire au sort les événements de l'étape et renvoie leur description."""
    return [
        EVENEMENTS[cle][1](damier, milieu, contexts)
        for cle, proba in PROBA_EVENEMENTS.items()
        if random.random() < proba
    ]


def nom_pluriel(nom: str, nombre: int) -> str:
    nom = nom.lower()
    if nombre == 1:
        return nom
    return nom + ("x" if nom.endswith("eau") else "s")


def decrire_changements(
    avant: list[list[int]],
    apres: list[list[int]],
    contexts: tuple[ContexteEcologique, ...] = ZONES,
) -> list[tuple[str, list[tuple[str, str]]]]:
    """Résume, zone par zone, ce qui a changé entre deux damiers.

    Chaque zone modifiée donne une liste de fragments (catégorie, texte) ;
    la catégorie sert à colorer le journal.
    """
    taille = len(avant)
    resultat = []
    for index, zone in enumerate(contexts):
        pousses: Counter[str] = Counter()
        infectes = morts = tues_maladie = en_feu = departs_castor = 0
        pourris = humifies = 0
        for ligne, colonne in cases_de_zone(index, taille):
            a, b = avant[ligne][colonne], apres[ligne][colonne]
            if a == b:
                continue
            if est_arbre(b) and not est_arbre(a):
                pousses[espece_de(b).nom] += 1
            elif est_arbre_sain(a) and est_arbre_malade(b):
                infectes += 1
            elif est_arbre(a) and b == ARBRE_MORT:
                if est_arbre_malade(a):
                    tues_maladie += 1
                else:
                    morts += 1
            elif b == EN_FEU:
                en_feu += 1
            elif a == ARBRE_MORT and b == BOIS_POURRI:
                pourris += 1
            elif a == BOIS_POURRI and b == HUMUS:
                humifies += 1
            elif a == CASTOR:
                departs_castor += 1
        fragments = []
        if pousses:
            detail = ", ".join(f"{n} {nom_pluriel(nom, n)}" for nom, n in pousses.most_common())
            fragments.append(("pousse", f"+{sum(pousses.values())} ({detail})"))
        if infectes:
            fragments.append(("maladie", f"{infectes} infecté{'s' if infectes > 1 else ''}"))
        if tues_maladie:
            fragments.append(("maladie", f"{tues_maladie} tué{'s' if tues_maladie > 1 else ''} par la maladie"))
        if morts:
            fragments.append(("mort", f"{morts} mort{'s' if morts > 1 else ''}"))
        if en_feu:
            fragments.append(("feu", f"{en_feu} case{'s' if en_feu > 1 else ''} en feu"))
        if pourris:
            fragments.append(("decomposition", f"{pourris} tronc{'s' if pourris > 1 else ''} en décomposition"))
        if humifies:
            fragments.append(("decomposition", f"{humifies} devenu{'s' if humifies > 1 else ''} humus"))
        if departs_castor:
            fragments.append(("castor", "le castor quitte son barrage"))
        if fragments:
            resultat.append((zone.nom, fragments))
    return resultat


def afficher_damier(damier: list[list[int]]) -> None:
    symboles = {
        CASE_VIDE: ".", ARBRE_SAIN: "#", ARBRE_MALADE: "X", RIVIERE: "~", ROCHER: "O",
        ARBRE_MORT: " ", CENDRES: ",", EN_FEU: "*", CASTOR: "K", BOIS_POURRI: ";", HUMUS: ":",
    }
    for ligne in damier:
        print(" ".join(ESPECES_PAR_CODE[case].symbole if case in ESPECES_PAR_CODE else symboles.get(case, "x") for case in ligne))


class ApplicationForet:
    COULEURS = {
        CASE_VIDE: "white", ARBRE_SAIN: "forest green", ARBRE_MALADE: "firebrick",
        RIVIERE: "#5dade2", ROCHER: "#7f8c8d", ARBRE_MORT: "#d5d8dc",
        CENDRES: "#4d4d4d", EN_FEU: "#ff7f0e", CASTOR: "#8b5a2b",
        BOIS_POURRI: "#c8ad8d", HUMUS: "#6d4c35",
    }
    SYMBOLES = {
        CASE_VIDE: "",
        ARBRE_SAIN: "●",
        ARBRE_MALADE: "✖",
        RIVIERE: "≈",
        ROCHER: "◆",
        ARBRE_MORT: "†",
        CENDRES: "░",
        EN_FEU: "✱",
        CASTOR: "◉",
        BOIS_POURRI: "∴",
        HUMUS: "◦",
    }
    COULEUR_MYCORHIZES = "#d4ac0d"
    LIGNES_JOURNAL_MAX = 800
    STYLES_JOURNAL = {
        "etape": {"font": ("Arial", 11, "bold"), "spacing1": 8},
        "resume": {"foreground": "#566573"},
        "zone": {"font": ("Arial", 10, "bold")},
        "evenement": {"foreground": "#9c4a00", "background": "#fdebd0", "font": ("Arial", 10, "bold")},
        "pousse": {"foreground": "#1e8449"},
        "maladie": {"foreground": "#b03a2e"},
        "mort": {"foreground": "#616a6b"},
        "feu": {"foreground": "#d35400", "font": ("Arial", 10, "bold")},
        "castor": {"foreground": "#8b5a2b"},
        "decomposition": {"foreground": "#795548"},
        "calme": {"foreground": "#99a3a4", "font": ("Arial", 10, "italic")},
    }

    def __init__(self, fenetre: tk.Tk) -> None:
        self.fenetre = fenetre
        self.fenetre.title("Dynamique de quatre écosystèmes forestiers")
        self.damier = creer_damier(TAILLE, DENSITE_ARBRES)
        self.milieu = creer_milieu(TAILLE)
        self.etape = 0
        self.en_cours = False
        self.tache_auto: str | None = None
        self.cases: list[list[tk.Button]] = []
        self.titre = tk.Label(fenetre, text="Étape 0", font=("Arial", 16, "bold"))
        self.titre.pack(pady=(12, 2))
        self.sous_titre = tk.Label(
            fenetre,
            text="Chaque quadrant évolue avec son propre contexte écologique.",
            font=("Arial", 10),
        )
        self.sous_titre.pack()
        centre = tk.Frame(fenetre)
        centre.pack(padx=12, pady=8, fill=tk.X)
        self.grille = tk.Frame(centre)
        self.grille.pack(side=tk.LEFT, anchor="n")
        self.construire_grille()
        self.creer_journal(centre)
        commandes = tk.Frame(fenetre)
        commandes.pack(pady=(4, 8))
        tk.Button(commandes, text="Étape suivante", command=self.etape_suivante, font=("Arial", 12, "bold"), bg="#d9ead3", padx=12, pady=6).pack(side=tk.LEFT, padx=5)
        self.bouton_lecture = tk.Button(commandes, text="▶ Lecture", command=self.basculer_lecture, font=("Arial", 12), padx=12, pady=6, width=10)
        self.bouton_lecture.pack(side=tk.LEFT, padx=5)
        tk.Button(commandes, text="Recommencer", command=self.recommencer, font=("Arial", 12), padx=12, pady=6).pack(side=tk.LEFT, padx=5)
        # Délai entre deux étapes en mode continu.
        self.delai = tk.Scale(commandes, from_=50, to=2000, resolution=50, orient=tk.HORIZONTAL, label="Délai (ms)", length=160)
        self.delai.set(500)
        self.delai.pack(side=tk.LEFT, padx=5)
        self.creer_commandes_evenements(fenetre)
        self.creer_legende(fenetre)
        self.information = tk.Label(fenetre, text="", font=("Arial", 10))
        self.information.pack(pady=(0, 12))
        self.ecrire_journal([("Nouvelle simulation : sol nu.\n", "etape")])
        self.actualiser_grille()

    def creer_journal(self, parent: tk.Frame) -> None:
        """Panneau à droite de la grille qui raconte chaque étape, le plus récent en haut."""
        cadre = tk.LabelFrame(parent, text="Journal du damier", padx=6, pady=4, font=("Arial", 11, "bold"))
        cadre.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))
        self.texte_journal = tk.Text(cadre, width=55, height=20, wrap=tk.WORD, font=("Arial", 10),
                                     bg="#fbfcfc", relief=tk.FLAT, state=tk.DISABLED)
        barre = tk.Scrollbar(cadre, command=self.texte_journal.yview)
        self.texte_journal.configure(yscrollcommand=barre.set)
        barre.pack(side=tk.RIGHT, fill=tk.Y)
        self.texte_journal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        for tag, style in self.STYLES_JOURNAL.items():
            self.texte_journal.tag_configure(tag, **style)

    def creer_commandes_evenements(self, parent: tk.Tk) -> None:
        """Un bouton par événement et une case pour activer le hasard."""
        cadre = tk.LabelFrame(parent, text="Perturbations et espèces", padx=8, pady=5)
        cadre.pack(padx=12, pady=(0, 8))
        for cle, (libelle, _) in EVENEMENTS.items():
            tk.Button(cadre, text=libelle, command=lambda c=cle: self.declencher(c), padx=6).pack(side=tk.LEFT, padx=2)
        self.aleatoire = tk.BooleanVar(value=True)
        tk.Checkbutton(cadre, text="Événements aléatoires", variable=self.aleatoire).pack(side=tk.LEFT, padx=(10, 0))

    def creer_legende(self, parent: tk.Tk) -> None:
        """Affiche les états et les paramètres qui donnent du sens aux couleurs."""
        cadre = tk.LabelFrame(parent, text="Légende et contextes", padx=8, pady=5)
        cadre.pack(padx=12, pady=(0, 8), fill=tk.X)
        for index, zone in enumerate(ZONES):
            texte = (
                f"{index + 1}. {zone.nom}\n"
                f"{zone.description} | humidité {zone.humidite:.0%} | "
                f"hydrométrie {zone.hydrometrie:.0%} | sol {zone.type_sol}"
            )
            tk.Label(cadre, text=texte, anchor="w", justify=tk.LEFT, bg=zone.couleur_zone).grid(
                row=index // 2, column=index % 2, padx=4, pady=2, sticky="ew"
            )
        cadre.columnconfigure(0, weight=1)
        cadre.columnconfigure(1, weight=1)
        tk.Label(
            parent,
            text=(
                "C chêne   H hêtre   P pin   S saule   B bouleau (pionnier)   R robinier (invasif)\n"
                "× malade   † mort   ∴ bois pourri   ◦ humus   ✱ en feu   ░ cendres   ◉ castor   cadre doré : mycorhizes"
            ),
            font=("Arial", 9),
        ).pack(pady=(0, 5))

    def construire_grille(self) -> None:
        for ligne in range(TAILLE):
            boutons_ligne = []
            for colonne in range(TAILLE):
                bouton = tk.Button(self.grille, width=3, height=1, borderwidth=1, highlightthickness=2,
                                   command=lambda l=ligne, c=colonne: self.cliquer_case(l, c))
                bouton.grid(row=ligne, column=colonne)
                boutons_ligne.append(bouton)
            self.cases.append(boutons_ligne)

    def actualiser_grille(self) -> None:
        compteurs = [[0, 0, 0] for _ in ZONES]
        fond_fenetre = self.fenetre.cget("bg")
        for ligne in range(TAILLE):
            for colonne in range(TAILLE):
                etat = self.damier[ligne][colonne]
                zone = zone_de_case(ligne, colonne, TAILLE)
                if est_arbre_sain(etat):
                    compteurs[zone][0] += 1
                elif est_arbre_malade(etat):
                    compteurs[zone][1] += 1
                elif etat == ARBRE_MORT:
                    compteurs[zone][2] += 1
                couleur = ESPECES_PAR_CODE[etat].couleur if etat in ESPECES_PAR_CODE else self.COULEURS.get(etat, "#8b0000")
                if etat == CASE_VIDE:
                    couleur = ZONES[zone].couleur_zone
                symbole = ESPECES_PAR_CODE[etat].symbole if etat in ESPECES_PAR_CODE else self.SYMBOLES.get(etat, "")
                if est_arbre_malade(etat):
                    symbole = f"×{espece_de(etat).symbole}"
                relief = tk.GROOVE
                if ligne in (TAILLE // 2 - 1, TAILLE // 2) or colonne in (TAILLE // 2 - 1, TAILLE // 2):
                    relief = tk.SOLID
                self.cases[ligne][colonne].configure(
                    text=symbole,
                    fg="black" if etat in (CASE_VIDE, ARBRE_MORT, RIVIERE, ROCHER, EN_FEU, BOIS_POURRI) else "white",
                    bg=couleur,
                    activebackground=couleur,
                    relief=relief,
                    highlightbackground=self.COULEUR_MYCORHIZES if self.milieu.mycorhizes[ligne][colonne] else fond_fenetre,
                )
        resume = "   ".join(
            f"{ZONES[i].nom}: {sains} sains / {malades} malades / {morts} morts"
            for i, (sains, malades, morts) in enumerate(compteurs)
        )
        self.information.configure(text=resume)
        titre = f"Étape {self.etape}"
        if self.milieu.secheresse > 0:
            titre += f" — sécheresse ({self.milieu.secheresse} étape(s) restante(s))"
        self.titre.configure(text=titre)

    def ecrire_journal(self, morceaux: list[tuple[str, str]]) -> None:
        """Ajoute un bloc (texte, style) en haut du journal."""
        arguments = [element for texte, tag in morceaux for element in (texte, tag)]
        self.texte_journal.configure(state=tk.NORMAL)
        self.texte_journal.insert("1.0", *arguments)
        self.texte_journal.delete(f"{self.LIGNES_JOURNAL_MAX}.0", tk.END)
        self.texte_journal.configure(state=tk.DISABLED)
        self.texte_journal.yview_moveto(0)

    def journaliser_etape(self, changements: list[tuple[str, list[tuple[str, str]]]], evenements: list[str]) -> None:
        arbres = sum(est_arbre(etat) for ligne in self.damier for etat in ligne)
        malades = sum(est_arbre_malade(etat) for ligne in self.damier for etat in ligne)
        morceaux = [(f"Étape {self.etape}", "etape"), (f"   {arbres} arbres, {malades} malades\n", "resume")]
        morceaux += [(f"  ⚠ {message}\n", "evenement") for message in evenements]
        for nom_zone, fragments in changements:
            morceaux.append((f"  {nom_zone} : ", "zone"))
            for position, (categorie, texte) in enumerate(fragments):
                morceaux.append(((" · " if position else "") + texte, categorie))
            morceaux.append(("\n", ""))
        if not changements and not evenements:
            morceaux.append(("  Aucun changement.\n", "calme"))
        self.ecrire_journal(morceaux)

    def declencher(self, cle: str) -> None:
        message = EVENEMENTS[cle][1](self.damier, self.milieu, ZONES)
        self.ecrire_journal([(f"Étape {self.etape} — action manuelle\n", "etape"), (f"  ⚠ {message}\n", "evenement")])
        self.actualiser_grille()

    def cliquer_case(self, ligne: int, colonne: int) -> None:
        etat = self.damier[ligne][colonne]
        if est_arbre_sain(etat):
            self.damier[ligne][colonne] = code_espece_malade(code_espece(etat))
            zone = ZONES[zone_de_case(ligne, colonne, TAILLE)]
            self.ecrire_journal([
                (f"Étape {self.etape} — action manuelle\n", "etape"),
                (f"  Contamination : un {espece_de(etat).nom.lower()} ({zone.nom}, ligne {ligne + 1}, colonne {colonne + 1})\n", "maladie"),
            ])
            self.actualiser_grille()

    def etape_suivante(self) -> None:
        avant = self.damier
        secheresse_en_cours = self.milieu.secheresse > 0
        self.damier = etape_ecologique(self.damier, ZONES, self.milieu)
        self.etape += 1
        changements = decrire_changements(avant, self.damier)
        evenements = evenements_aleatoires(self.damier, self.milieu, ZONES) if self.aleatoire.get() else []
        if secheresse_en_cours and self.milieu.secheresse == 0:
            evenements.insert(0, "Fin de la sécheresse.")
        self.journaliser_etape(changements, evenements)
        self.actualiser_grille()

    def basculer_lecture(self) -> None:
        """Lance ou met en pause l'enchaînement automatique des étapes."""
        if self.en_cours:
            self.arreter_lecture()
        else:
            self.en_cours = True
            self.bouton_lecture.configure(text="⏸ Pause")
            self.boucle_auto()

    def boucle_auto(self) -> None:
        if not self.en_cours:
            return
        self.etape_suivante()
        self.tache_auto = self.fenetre.after(self.delai.get(), self.boucle_auto)

    def arreter_lecture(self) -> None:
        self.en_cours = False
        if self.tache_auto is not None:
            self.fenetre.after_cancel(self.tache_auto)
            self.tache_auto = None
        self.bouton_lecture.configure(text="▶ Lecture")

    def recommencer(self) -> None:
        self.arreter_lecture()
        self.damier = creer_damier(TAILLE, DENSITE_ARBRES)
        self.milieu = creer_milieu(TAILLE)
        self.etape = 0
        self.texte_journal.configure(state=tk.NORMAL)
        self.texte_journal.delete("1.0", tk.END)
        self.ecrire_journal([("Nouvelle simulation : sol nu.\n", "etape")])
        self.actualiser_grille()


if __name__ == "__main__":
    fenetre = tk.Tk()
    ApplicationForet(fenetre)
    fenetre.mainloop()
