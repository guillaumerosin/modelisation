# Simulation de quatre écosystèmes forestiers

## Contexte

Cette simulation représente un damier de 12 × 12 cases séparé en quatre zones.
Chaque zone représente un contexte écologique différent et évolue en parallèle.
Un champignon pathogène apparaît dans un arbre contaminé et peut ensuite se
transmettre aux arbres voisins.

Le champignon choisi est fictif, mais il est inspiré de l'armillaire (`Armillaria mellea`), un champignon réel qui peut attaquer les racines et le bois de nombreux arbres. Dans la nature, il se propage notamment par les racines et par des filaments souterrains appelés rhizomorphes.

## Fonctionnement de la simulation

- La simulation commence sur un sol nu : les 144 cases sont vides au départ,
  sans arbres, rochers ni rivière.
- La grille de 12 × 12 cases est divisée en quatre quadrants :
  - **Forêt humide** : humidité et fertilité élevées, régénération importante.
  - **Milieu sec** : la faible humidité est un facteur limitant et augmente la mortalité.
  - **Montagne** : croissance lente et pression de maladie faible.
  - **Zone anthropisée** : fertilité faible, mortalité et pression de maladie plus fortes.
- À chaque étape, les zones appliquent leurs propres probabilités de
  régénération. Les premiers arbres apparaissent donc progressivement, ce qui
  représente une succession écologique sur un sol nu.
- Une fois les arbres apparus, l'utilisateur peut cliquer sur un arbre sain pour
  placer la contamination.
- À chaque clic sur **Étape suivante**, les quatre populations évoluent simultanément :
  maladie, mortalité et régénération sont calculées pour chaque zone.
- La maladie atteint les arbres sains situés directement au nord, au sud, à
  l'est ou à l'ouest d'un arbre malade. Une frontière de zone bloque la
  propagation afin de représenter la fragmentation des habitats.
- La propagation se fait étape par étape : les arbres contaminés pendant une étape propagent la maladie à l'étape suivante.
- Le bouton **Recommencer** remet le sol entièrement à nu et relance la
  succession écologique.

Cette règle est une simplification pédagogique inspirée des notions du cours :
facteurs abiotiques (climat, humidité, sol), interactions biotiques
(parasitisme et maladie), régulation des populations et facteur anthropique.

## Légende

- Vert : arbre sain
- Rouge : arbre contaminé
- Gris clair : arbre mort
- Blanc ou couleur pâle : case vide (la couleur indique sa zone)

## Lancer le programme

Depuis le dossier du projet :

```bash
python3 modelisation.py
```

Le programme utilise `tkinter`, généralement inclus avec Python sous Linux, Windows et macOS.
