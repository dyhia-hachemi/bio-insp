import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from puzzle import load_puzzle
from validation import verifier_puzzle
from ga import run_ga

CHEMIN = os.path.join(os.path.dirname(__file__), "..", "data", "puzzle.txt")


def _p():
    return load_puzzle(CHEMIN)


def test_grille_du_sujet_est_valide():
    assert verifier_puzzle(_p()) == []


def test_doublon_dans_une_ligne():
    p = _p(); p[0][0] = 2            # la ligne 1 contient déjà un 2
    assert any("ligne 1" in m for m in verifier_puzzle(p))


def test_doublon_dans_une_colonne():
    p = _p(); p[3][0] = 8            # 8 déjà présent plus haut dans la colonne 1
    assert any("colonne 1" in m for m in verifier_puzzle(p))


def test_doublon_dans_un_bloc():
    p = _p(); p[1][0] = 8            # 8 déjà présent dans le bloc en haut à gauche
    assert any("bloc" in m for m in verifier_puzzle(p))


def test_mauvaise_forme():
    assert verifier_puzzle(_p()[:8]) != []
    p = _p(); p[0] = p[0][:8]
    assert verifier_puzzle(p) != []
    p = _p(); p[0][0] = 12
    assert verifier_puzzle(p) != []


def test_run_ga_refuse_une_grille_invalide():
    p = _p(); p[0][0] = 2
    try:
        run_ga(p, {"max_gen": 2, "pop_size": 10})
        assert False, "une grille invalide aurait dû être refusée"
    except ValueError as e:
        assert "invalide" in str(e)