import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from puzzle import load_puzzle, make_mask
from encoding import create_individual, init_population

CHEMIN = os.path.join(os.path.dirname(__file__), "..", "data", "puzzle.txt")


def _donnees():
    p = load_puzzle(CHEMIN)
    return p, make_mask(p)


def test_chaque_ligne_est_une_permutation():
    p, m = _donnees()
    rng = random.Random(1)
    for _ in range(100):
        g = create_individual(p, m, rng)
        for ligne in g:
            assert sorted(ligne) == list(range(1, 10))


def test_chiffres_fixes_conserves():
    p, m = _donnees()
    rng = random.Random(2)
    for _ in range(100):
        g = create_individual(p, m, rng)
        for i in range(9):
            for j in range(9):
                if m[i][j]:
                    assert g[i][j] == p[i][j]


def test_taille_population():
    p, m = _donnees()
    pop = init_population(50, p, m, random.Random(3))
    assert len(pop) == 50
    assert all(len(g) == 9 and all(len(l) == 9 for l in g) for g in pop)


def test_meme_graine_meme_resultat():
    p, m = _donnees()
    a = init_population(5, p, m, random.Random(42))
    b = init_population(5, p, m, random.Random(42))
    assert a == b


def test_puzzle_non_modifie():
    p, m = _donnees()
    copie = [r[:] for r in p]
    init_population(20, p, m, random.Random(4))
    assert p == copie