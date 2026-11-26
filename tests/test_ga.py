import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from puzzle import load_puzzle, make_mask, is_valid, respects_fixed
from fitness import fitness
from ga import run_ga
from test_puzzle import SOLUTION

CHEMIN = os.path.join(os.path.dirname(__file__), "..", "data", "puzzle.txt")
PETIT = {"pop_size": 60, "max_gen": 30}


def _puzzle():
    p = load_puzzle(CHEMIN)
    return p, make_mask(p)


def test_run_ga_renvoie_le_bon_format():
    p, m = _puzzle()
    grille, nb_gen, hist = run_ga(p, {"seed": 1, **PETIT})
    assert len(grille) == 9 and all(len(l) == 9 for l in grille)
    assert isinstance(nb_gen, int) and nb_gen <= PETIT["max_gen"]
    assert len(hist) == nb_gen + 1
    assert hist[-1] == fitness(grille)


def test_historique_ne_remonte_jamais_grace_a_l_elitisme():
    p, m = _puzzle()
    _, _, hist = run_ga(p, {"seed": 2, **PETIT})
    assert all(hist[i + 1] <= hist[i] for i in range(len(hist) - 1))


def test_meme_graine_meme_resultat():
    p, m = _puzzle()
    a = run_ga(p, {"seed": 3, **PETIT})
    b = run_ga(p, {"seed": 3, **PETIT})
    assert a == b


def test_le_resultat_respecte_lignes_et_chiffres_fixes():
    p, m = _puzzle()
    grille, _, _ = run_ga(p, {"seed": 4, **PETIT})
    assert all(sorted(l) == list(range(1, 10)) for l in grille)
    assert respects_fixed(grille, p, m)


def test_le_puzzle_n_est_pas_modifie():
    p, m = _puzzle()
    copie = [l[:] for l in p]
    run_ga(p, {"seed": 5, **PETIT})
    assert p == copie


def test_callback_appele_a_chaque_generation_avec_une_copie():
    p, m = _puzzle()
    appels = []
    grille, nb_gen, _ = run_ga(p, {"seed": 6, **PETIT},
                               callback=lambda g, b, f: appels.append((g, b, f)))
    assert [a[0] for a in appels] == list(range(nb_gen + 1))
    assert appels[-1][2] == fitness(grille)
    appels[0][1][0][0] = 99          # modifier la copie ne doit rien casser
    assert grille[0][0] != 99


def test_une_exception_du_callback_arrete_l_algorithme():
    class Stop(Exception):
        pass

    def cb(gen, best, note):
        if gen == 3:
            raise Stop()

    p, m = _puzzle()
    try:
        run_ga(p, {"seed": 7, **PETIT}, callback=cb)
        assert False, "l'exception du callback a été avalée"
    except Stop:
        pass


def test_toute_solution_trouvee_est_la_bonne():
    p, m = _puzzle()
    for seed in range(4):
        grille, _, hist = run_ga(p, {"seed": seed, "pop_size": 100, "max_gen": 60})
        if hist[-1] == 0:
            assert is_valid(grille) and grille == SOLUTION


def test_les_parametres_par_defaut_sont_completes():
    p, m = _puzzle()
    grille, nb_gen, hist = run_ga(p, {"max_gen": 2, "pop_size": 20})   # aucune autre clé
    assert nb_gen <= 2 and len(hist) == nb_gen + 1