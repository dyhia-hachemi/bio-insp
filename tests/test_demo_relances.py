import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from puzzle import load_puzzle, make_mask
from demo import lancer_demo
from test_puzzle import SOLUTION

CHEMIN = os.path.join(os.path.dirname(__file__), "..", "data", "puzzle.txt")


def _donnees():
    p = load_puzzle(CHEMIN)
    return p, make_mask(p)


def _faux_ga(reussit_a_partir_de, graines_vues):
    """Faux AG : échoue tant que la graine est < reussit_a_partir_de."""
    def run_ga(puzzle, params, callback=None):
        graines_vues.append(params["seed"])
        if callback:
            callback(0, SOLUTION if params["seed"] >= reussit_a_partir_de else puzzle, 3)
        if params["seed"] >= reussit_a_partir_de:
            return SOLUTION, 5, [3, 0]
        return puzzle, 5, [3, 3]
    return run_ga


def test_relance_avec_graines_successives_jusqu_a_la_solution(capsys):
    p, m = _donnees()
    vues = []
    ok = lancer_demo(_faux_ga(42, vues), p, m, {"seed": 40}, max_time=5, max_essais=None)
    assert ok is True and vues == [40, 41, 42]


def test_une_seule_tentative_par_defaut(capsys):
    p, m = _donnees()
    vues = []
    ok = lancer_demo(_faux_ga(99, vues), p, m, {"seed": 1}, max_time=5)
    assert ok is False and vues == [1]


def test_nombre_maximal_d_essais(capsys):
    p, m = _donnees()
    vues = []
    ok = lancer_demo(_faux_ga(99, vues), p, m, {"seed": 7}, max_time=5, max_essais=3)
    assert ok is False and vues == [7, 8, 9]


def test_reussite_immediate_ne_relance_pas(capsys):
    p, m = _donnees()
    vues = []
    ok = lancer_demo(_faux_ga(0, vues), p, m, {"seed": 3}, max_time=5, max_essais=None)
    assert ok is True and vues == [3]


def test_limite_de_temps_arrete_les_relances(capsys):
    p, m = _donnees()
    vues = []
    ok = lancer_demo(_faux_ga(10**9, vues), p, m, {"seed": 0}, max_time=-1, max_essais=None)
    assert ok is False and len(vues) == 1