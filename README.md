# Simulation de quatre écosystèmes forestiers

## Contexte

Cette simulation représente un damier de 12 × 12 cases séparé en quatre zones.
Chaque zone représente un contexte écologique différent et évolue en parallèle.
Un champignon pathogène apparaît dans un arbre contaminé et peut ensuite se
transmettre aux arbres voisins.

Le champignon choisi est fictif, mais il est inspiré de l'armillaire (`Armillaria mellea`), un champignon réel qui peut attaquer les racines et le bois de nombreux arbres. Dans la nature, il se propage notamment par les racines et par des filaments souterrains appelés rhizomorphes.

Les numéros de page renvoient au cours [Intro-ecologie-m2.pdf](Intro-ecologie-m2.pdf)
(les liens `#page=` s'ouvrent directement à la bonne page dans la plupart des lecteurs PDF).

## Fonctionnement de la simulation

- La simulation commence sur un sol nu : les 144 cases sont vides au départ,
  sans arbres, rochers ni rivière.
- La grille de 12 × 12 cases est divisée en quatre quadrants :
  - **Forêt humide** : sol humifère et hydrométrie élevée.
  - **Milieu sec** : sol sableux et hydrométrie faible, facteur limitant.
  - **Montagne** : sol caillouteux et hydrométrie moyenne.
  - **Zone anthropisée** : sol argilo-calcaire et hydrométrie perturbée.
- Quatre espèces peuvent apparaître selon leurs préférences :
  - **Chêne** : sols argilo-calcaires ou limoneux, besoin en eau moyen ;
  - **Hêtre** : sols limoneux ou humifères, préfère les milieux humides ;
  - **Pin** : sols sableux ou caillouteux, résiste aux milieux secs ;
  - **Saule** : sols alluviaux ou humifères, très forte préférence pour l’humidité ;
  - **Bouleau** (pionnier) : colonise les sols nus, les cendres et les trouées, mais vit peu longtemps ;
  - **Robinier faux-acacia** (invasif) : n'apparaît que s'il est introduit, puis se propage par drageons.
- La probabilité d'apparition d'une espèce dépend de l'adéquation entre son
  hydrométrie idéale et celle de la zone, ainsi que du type de sol.
- À chaque étape, les zones appliquent leurs propres probabilités de
  régénération. Les premiers arbres apparaissent donc progressivement, ce qui
  représente une succession écologique sur un sol nu.
- Une fois les arbres apparus, l'utilisateur peut cliquer sur un arbre sain pour
  placer la contamination (y compris pendant la lecture continue).
- À chaque étape, les quatre populations évoluent simultanément :
  maladie, mortalité et régénération sont calculées pour chaque zone.
- La maladie atteint les arbres sains situés directement au nord, au sud, à
  l'est ou à l'ouest d'un arbre malade. Une frontière de zone bloque la
  propagation afin de représenter la fragmentation des habitats.
- La propagation se fait étape par étape : les arbres contaminés pendant une étape propagent la maladie à l'étape suivante.

## Commandes

- **Étape suivante** : avance la simulation d'une seule étape.
- **▶ Lecture / ⏸ Pause** : enchaîne les étapes automatiquement, puis les met en pause.
- **Délai (ms)** : temps entre deux étapes en lecture continue (50 à 2000 ms),
  réglable pendant que la simulation tourne.
- **Recommencer** : arrête la lecture, remet le sol entièrement à nu et relance
  la succession écologique.
- **Feu, Tempête, Sécheresse, Coupe, Invasive, Castor, Mycorhizes** : déclenchent
  immédiatement l'événement correspondant (voir plus bas).
- **Événements aléatoires** (coché par défaut) : à chaque étape, chaque événement
  a une petite probabilité de survenir seul (de 1 à 3 %, réglable dans
  `PROBA_EVENEMENTS`).
- **Journal du damier** (à droite de la grille) : raconte chaque étape, la plus
  récente en haut. Il donne le nombre d'arbres et de malades, puis, zone par
  zone, les pousses (par espèce), les infections, les morts (naturelles ou dues
  à la maladie) et les arbres en feu. Les événements y sont surlignés en orange,
  ainsi que les actions manuelles (contamination d'un arbre, boutons). Les mêmes
  couleurs se retrouvent dans le journal : vert pour les pousses, rouge pour la
  maladie, gris pour les morts, orange pour le feu.

## Ce qui se passe pendant une simulation

### 1. Colonisation d'un sol nu (étapes 0 à ~15)

Au départ, aucun arbre n'est présent. À chaque étape, une case vide a une
probabilité `régénération × fertilité × lumière` de recevoir un arbre. La
**forêt humide** se remplit très vite (environ 15 % de chances par case et par
étape). Les trois autres zones se colonisent beaucoup plus lentement (entre 1 et
3 %). Sur une case sans voisin, le **bouleau** est favorisé : il est souvent le
premier arbre à apparaître, puis il recule (forte mortalité) au profit des
espèces qui s'installent sous couvert.

→ C'est une **succession primaire** : la colonisation d'un milieu vierge
([p. 148](Intro-ecologie-m2.pdf#page=148), § 6.5.1 *Successions écologiques*).

### 2. Tri des espèces selon le milieu

L'espèce qui pousse n'est pas tirée au hasard : elle est pondérée par
l'écart entre son hydrométrie idéale et celle de la zone, et par la
compatibilité de son sol préféré. Après une soixantaine d'étapes, on observe
en moyenne :

| Zone | Arbres vivants (sur 36 cases) | Espèces dominantes |
|------|------------------|--------------------|
| Forêt humide | ≈ 27 | Saule et hêtre (le bouleau, présent au début, a presque disparu) |
| Milieu sec | ≈ 4 à 5 | Pin |
| Montagne | ≈ 5 | Pin |
| Zone anthropisée | ≈ 2 | Chêne et bouleau |

→ Chaque espèce occupe la zone qui correspond le mieux à sa **niche
écologique** ([p. 17](Intro-ecologie-m2.pdf#page=17), § 1.7). Le saule est
**hydrophile**, le chêne et le hêtre plutôt **mésophiles** et le pin
**xérophile** ([p. 55-56](Intro-ecologie-m2.pdf#page=55), § 3.3.3
*Hygrométrie*). Le type de sol (sableux, limoneux, humifère…) correspond aux
**facteurs édaphiques** et à la texture du sol
([p. 61-64](Intro-ecologie-m2.pdf#page=61), § 3.4).

### 3. Équilibre dynamique

La population ne grandit pas indéfiniment. Chaque arbre a une probabilité de
mourir (mortalité de base de la zone). Elle augmente quand l'arbre a plus de
deux voisins (compétition pour la lumière et l'espace). Les cases mortes (†)
peuvent ensuite être recolonisées. Le nombre d'arbres finit par osciller autour
d'une valeur stable propre à chaque zone, sans jamais se figer.

→ Cette valeur correspond à la **capacité de charge** du milieu. La compétition
est un facteur **dépendant de la densité**
([p. 84-85](Intro-ecologie-m2.pdf#page=84), § 4.2 *Régulation des populations* ;
[p. 21](Intro-ecologie-m2.pdf#page=21), § 2.2 *La compétition*). Le cours
rappelle aussi qu'un climax n'est jamais parfaitement stable : c'est un
équilibre dynamique ([p. 148](Intro-ecologie-m2.pdf#page=148)).

### 3 bis. Décomposition du bois mort

Un arbre mort (†) ne disparaît pas d'un coup, et rien ne peut pousser sur son
tronc. Il suit un cycle en trois temps :

1. **† arbre mort** : le tronc est encore là ;
2. **∴ bois pourri** : champignons, bactéries et invertébrés le décomposent ;
3. **◦ humus** : la matière organique enrichit le sol. Une graine y germe
   1,5 fois plus facilement. Si rien n'y pousse, l'humus finit lessivé et
   redevient une case vide (3 % de chances par étape).

À chaque étape, un tronc passe au stade suivant avec une probabilité
`0,05 + 0,25 × hydrométrie`, divisée par deux pendant une sécheresse. Le
bois mort disparaît donc vite en forêt humide (environ 4 étapes par stade). Il
reste bien plus longtemps en milieu sec (environ 10 étapes par stade). À
l'équilibre, le milieu sec contient en moyenne 13 cases de bois mort ou
pourri, contre 7 en forêt humide, qui compte pourtant 7 fois plus d'arbres. Le
bois mort est aussi un **combustible** : le feu s'y propage.

→ Rôle des **décomposeurs**, qui ferment le cycle de la matière
([p. 115](Intro-ecologie-m2.pdf#page=115), § 5.2.3) ; litière forestière,
humus et recyclage des nutriments
([p. 150-151](Intro-ecologie-m2.pdf#page=150)) ; formation de l'humus dans la
pédogenèse ([p. 61-63](Intro-ecologie-m2.pdf#page=61)).

### 4. Introduction de la maladie (clic sur un arbre)

Un arbre cliqué devient malade (affiché avec ×). À chaque étape, il peut
contaminer ses voisins directs selon la `pression_maladie` de la zone. Un arbre
malade meurt plus souvent qu'un arbre sain (+8 % de mortalité).

- Dans la **forêt humide**, les arbres sont serrés et la pression est forte
  (30 %). L'épidémie s'y propage vite et peut décimer une grande partie du
  quadrant.
- Dans le **milieu sec** et en **montagne**, les arbres sont rares et isolés.
  La maladie trouve peu de voisins et s'éteint souvent d'elle-même.

→ C'est du **parasitisme** : le champignon vit aux dépens de son hôte
([p. 21-22](Intro-ecologie-m2.pdf#page=21), § 2.4). C'est aussi le rôle de la
**maladie dans la régulation des populations**, un facteur dont l'effet augmente
avec la densité ([p. 86-90](Intro-ecologie-m2.pdf#page=86), § 4.2.2).

### 5. Fragmentation : la maladie reste dans son quadrant

La contamination ne franchit jamais la limite d'une zone. Les quatre
populations sont donc isolées les unes des autres.

→ Cela illustre l'action humaine qui transforme et découpe les habitats
(**facteur anthropique**, [p. 24-26](Intro-ecologie-m2.pdf#page=24), § 2.7).
La zone anthropisée combine en plus un sol appauvri (fertilité 35 %), une
faible régénération et une forte compétition. Elle reste presque vide : c'est
une **série régressive** liée à l'action humaine
([p. 149](Intro-ecologie-m2.pdf#page=149)).

### 6. Recolonisation après l'épidémie

Les cases libérées par les arbres morts sont recolonisées au fil des étapes.
La population se reconstitue jusqu'à retrouver son équilibre.

→ Il s'agit d'une **succession secondaire**, dans un milieu déjà perturbé
([p. 148](Intro-ecologie-m2.pdf#page=148)).

## Perturbations et nouvelles espèces

Chaque événement peut survenir au hasard ou être déclenché avec son bouton.
Les effets indiqués ont été mesurés sur 100 simulations, sur une forêt à
l'équilibre (environ 39 arbres sur la grille).

### Feu de forêt ✱

Un arbre s'enflamme, plus souvent en milieu sec. À l'étape suivante, il devient
cendres (░) et peut enflammer ses voisins. Ce risque vaut 50 % en forêt humide
et environ 85 % en milieu sec. Le feu **traverse les frontières de zone**. Les
cendres fertilisent le sol (régénération × 1,5) et favorisent le bouleau
pionnier.

À observer : en milieu sec, le feu s'éteint vite par manque de combustible
(environ 2 arbres brûlés). En forêt humide, il trouve beaucoup d'arbres mais
progresse lentement (environ 5 arbres en moyenne, parfois bien plus). Pendant
une sécheresse, il devient beaucoup plus dangereux.

→ Facteur **apériodique** ([p. 14](Intro-ecologie-m2.pdf#page=14)), suivi d'une
**succession secondaire** avec des espèces pionnières
([p. 148](Intro-ecologie-m2.pdf#page=148)).

### Tempête (chablis)

Une bande de deux lignes traverse toute la grille. Chaque arbre y est abattu
avec une probabilité qui dépend de l'exposition au vent de la zone : 90 % en
montagne, 30 % en forêt humide. Les trouées ainsi ouvertes sont recolonisées en
priorité par le bouleau.

→ Le **vent** comme facteur limitant en montagne
([p. 56](Intro-ecologie-m2.pdf#page=56), § 3.3.4) ; zonation altitudinale
([p. 102-103](Intro-ecologie-m2.pdf#page=102)).

### Sécheresse

Pendant 6 étapes, l'hydrométrie de toutes les zones baisse de 35 points, et la
régénération est divisée par deux. Plus une espèce a besoin d'eau, plus sa
mortalité augmente. C'est l'événement le plus brutal : le nombre d'arbres est
**divisé par deux** en 5 étapes, puis il se reconstitue en une vingtaine
d'étapes. Les saules et les hêtres souffrent ; le pin, xérophile, s'en sort.

→ Facteur abiotique « catastrophique », **indépendant de la densité**
([p. 84](Intro-ecologie-m2.pdf#page=84)) ; **valence écologique** : les espèces
sténoèces souffrent plus que les espèces euryèces
([p. 83](Intro-ecologie-m2.pdf#page=83)) ; hygrométrie
([p. 55-56](Intro-ecologie-m2.pdf#page=55)).

### Coupe humaine

Le bloc de 3 × 3 cases le plus boisé d'une zone est coupé à ras (souvent la zone
anthropisée, mais l'homme va là où il y a du bois).

→ **Facteur anthropique** ([p. 24-26](Intro-ecologie-m2.pdf#page=24)) ;
« végétation de substitution » et série régressive
([p. 149-150](Intro-ecologie-m2.pdf#page=149)).

### Espèce invasive : robinier faux-acacia (R)

L'homme introduit deux robiniers dans la zone anthropisée. Le robinier ne se
sème pas comme les autres espèces : il **drageonne**, c'est-à-dire que ses
racines produisent de nouveaux pieds sur les cases libres voisines. Il meurt
moins que les espèces locales et augmente la mortalité des arbres voisins. Il
**franchit les frontières** de zone. En 25 étapes, il passe de 2 à environ 7
pieds en moyenne, et l'invasion continue ensuite.

→ **Compétition interspécifique** et **exclusion compétitive**
([p. 17](Intro-ecologie-m2.pdf#page=17), [p. 21](Intro-ecologie-m2.pdf#page=21)) ;
introduction d'espèces par l'homme
([p. 24-25](Intro-ecologie-m2.pdf#page=24)).

### Castor ◉ (espèce architecte)

Un castor s'installe sur une case libre d'une zone assez humide. À chaque
étape, il abat parfois un arbre voisin. Son barrage augmente l'humidité des
cases autour de lui, jusqu'à +40 points, et cette humidité reste après son
départ (5 % de chances par étape). Les saules sont donc favorisés autour de
l'ancien barrage.

→ **Espèces architectes** ou ingénieurs écosystémiques : le castor est l'exemple
du cours ([p. 94-96](Intro-ecologie-m2.pdf#page=94), § 4.3).

### Mycorhizes (cadre doré)

Un réseau de champignons mutualistes colonise un carré de 3 × 3 cases. Les
arbres de ces cases meurent un peu moins (−3 points) et résistent mieux à la
maladie : la contagion vers eux est divisée par deux. Ce réseau est permanent.

→ **Mutualisme** : les mycorhizes améliorent la nutrition des plantes
([p. 22](Intro-ecologie-m2.pdf#page=22), § 2.5). On peut opposer ce champignon
bénéfique au champignon pathogène (parasitisme, § 2.4).

## Correspondance code ↔ cours

| Élément du code | Notion du cours | Pages |
|-----------------|-----------------|-------|
| Damier = biotope, arbres = biocénose | Écosystème | [11-12](Intro-ecologie-m2.pdf#page=11) |
| `hydrometrie`, `humidite` | Facteur abiotique climatique, hygrométrie | [14](Intro-ecologie-m2.pdf#page=14), [55-56](Intro-ecologie-m2.pdf#page=55) |
| `type_sol`, `fertilite` | Facteurs édaphiques, texture du sol | [61-64](Intro-ecologie-m2.pdf#page=61) |
| `lumiere` (faible en montagne) | Éclairement ; zonation altitudinale | [45](Intro-ecologie-m2.pdf#page=45), [102-103](Intro-ecologie-m2.pdf#page=102) |
| `regeneration × fertilite × lumiere` | Facteurs limitants (loi de Liebig) | [15-16](Intro-ecologie-m2.pdf#page=15) |
| `hydrometrie_ideale`, `sols_favorables` | Niche écologique, valence écologique | [17](Intro-ecologie-m2.pdf#page=17), [83](Intro-ecologie-m2.pdf#page=83) |
| Mortalité accrue avec les voisins (`competition`) | Compétition, régulation dépendante de la densité | [21](Intro-ecologie-m2.pdf#page=21), [84-85](Intro-ecologie-m2.pdf#page=84) |
| `pression_maladie`, `propager_maladie` | Parasitisme, rôle de la maladie | [21-22](Intro-ecologie-m2.pdf#page=21), [86-90](Intro-ecologie-m2.pdf#page=86) |
| Frontières entre quadrants, zone anthropisée | Facteur anthropique, série régressive | [24-26](Intro-ecologie-m2.pdf#page=24), [149](Intro-ecologie-m2.pdf#page=149) |
| Départ sur sol nu, recolonisation | Successions primaire et secondaire | [148-149](Intro-ecologie-m2.pdf#page=148) |
| Chêne et hêtre | Espèces typiques des forêts tempérées caducifoliées | [162](Intro-ecologie-m2.pdf#page=162) |
| `declencher_feu`, `CENDRES`, bouleau `pionniere` | Facteur apériodique, espèces pionnières | [14](Intro-ecologie-m2.pdf#page=14), [148](Intro-ecologie-m2.pdf#page=148) |
| `declencher_tempete`, `exposition_vent` | Le vent | [56](Intro-ecologie-m2.pdf#page=56) |
| `declencher_secheresse` | Facteur indépendant de la densité, valence écologique | [83-84](Intro-ecologie-m2.pdf#page=83) |
| `declencher_coupe` | Facteur anthropique, série régressive | [24-26](Intro-ecologie-m2.pdf#page=24), [149-150](Intro-ecologie-m2.pdf#page=149) |
| Robinier `invasive`, drageons | Compétition, exclusion compétitive | [17](Intro-ecologie-m2.pdf#page=17), [21](Intro-ecologie-m2.pdf#page=21) |
| `activite_castors`, `humidite_bonus` | Espèce architecte | [94-96](Intro-ecologie-m2.pdf#page=94) |
| `mycorhizes` | Mutualisme | [22](Intro-ecologie-m2.pdf#page=22) |
| `BOIS_POURRI`, `HUMUS`, vitesse liée à l'hydrométrie | Décomposeurs, litière et humus | [115](Intro-ecologie-m2.pdf#page=115), [150-151](Intro-ecologie-m2.pdf#page=150) |

## Limites du modèle

Cette règle est une simplification pédagogique. Le modèle ne tient compte ni
des saisons, ni de l'âge des arbres, ni de la température dans la vitesse de
décomposition (seule l'humidité compte).
L'effet des facteurs limitants est calculé comme un produit, et non comme un
véritable minimum au sens de Liebig. Le champ `humidite` est seulement affiché
dans la légende ; c'est `hydrometrie` qui intervient dans les calculs.
Le castor est représenté sans rivière (il s'installe sur une case libre), et le
robinier ne fixe pas l'azote du sol, contrairement au vrai robinier.

## Légende

- C : chêne, H : hêtre, P : pin, S : saule, B : bouleau (pionnier), R : robinier (invasif)
- ✱ orange : arbre en feu ; ░ gris foncé : cendres ; ◉ brun : castor
- Cadre doré : case colonisée par des mycorhizes
- Rouge : arbre contaminé (l'espèce reste indiquée)
- † gris clair : arbre mort ; ∴ beige : bois pourri ; ◦ brun foncé : humus
- Blanc ou couleur pâle : case vide (la couleur indique sa zone)

## Lancer le programme

Depuis le dossier du projet :

```bash
python3 modelisation.py
```

Le programme utilise `tkinter`, généralement inclus avec Python sous Linux, Windows et macOS.
