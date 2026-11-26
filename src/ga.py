import random

from puzzle import make_mask
from encoding import init_population
from fitness import fitness
from operators import tournament, crossover, mutate

# Valeurs utilisées quand l'appelant ne donne pas un paramètre
PARAMS_PAR_DEFAUT = {
    "seed": None,          # graine aléatoire (None = différent à chaque lancement)
    "pop_size": 300,       # nombre de grilles par génération
    "p_cross": 0.9,        # probabilité de croiser deux parents
    "p_mut": 1.0,          # probabilité qu'un enfant subisse un échange
    "tournament_k": 3,     # nombre de candidats par tournoi
    "elite_frac": 0.05,    # part de la population copiée sans changement
    "max_gen": 1000,       # nombre maximal de générations
}


def _copie(grille):
    """Copie d'une grille."""
    return [ligne[:] for ligne in grille]


def run_ga(puzzle, params=None, callback=None):
    """Algorithme génétique pour le Sudoku.

    Renvoie (meilleure_grille, nb_generations, historique), 
    où historique contient le meilleur nombre d'erreurs de chaque génération.
    callback(gen, meilleure_grille, meilleure_note) est appelé à chaque génération.
    """
    # paramètres : valeurs par défaut
    cfg = dict(PARAMS_PAR_DEFAUT)
    if params:
        cfg.update(params)

    rng = random.Random(cfg["seed"])
    mask = make_mask(puzzle)
    n = cfg["pop_size"]
    n_elite = max(1, int(n * cfg["elite_frac"]))

    pop = init_population(n, puzzle, mask, rng)
    historique = []

    for gen in range(cfg["max_gen"] + 1):
        # évaluer chaque grille et les classer (moins d'erreurs = meilleur)
        notes = [fitness(g) for g in pop]
        ordre = sorted(range(n), key=lambda i: notes[i])
        meilleur = pop[ordre[0]]
        meilleure_note = notes[ordre[0]]
        historique.append(meilleure_note)

        # prévenir la démo (avec une copie de la meilleure grille)
        if callback is not None:
            callback(gen, _copie(meilleur), meilleure_note)

        # arrêt : solution trouvée ou nombre maximal de générations atteint
        if meilleure_note == 0 or gen == cfg["max_gen"]:
            return _copie(meilleur), gen, historique

        # génération suivante : d'abord les élites, copiées telles quelles
        nouvelle_pop = [_copie(pop[i]) for i in ordre[:n_elite]]

        # puis on remplit avec des enfants
        while len(nouvelle_pop) < n:
            p1 = tournament(pop, notes, cfg["tournament_k"], rng)
            p2 = tournament(pop, notes, cfg["tournament_k"], rng)
            if rng.random() < cfg["p_cross"]:
                enfant = crossover(p1, p2, rng)
            else:
                enfant = _copie(p1)
            enfant = mutate(enfant, mask, cfg["p_mut"], rng)
            nouvelle_pop.append(enfant)

        pop = nouvelle_pop