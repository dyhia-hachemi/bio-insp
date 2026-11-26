import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from puzzle import load_puzzle, make_mask, is_valid
from encoding import create_individual
from fitness import fitness
from test_puzzle import SOLUTION

CHEMIN = os.path.join(os.path.dirname(__file__), "..", "data", "puzzle.txt")


def test_solution_a_zero_erreur():
    assert fitness(SOLUTION) == 0


def test_individu_aleatoire_a_des_erreurs():
    p = load_puzzle(CHEMIN); m = make_mask(p)
    g = create_individual(p, m, random.Random(1))
    assert fitness(g) > 0


def test_echange_dans_une_ligne_cree_des_erreurs():
    g = [r[:] for r in SOLUTION]
    g[0][0], g[0][1] = g[0][1], g[0][0]
    assert fitness(g) > 0


def test_un_seul_doublon_donne_peu_d_erreurs():
    g = [r[:] for r in SOLUTION]
    g[0][0], g[0][1] = g[0][1], g[0][0]
    assert 0 < fitness(g) < 10


def test_fitness_nulle_equivaut_a_grille_valide():
    rng = random.Random(5)
    for _ in range(50):
        g = [r[:] for r in SOLUTION]
        i = rng.randrange(9)
        a, b = rng.sample(range(9), 2)
        g[i][a], g[i][b] = g[i][b], g[i][a]
        assert (fitness(g) == 0) == is_valid(g)


def test_fitness_ne_modifie_pas_la_grille():
    g = [r[:] for r in SOLUTION]
    copie = [r[:] for r in g]
    fitness(g)
    assert g == copie