import random


TAILLE = 10
DENSITE_ARBRES = 0.8

CASE_VIDE = 0
ARBRE_SAIN = 1
ARBRE_MALADE = 2


def creer_damier(taille: int, densite: float) -> list[list[int]]:
	"""Cree un damier avec des arbres repartis aleatoirement."""
	damier = []

	for _ in range(taille):
		ligne = []
		for _ in range(taille):
			if random.random() < densite:
				ligne.append(ARBRE_SAIN)
			else:
				ligne.append(CASE_VIDE)
		damier.append(ligne)

	return damier


def placer_arbre_malade(damier: list[list[int]]) -> None:
	"""Transforme un arbre sain choisi au hasard en arbre malade."""
	arbres_sains = [
		(ligne, colonne)
		for ligne in range(len(damier))
		for colonne in range(len(damier[ligne]))
		if damier[ligne][colonne] == ARBRE_SAIN
	]

	if arbres_sains:
		ligne, colonne = random.choice(arbres_sains)
		damier[ligne][colonne] = ARBRE_MALADE


def propager_maladie(damier: list[list[int]]) -> list[list[int]]:
	"""Contamine les arbres sains voisins des arbres malades."""
	nouveau_damier = [ligne[:] for ligne in damier]

	for ligne in range(len(damier)):
		for colonne in range(len(damier[ligne])):
			if damier[ligne][colonne] != ARBRE_MALADE:
				continue

			voisins = [
				(ligne - 1, colonne),
				(ligne + 1, colonne),
				(ligne, colonne - 1),
				(ligne, colonne + 1),
			]

			for ligne_voisine, colonne_voisine in voisins:
				if 0 <= ligne_voisine < len(damier) and 0 <= colonne_voisine < len(damier[ligne]):
					if damier[ligne_voisine][colonne_voisine] == ARBRE_SAIN:
						nouveau_damier[ligne_voisine][colonne_voisine] = ARBRE_MALADE

	return nouveau_damier


def afficher_damier(damier: list[list[int]]) -> None:
	"""Affiche le damier avec un symbole par etat."""
	symboles = {
		CASE_VIDE: ".",
		ARBRE_SAIN: "#",
		ARBRE_MALADE: "X",
	}

	for ligne in damier:
		print(" ".join(symboles[case] for case in ligne))


damier = creer_damier(TAILLE, DENSITE_ARBRES)
placer_arbre_malade(damier)

print("Etat initial :")
afficher_damier(damier)

damier = propager_maladie(damier)

print("\nApres une etape de propagation :")
afficher_damier(damier)
