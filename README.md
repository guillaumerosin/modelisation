# Simulation de contamination d'une forêt

## Contexte

Cette simulation représente une forêt composée d'arbres sains. Un champignon pathogène apparaît dans un arbre contaminé et peut ensuite se transmettre aux arbres voisins.

Le champignon choisi est fictif, mais il est inspiré de l'armillaire (`Armillaria mellea`), un champignon réel qui peut attaquer les racines et le bois de nombreux arbres. Dans la nature, il se propage notamment par les racines et par des filaments souterrains appelés rhizomorphes.

## Fonctionnement de la simulation

- La forêt est créée sur une grille de 10 × 10 cases.
- Les arbres sont répartis aléatoirement.
- L'utilisateur choisit lui-même l'arbre contaminé en cliquant sur un arbre sain.
- À chaque clic sur **Étape suivante**, la maladie atteint les arbres sains situés directement au nord, au sud, à l'est ou à l'ouest d'un arbre malade.
- La propagation se fait étape par étape : les arbres contaminés pendant une étape propagent la maladie à l'étape suivante.
- La rivière et les rochers sont des obstacles : ils ne sont pas contaminés et empêchent la propagation entre deux cases voisines.
- Le bouton **Recommencer** crée une nouvelle forêt avec une nouvelle disposition des arbres, de la rivière et des rochers.

Cette règle est une simplification pédagogique : dans une vraie forêt, la propagation dépend aussi de la distance entre les racines, de l'humidité, de la nature du sol, de la santé des arbres et des conditions météorologiques.

## Légende

- Vert : arbre sain
- Rouge : arbre contaminé
- Bleu : rivière
- Gris : rocher
- Blanc : case vide

## Lancer le programme

Depuis le dossier du projet :

```bash
python3 modelisation.py
```

Le programme utilise `tkinter`, généralement inclus avec Python sous Linux, Windows et macOS.
