import random
import tkinter as tk


TAILLE = 10
DENSITE_ARBRES = 0.8

CASE_VIDE = 0
ARBRE_SAIN = 1
ARBRE_MALADE = 2
RIVIERE = 3
ROCHER = 4


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


def ajouter_decors(damier: list[list[int]], nombre_rochers: int = 8) -> None:
	"""Ajoute une riviere continue et des rochers sur les cases vides."""
	taille = len(damier)
	colonne_riviere = taille // 2

	for ligne in range(taille):
		for colonne in range(max(0, colonne_riviere - 1), min(taille, colonne_riviere + 2)):
			damier[ligne][colonne] = RIVIERE

	cases_vides = [
		(ligne, colonne)
		for ligne in range(taille)
		for colonne in range(len(damier[ligne]))
		if damier[ligne][colonne] == CASE_VIDE
	]
	for ligne, colonne in random.sample(cases_vides, min(nombre_rochers, len(cases_vides))):
		damier[ligne][colonne] = ROCHER


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
				if 0 <= ligne_voisine < len(damier) and 0 <= colonne_voisine < len(damier[ligne_voisine]):
					if damier[ligne_voisine][colonne_voisine] == ARBRE_SAIN:
						nouveau_damier[ligne_voisine][colonne_voisine] = ARBRE_MALADE

	return nouveau_damier


def afficher_damier(damier: list[list[int]]) -> None:
	"""Affiche le damier avec un symbole par etat."""
	symboles = {
		CASE_VIDE: ".",
		ARBRE_SAIN: "#",
		ARBRE_MALADE: "X",
		RIVIERE: "~",
		ROCHER: "O",
	}

	for ligne in damier:
		print(" ".join(symboles[case] for case in ligne))


class ApplicationForet:
	"""Interface interactive de la simulation."""

	COULEURS = {
		CASE_VIDE: "white",
		ARBRE_SAIN: "forest green",
		ARBRE_MALADE: "firebrick",
		RIVIERE: "#5dade2",
		ROCHER: "#7f8c8d",
	}

	def __init__(self, fenetre: tk.Tk) -> None:
		self.fenetre = fenetre
		self.fenetre.title("Propagation d'une maladie dans une foret")
		self.damier = creer_damier(TAILLE, DENSITE_ARBRES)
		ajouter_decors(self.damier)
		self.etape = 0
		self.cases: list[list[tk.Button]] = []

		self.titre = tk.Label(fenetre, text="Etape 0", font=("Arial", 16, "bold"))
		self.titre.pack(pady=(12, 4))

		self.grille = tk.Frame(fenetre)
		self.grille.pack(padx=12, pady=8)
		self.construire_grille()

		commandes = tk.Frame(fenetre)
		commandes.pack(pady=(4, 12))
		tk_bouton = tk.Button(
			commandes,
			text="Etape suivante",
			command=self.etape_suivante,
			font=("Arial", 12, "bold"),
			bg="#d9ead3",
			padx=12,
			pady=6,
		)
		tk_bouton.pack(side=tk.LEFT, padx=5)
		tk_reset = tk.Button(
			commandes,
			text="Recommencer",
			command=self.recommencer,
			font=("Arial", 12),
			padx=12,
			pady=6,
		)
		tk_reset.pack(side=tk.LEFT, padx=5)

		self.information = tk.Label(
			fenetre,
			text="Clique sur un arbre sain pour placer la contamination, puis avance etape par etape.",
			font=("Arial", 10),
		)
		self.information.pack(pady=(0, 12))

	def construire_grille(self) -> None:
		"""Construit les cases cliquables du damier."""
		for ligne in range(TAILLE):
			boutons_ligne = []
			for colonne in range(TAILLE):
				bouton = tk.Button(
					self.grille,
					width=3,
					height=1,
					borderwidth=1,
					command=lambda l=ligne, c=colonne: self.cliquer_case(l, c),
				)
				bouton.grid(row=ligne, column=colonne)
				boutons_ligne.append(bouton)
			self.cases.append(boutons_ligne)
		self.actualiser_grille()

	def actualiser_grille(self) -> None:
		for ligne in range(TAILLE):
			for colonne in range(TAILLE):
				etat = self.damier[ligne][colonne]
				self.cases[ligne][colonne].configure(bg=self.COULEURS[etat], activebackground=self.COULEURS[etat])

	def cliquer_case(self, ligne: int, colonne: int) -> None:
		if self.damier[ligne][colonne] == ARBRE_SAIN:
			self.damier[ligne][colonne] = ARBRE_MALADE
			self.actualiser_grille()

	def etape_suivante(self) -> None:
		self.damier = propager_maladie(self.damier)
		self.etape += 1
		self.titre.configure(text=f"Etape {self.etape}")
		self.actualiser_grille()

	def recommencer(self) -> None:
		self.damier = creer_damier(TAILLE, DENSITE_ARBRES)
		ajouter_decors(self.damier)
		self.etape = 0
		self.titre.configure(text="Etape 0")
		self.actualiser_grille()


fenetre = tk.Tk()
application = ApplicationForet(fenetre)
fenetre.mainloop()
