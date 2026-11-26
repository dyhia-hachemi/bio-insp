"""
test_puzzle.py est un fichier qui vérifie automatiquement que les  fonctions deja declarees marchent
pour assurer que puzzle.py n'a pas de bug

"""



import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from puzzle import load_puzzle, make_mask, is_valid, respects_fixed

CHEMIN = os.path.join(os.path.dirname(__file__), "..", "data", "puzzle.txt")

# Une solution connue de notre grille (trouvée par un solveur classique)
SOLUTION = [
    [5, 9, 2, 6, 3, 1, 7, 4, 8],
    [7, 4, 6, 5, 9, 8, 2, 1, 3],
    [8, 1, 3, 7, 4, 2, 5, 9, 6],
    [1, 3, 8, 9, 5, 7, 4, 6, 2],
    [4, 2, 7, 3, 8, 6, 9, 5, 1],
    [6, 5, 9, 1, 2, 4, 3, 8, 7],
    [3, 6, 4, 2, 1, 5, 8, 7, 9],
    [2, 7, 5, 8, 6, 9, 1, 3, 4],
    [9, 8, 1, 4, 7, 3, 6, 2, 5],
]


def test_load_puzzle():
    p = load_puzzle(CHEMIN)
    assert len(p) == 9 and all(len(r) == 9 for r in p)
    assert p[0][2] == 2          # premier chiffre donné
    assert p[0][0] == 0          # case vide


def test_make_mask():
    p = load_puzzle(CHEMIN)
    m = make_mask(p)
    assert m[0][2] is True and m[0][0] is False


def test_solution_est_valide():
    assert is_valid(SOLUTION)


def test_grille_vide_invalide():
    assert not is_valid(load_puzzle(CHEMIN))


def test_doublon_detecte():
    g = [r[:] for r in SOLUTION]
    g[0][0], g[0][1] = g[0][1], g[0][0]   # échange : lignes OK, colonnes cassées
    assert not is_valid(g)


def test_respects_fixed():
    p = load_puzzle(CHEMIN)
    m = make_mask(p)
    assert respects_fixed(SOLUTION, p, m)
    g = [r[:] for r in SOLUTION]
    g[0][2] = 9                            # on casse une case fixe
    assert not respects_fixed(g, p, m)