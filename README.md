# Méthodes bio-inspirées : Sudoku et algorithme génétique

## Sommaire

1. [But du projet](#1-but-du-projet)
2. [Rappel de l'énoncé et correspondance avec le code](#2-rappel-de-lénoncé-et-correspondance-avec-le-code)
3. [Comment fonctionne l'algorithme](#3-comment-fonctionne-lalgorithme)
4. [Choix de conception et justifications](#4-choix-de-conception-et-justifications)
5. [Structure du dépôt et rôle de chaque fichier](#5-structure-du-dépôt-et-rôle-de-chaque-fichier)
6. [Interfaces entre les fichiers (à ne pas casser)](#6-interfaces-entre-les-fichiers-à-ne-pas-casser)
7. [Installation et utilisation](#7-installation-et-utilisation)
8. [Tests](#8-tests)
9. [Résultats mesurés et limites actuelles](#9-résultats-mesurés-et-limites-actuelles)
10. [Guide pour ajouter une amélioration à l'AG](#11-guide-pour-ajouter-une-amélioration-à-lag)
11. [Glossaire](#15-glossaire)

---

## 1. But du projet

On reçoit une grille de Sudoku **partiellement remplie**. Le but est de la **compléter** avec un algorithme génétique de façon à obtenir une grille correcte :

- chaque chiffre de 1 à 9 apparaît **une seule fois** dans chaque ligne, chaque colonne et chaque sous-grille 3×3 ;
- les **chiffres de départ ne sont jamais modifiés**;
- on cherche à y arriver avec **le moins de générations possible**.

### Pourquoi un algorithme génétique pour un Sudoku ?

Un Sudoku se résout instantanément avec un algorithme exact (le retour sur trace). L'intérêt ici est **pédagogique** : le Sudoku est un problème de **contraintes** facile à vérifier, donc un bon banc d'essai pour étudier comment une métaheuristique bio-inspirée gère des contraintes, un très grand espace de recherche et le risque de rester bloquée dans un optimum local. Les mêmes idées servent pour les emplois du temps, la planification ou l'affectation de ressources. La littérature utilise d'ailleurs le Sudoku comme banc d'essai pour les AG (voir la section Références).

## 2. Rappel de l'énoncé et correspondance avec le code

L'énoncé demande d'appliquer l'AG au Sudoku. Le travail demandé et sa réalisation :

| Travail demandé | Où dans le code |
|---|---|
| Écrire une fonction capable de vérifier si une grille est correcte | `src/puzzle.py` : `is_valid` et `respects_fixed` |
| Proposer un codage représentatif des grilles | `src/encoding.py` |
| Proposer une fonction objective | `src/fitness.py` |
| Implémenter la sélection, le croisement et la mutation | `src/operators.py` |
| Essayer d'avoir la solution en un minimum de générations | `src/ga.py` (version de base) ; améliorations et mesures à faire (voir section 10) |
| Réaliser une démonstration de la solution | `src/demo.py` |

## 3. Comment fonctionne l'algorithme

Un AG imite la sélection naturelle : on fait évoluer une **population** de grilles candidates. À chaque **génération** :

```
 population de 300 grilles
          |
          v
 1. ÉVALUER : compter les erreurs de chaque grille (fitness)
          |
          v
 2. ARRÊT ? meilleure grille à 0 erreur, ou max_gen atteint  --> on renvoie la meilleure
          |
          v
 3. ÉLITISME : copier telles quelles les 5 % de meilleures grilles
          |
          v
 4. REMPLIR le reste de la nouvelle population, en répétant :
       - choisir 2 parents (tournoi)
       - les croiser (ligne par ligne)
       - muter l'enfant (échange de 2 cases libres dans une ligne)
          |
          v
 nouvelle génération  -->  retour en 1
```

Pourquoi cela s'améliore : une grille qui a peu d'erreurs a plus de chances d'être choisie comme parent, et ses lignes bien placées passent aux enfants. Le meilleur nombre d'erreurs descend donc de génération en génération, jusqu'à 0.

## 4. Choix de conception et justifications

### 4.1 Le codage : chaque ligne est une permutation de 1 à 9

Un individu est une grille 9×9 (liste de 9 listes de 9 entiers) où **chaque ligne est une permutation de 1 à 9 qui contient déjà les chiffres fixes de cette ligne, à leur place**. Pour fabriquer une ligne : on repère les chiffres fixes, on calcule les chiffres manquants, on les mélange, et on les place dans les cases libres.

Les contraintes sont donc réparties en deux familles :

| Contrainte | Traitement | Où |
|---|---|---|
| Chiffres fixes et unicité dans chaque **ligne** | **Garantie par construction** | codage et opérateurs |
| Unicité dans chaque **colonne** et chaque **bloc 3×3** | **Pénalisée** (comptée comme erreurs) | fonction objective |

**Justifications :**

1. **Le codage n'exclut aucune solution.** Dans un Sudoku valide, chaque ligne est forcément une permutation de 1 à 9 et respecte les chiffres fixes. Toute vraie solution appartient donc à l'espace représenté.
2. **L'espace de recherche est beaucoup plus petit.** Sur la grille du sujet, il y a 46 cases libres. Si chaque case libre pouvait prendre n'importe quel chiffre, il y aurait environ **7,9 × 10⁴³** grilles. Avec notre codage (chaque ligne est une permutation), il y en a environ **1,1 × 10²⁰**, soit environ 10²⁴ fois moins.
3. **C'est simple à construire et le croisement par lignes est naturel** : échanger des lignes entières entre deux parents ne casse jamais le codage.
4. **Le rôle « garanti » aurait pu être joué par les colonnes ou par les blocs** (c'est symétrique). Nous avons choisi les lignes pour la simplicité. Ne rien garantir et tout pénaliser serait possible, mais l'espace de recherche serait bien plus grand.

**Le prix de ce choix :** le croisement et la mutation ne corrigent pas directement les colonnes et les blocs, ce qui explique en partie que l'algorithme se bloque parfois à quelques erreurs (voir section 9).

### 4.2 La fonction objective : nombre d'erreurs (à minimiser)

```
erreurs d'un groupe de 9 cases = 9 - (nombre de chiffres différents du groupe)
fitness(grille) = somme des erreurs des 9 colonnes et des 9 blocs 3×3
```

- **0 erreur = grille valide.** Pour les grilles produites par notre codage, `fitness == 0` est équivalent à `is_valid == True` (les lignes sont déjà correctes). Le test `test_fitness_nulle_equivaut_a_grille_valide` le vérifie.
- On ne compte pas les lignes : le codage les garantit, ce qui économise un tiers du calcul à chaque évaluation.
- **Ordre de grandeur :** sur la grille du sujet, une grille aléatoire a entre 30 et 58 erreurs (environ 43 en moyenne).
- **Limite :** cette fonction n'a de sens que si les lignes restent des permutations. Tout nouvel opérateur doit conserver cet invariant (voir section 11).

### 4.3 Sélection : tournoi de taille 3

On tire `k` grilles au hasard et la meilleure (le moins d'erreurs) gagne. Ce n'est pas toujours la meilleure de toute la population : un peu de hasard est conservé, et `k` règle la sévérité de la sélection.

### 4.4 Croisement : par lignes

Pour chacune des 9 lignes, une pièce décide si l'enfant prend la ligne du parent 1 ou du parent 2. Comme chaque ligne est une permutation avec les chiffres fixes aux mêmes positions chez les deux parents, **toute combinaison de lignes est valide**. Les lignes de l'enfant sont des **copies** (pas de liste partagée avec les parents).

### 4.5 Mutation : échange de deux cases libres dans une ligne

Avec la probabilité `p_mut`, on choisit une ligne ayant au moins deux cases libres, on tire deux de ces cases libres et on échange leurs valeurs. L'échange garde la ligne en permutation et ne touche jamais aux chiffres fixes. Remplacer un chiffre par un autre au hasard créerait un doublon dans la ligne : c'est pourquoi on échange.

### 4.6 Élitisme : 5 % des meilleures grilles passent inchangées

Cela garantit que **le meilleur nombre d'erreurs ne remonte jamais** d'une génération à l'autre (l'historique est décroissant ou constant ; un test le vérifie).

### 4.7 Valeurs par défaut des paramètres

| Clé de `params` | Rôle | Défaut |
|---|---|---|
| `seed` | graine aléatoire (même graine = même exécution) | `None` (aléatoire) |
| `pop_size` | grilles par génération | 300 |
| `p_cross` | probabilité de croiser deux parents | 0,9 |
| `p_mut` | probabilité qu'un enfant subisse un échange | **1,0** |
| `tournament_k` | candidats par tournoi | 3 |
| `elite_frac` | part de la population copiée sans changement | 0,05 |
| `max_gen` | nombre maximal de générations | 1000 |

Ces valeurs de départ sont à **affiner par des expériences** (travail de Z).

### 4.8 La graine aléatoire

Une graine est le point de départ du générateur de nombres aléatoires : **même graine = exactement la même exécution**, sur toutes les machines (nous avons vérifié les mêmes nombres de générations sur deux machines différentes). Ce n'est pas un défaut, c'est un outil :

- graine fixe : tests, rapport reproductible, reproduction d'un problème ;
- graines différentes : mesurer la fiabilité (30 exécutions avec 30 graines) et relancer en cas d'échec.

La graine ne rend pas l'algorithme meilleur : elle fixe seulement *laquelle* des exécutions possibles on observe.

### 4.9 Validation de la grille de départ

Sans contrôle, une grille de départ invalide (par exemple un chiffre en double dans une ligne) ne fait pas planter le programme : elle produit des lignes qui ne sont plus des permutations, et l'algorithme tourne sur des données fausses sans le dire. `verifier_puzzle` refuse donc la grille avec des messages précis (forme 9×9, valeurs de 0 à 9, doublons dans les lignes, colonnes et blocs). `run_ga` lève une `ValueError`, et la démo affiche les problèmes.

**Limite :** une grille qui paraît correcte mais n'a **aucune solution** n'est pas détectée : l'algorithme tournera jusqu'à la limite et affichera les erreurs restantes.

### 4.10 Démo : relances automatiques avec graines successives

Si une tentative n'aboutit pas, la démo relance avec la graine suivante (graine, graine+1, …) jusqu'à la solution ou la limite de temps, avec un nombre limité de générations par tentative (300 par défaut). Le comportement reste **reproductible** (même grille + même graine de départ = même suite de tentatives) et **plus fiable**.

**Attention : ce n'est pas l'optimisation de l'AG.** C'est un redémarrage grossier au niveau de la démo : il augmente la fiabilité, mais il ne réduit pas le nombre de générations d'une exécution. Il abandonne après un nombre fixe de générations même si l'algorithme est bloqué depuis longtemps (la graine 42 reste à 5 erreurs entre les générations 50 et 210). Un redémarrage **déclenché par la stagnation**, dans `run_ga`, est une amélioration à faire (section 10).

## 5. Structure du dépôt et rôle de chaque fichier

```
README.md
data/
    puzzle.txt                 grille du sujet (35 chiffres fixes, solution unique)
    grille_*.txt               grilles de test de difficultés variées (voir section 9)
src/
    puzzle.py                  (X)  chargement, masque, is_valid, respects_fixed
    validation.py              (Y)  verifier_puzzle : contrôle de la grille de départ
    encoding.py                (Y)  codage : individus et population
    fitness.py                 (Y)  fonction objective
    operators.py               (Y)  tournoi, croisement, mutation
    ga.py                      (Y)  boucle principale run_ga
    demo.py                    (X, modifié par Y)  démonstration en terminal
    experiments.py             (Z)  expériences et courbes (à créer)
tests/
    test_puzzle.py             (X)  contient la grille SOLUTION de référence
    test_encoding.py           (Y)
    test_fitness.py            (Y)
    test_operators.py          (Y)
    test_ga.py                 (Y)
    test_validation.py         (Y)
    test_demo_relances.py      (Y)
```

| Fichier | Contenu |
|---|---|
| `puzzle.py` | `load_puzzle` lit un fichier texte ; `make_mask` renvoie les cases fixes ; `is_valid` vérifie les règles du Sudoku ; `respects_fixed` vérifie que les chiffres de départ sont conservés. |
| `validation.py` | `verifier_puzzle(puzzle)` renvoie la liste des problèmes (liste vide = grille correcte). |
| `encoding.py` | `create_individual` fabrique une grille candidate ; `init_population` en fabrique `n`. |
| `fitness.py` | `fitness(grid)` renvoie le nombre d'erreurs (colonnes et blocs). |
| `operators.py` | `tournament`, `crossover`, `mutate`. |
| `ga.py` | `run_ga` : la boucle, l'élitisme, les paramètres par défaut, l'appel du callback, la validation. |
| `demo.py` | Affiche la grille (cases fixes en cyan), la progression par génération, relance en cas d'échec, vérifie le résultat. |
| `tests/test_puzzle.py` | Contient `SOLUTION`, la solution **unique** de `puzzle.txt`, utilisée comme référence par les autres tests. |

## 6. Interfaces entre les fichiers (à ne pas casser)

**Convention de données :** une grille est une **liste de 9 listes de 9 entiers**, avec `0` pour une case vide. Le masque a la même forme, avec `True` pour une case fixe.

```python
# puzzle.py
load_puzzle(path) -> grille
make_mask(puzzle) -> masque
is_valid(grid) -> bool
respects_fixed(grid, puzzle, mask) -> bool

# validation.py
verifier_puzzle(puzzle) -> list[str]            # [] = grille correcte

# encoding.py
create_individual(puzzle, mask, rng) -> grille
init_population(n, puzzle, mask, rng) -> list[grille]

# fitness.py
fitness(grid) -> int                            # nombre d'erreurs, 0 = valide

# operators.py
tournament(pop, fitnesses, k, rng) -> grille    # renvoie un membre de pop
crossover(p1, p2, rng) -> grille                # nouvel enfant (lignes copiées)
mutate(ind, mask, pm, rng) -> ind               # modifie ind sur place et le renvoie

# ga.py
run_ga(puzzle, params=None, callback=None) -> (meilleure_grille, nb_generations, historique)
#   callback(gen, meilleure_grille_copie, meilleure_note) appelé à CHAQUE génération
```

**Règles imposées par la démo et les tests :**

1. `run_ga` calcule le masque lui-même (`make_mask(puzzle)`).
2. Le callback est appelé **à chaque génération**, y compris celle qui trouve 0, avec une **copie** de la meilleure grille.
3. **Ne jamais entourer l'appel du callback d'un `try/except Exception`** : la démo arrête l'algorithme en levant une exception dans le callback quand la limite de temps est dépassée.
4. Tout tirage aléatoire passe par `rng` (`random.Random(seed)`), jamais par le module `random` directement : sinon la graine ne rend plus l'exécution reproductible.
5. `run_ga` n'est jamais censé modifier `puzzle`.
6. `params` peut être partiel : toute clé absente prend sa valeur par défaut.

## 7. Installation et utilisation

**Prérequis :** Python 3 (testé avec Python 3.12) et `pytest` pour les tests (`pip install pytest`). Aucune autre bibliothèque. Toutes les commandes se lancent **depuis la racine du projet**.

### Format d'un fichier de grille

9 lignes, 9 chiffres **séparés par des espaces**, `0` pour une case vide :

```
0 0 2 0 3 1 0 0 8
0 4 0 0 0 0 0 1 3
8 1 0 7 0 0 0 0 0
0 3 0 0 5 0 0 6 2
4 0 7 3 8 6 9 0 1
6 5 0 0 2 0 0 8 0
0 0 0 0 0 5 0 7 9
2 7 0 0 0 0 0 3 0
9 0 0 4 7 0 6 0 0
```

### Lancer la démonstration

```
python src/demo.py                                        # grille du sujet, graine de départ 0
python src/demo.py --seed 42                              # graine 42 : échoue seule, relance, réussit avec la 43
python src/demo.py --puzzle data/grille_moyenne.txt --max-time 60
```

| Option | Rôle | Défaut |
|---|---|---|
| `--seed` | graine de départ (les relances utilisent seed+1, seed+2, …) | 0 |
| `--max-time` | limite de temps totale en secondes | 60 |
| `--gen-par-essai` | générations maximales d'une tentative | 300 |
| `--puzzle` | chemin du fichier de grille | `data/puzzle.txt` |

La démo affiche la grille de départ (chiffres fixes en cyan), la progression, la grille finale, puis deux vérifications : `is_valid` (règles du Sudoku) et `respects_fixed` (chiffres de départ conservés). Si la limite de temps est atteinte, elle affiche la meilleure grille trouvée avec ses erreurs. Si la grille est invalide ou illisible, elle l'explique et s'arrête.

### Utiliser l'AG dans du code

```python
from puzzle import load_puzzle
from ga import run_ga

puzzle = load_puzzle("data/puzzle.txt")
grille, nb_gen, historique = run_ga(puzzle, {"seed": 0, "pop_size": 300, "p_mut": 1.0})
print(nb_gen, historique[-1])        # historique[-1] == 0 : solution trouvée
```

## 8. Tests

```
python -m pytest -q tests          # 46 tests
```

| Fichier de test | Ce qu'il vérifie |
|---|---|
| `test_puzzle.py` | chargement, masque, `is_valid`, `respects_fixed`, solution de référence |
| `test_encoding.py` | lignes en permutations, chiffres fixes conservés, taille de la population, même graine = même résultat, puzzle non modifié |
| `test_fitness.py` | solution à 0 erreur, individus aléatoires à plus de 0, un échange crée des erreurs, **fitness = 0 équivaut à `is_valid`**, grille non modifiée |
| `test_operators.py` | tournoi (meilleur de la population si `k` = taille), croisement (lignes issues d'un parent, **enfant indépendant**, codage conservé), mutation (`pm = 0` ne change rien, exactement 2 cases d'une même ligne, chiffres fixes et permutations conservés sur 1000 mutations) |
| `test_ga.py` | format du résultat, historique décroissant (élitisme), reproductibilité, résultat conforme au codage, puzzle non modifié, callback à chaque génération avec copie, **exception du callback non avalée**, toute solution trouvée est la bonne, paramètres par défaut complétés |
| `test_validation.py` | grille du sujet valide, doublons ligne/colonne/bloc, mauvaise forme, `run_ga` refuse une grille invalide |
| `test_demo_relances.py` | relances avec graines successives (faux AG), une seule tentative par défaut, limite du nombre d'essais, limite de temps |

## 9. Résultats mesurés et limites actuelles

> **Ces mesures sont indicatives** : un seul passage, sur une seule machine, avec peu de graines. Z doit les refaire proprement avec `experiments.py` (30 graines ou plus par configuration) avant de les utiliser dans le rapport.

### 9.1 Version de base, grille du sujet : effet de `p_mut`

16 graines (0 à 15), population 300, 600 générations maximum :

| `p_mut` | Réussites | Générations des réussites |
|---|---|---|
| 0,2 | 1 sur 16 | 36 |
| 0,5 | 3 sur 16 | 78, 250, 348 |
| 1,0 | **8 sur 16** | 34, 38, 45, 55, 63, 78, 313, 467 |

Les exécutions qui échouent restent bloquées à **2 à 7 erreurs**. C'est le comportement classique de cette famille d'algorithmes : la descente est rapide (de 31 erreurs à 2 en 30 générations environ), puis l'algorithme stagne.

### 9.2 Démo avec relances, selon la difficulté de la grille

300 générations par tentative, graines de départ 0, 1, 2… ; limite d'environ 35 secondes par grille.

| Fichier | Chiffres fixes | Résultat |
|---|---|---|
| `grille_tres_facile.txt` | 48 | solution à la 1re tentative, 0,1 s |
| `grille_facile.txt` | 40 | solution à la 1re tentative, 0,5 s |
| `puzzle.txt` (sujet) | 35 | solution à la 1re tentative avec la graine 0 (55 générations) |
| `grille_moyenne.txt` | 32 | solution à la 7e tentative, 17 s |
| `grille_wikipedia.txt` | 30 | solution à la 4e tentative, 9,7 s |
| `grille_difficile.txt` | 26 | **pas de solution en 14 tentatives** (37 s) |
| `grille_tres_difficile.txt` | 24 | **pas de solution en 13 tentatives** (35 s) |
| `grille_extreme_17.txt` | 17 | pas de solution dans un essai court (3 tentatives, 8 s) |

Les cinq grilles `tres_facile`, `facile`, `moyenne`, `difficile` et `tres_difficile` ont été générées à partir de la solution du sujet (chiffres permutés, lignes et blocs mélangés) puis creusées en vérifiant avec un solveur que la **solution reste unique**. `grille_wikipedia.txt` est un exemple classique de 30 chiffres. `grille_extreme_17.txt` est une grille de 17 chiffres connue pour sa difficulté ; son unicité n'a pas été vérifiée ici.

### 9.3 Limites connues

- **La version de base ne garantit pas la solution** : elle réussit environ une fois sur deux sur la grille du sujet, et échoue en dessous d'environ 30 chiffres fixes.
- Le blocage à quelques erreurs vient en partie du codage : les opérateurs ne corrigent pas directement les colonnes et les blocs.
- Une grille valide mais **sans solution** n'est pas détectée.
- La grille de départ est supposée avoir ses chiffres fixes cohérents : `verifier_puzzle` le contrôle, mais pas l'existence d'une solution.

## 10. Guide pour ajouter une amélioration à l'AG

1. **Ne changez pas les signatures** de la section 6. Si un paramètre est nécessaire, ajoutez une clé à `PARAMS_PAR_DEFAUT` dans `ga.py`.
2. **Par défaut, la fonctionnalité doit être désactivée** (par exemple `"restart_stagnation": None`) : sans option, `run_ga` doit se comporter exactement comme la version de base, et les 46 tests doivent continuer à passer.
3. **Respectez les invariants du codage** : après tout opérateur, chaque ligne doit rester une permutation de 1 à 9 et les chiffres fixes ne doivent pas bouger. Sinon `fitness` n'a plus de sens. Ajoutez un test dans `tests/` pour tout nouvel opérateur (par exemple 1000 appels aléatoires avec vérification des lignes et des chiffres fixes).
4. **Tout le hasard passe par `rng`**, jamais par `random` directement.
5. **Comparez avec la version de base sur les mêmes graines et les mêmes grilles** : une amélioration doit être mesurée, pas supposée.
6. **Une branche par amélioration** (`feature/restart-stagnation`, etc.), pull request relue par une autre personne.
7. Documentez le résultat dans ce README (section 9) 

## 11. Glossaire

- **Individu** : une grille candidate.
- **Population** : l'ensemble des grilles d'une génération.
- **Génération** : un tour complet d'évaluation, de sélection, de croisement et de mutation.
- **Fitness / fonction objective** : la note d'une grille ; ici le nombre d'erreurs, à minimiser.
- **Sélection par tournoi** : tirer quelques grilles au hasard et garder la meilleure.
- **Croisement** : fabriquer un enfant à partir de deux parents.
- **Mutation** : petite modification aléatoire d'un enfant.
- **Élitisme** : copier les meilleures grilles sans les modifier.
- **Graine (seed)** : point de départ du générateur aléatoire ; même graine = même exécution.
- **Masque** : grille de booléens indiquant les cases fixes.
- **Stagnation** : le meilleur nombre d'erreurs ne diminue plus pendant plusieurs générations.
- **Redémarrage** : repartir d'une nouvelle population quand l'algorithme est bloqué.
- **Optimum local** : une grille presque correcte dont on ne peut plus s'approcher du 0 par de petites modifications.
