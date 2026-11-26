import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from puzzle import load_puzzle, make_mask
from encoding import create_individual, init_population
from fitness import fitness
from operators import tournament, crossover, mutate

CHEMIN = os.path.join(os.path.dirname(__file__), "..", "data", "puzzle.txt")


def _donnees():
    p = load_puzzle(CHEMIN)
    return p, make_mask(p)


def _lignes_ok(g):
    return all(sorted(l) == list(range(1, 10)) for l in g)


def _fixes_ok(g, p, m):
    return all(g[i][j] == p[i][j] for i in range(9) for j in range(9) if m[i][j])


def test_tournoi_taille_totale_donne_le_meilleur():
    p, m = _donnees()
    rng = random.Random(1)
    pop = init_population(30, p, m, rng)
    fits = [fitness(g) for g in pop]
    gagnant = tournament(pop, fits, len(pop), rng)
    assert fitness(gagnant) == min(fits)


def test_tournoi_renvoie_un_membre_de_la_population():
    p, m = _donnees()
    rng = random.Random(2)
    pop = init_population(30, p, m, rng)
    fits = [fitness(g) for g in pop]
    for _ in range(50):
        assert tournament(pop, fits, 3, rng) in pop


def test_croisement_chaque_ligne_vient_d_un_parent():
    p, m = _donnees()
    rng = random.Random(3)
    a = create_individual(p, m, rng); b = create_individual(p, m, rng)
    for _ in range(100):
        e = crossover(a, b, rng)
        for i in range(9):
            assert e[i] == a[i] or e[i] == b[i]


def test_croisement_garde_lignes_et_chiffres_fixes():
    p, m = _donnees()
    rng = random.Random(4)
    a = create_individual(p, m, rng); b = create_individual(p, m, rng)
    for _ in range(100):
        e = crossover(a, b, rng)
        assert _lignes_ok(e) and _fixes_ok(e, p, m)


def test_croisement_enfant_independant_des_parents():
    p, m = _donnees()
    rng = random.Random(5)
    a = create_individual(p, m, rng); b = create_individual(p, m, rng)
    copie_a = [l[:] for l in a]; copie_b = [l[:] for l in b]
    e = crossover(a, b, rng)
    for i in range(9):
        for j in range(9):
            e[i][j] = 0
    assert a == copie_a and b == copie_b


def test_mutation_pm_zero_ne_change_rien():
    p, m = _donnees()
    rng = random.Random(6)
    g = create_individual(p, m, rng)
    avant = [l[:] for l in g]
    assert mutate(g, m, 0.0, rng) == avant


def test_mutation_garde_lignes_et_chiffres_fixes():
    p, m = _donnees()
    rng = random.Random(7)
    for _ in range(1000):
        g = create_individual(p, m, rng)
        mutate(g, m, 1.0, rng)
        assert _lignes_ok(g) and _fixes_ok(g, p, m)


def test_mutation_change_exactement_deux_cases_d_une_ligne():
    p, m = _donnees()
    rng = random.Random(8)
    for _ in range(200):
        g = create_individual(p, m, rng)
        avant = [l[:] for l in g]
        mutate(g, m, 1.0, rng)
        diff = [(i, j) for i in range(9) for j in range(9) if g[i][j] != avant[i][j]]
        assert len(diff) == 2 and diff[0][0] == diff[1][0]


def test_mutation_meme_graine_meme_resultat():
    p, m = _donnees()
    g1 = create_individual(p, m, random.Random(1)); g2 = [l[:] for l in g1]
    mutate(g1, m, 1.0, random.Random(9)); mutate(g2, m, 1.0, random.Random(9))
    assert g1 == g2