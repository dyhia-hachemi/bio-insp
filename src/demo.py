"""Test de demo.py SANS le vrai algorithme génétique de Y.

On utilise un "faux AG" : il ne cherche rien, il renvoie directement
une solution connue et appelle le callback comme le vrai AG le ferait.
Ça permet de vérifier l'affichage et le contrôle final de demo.py.
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from puzzle import load_puzzle, make_mask, is_valid, respects_fixed

# Codes couleur du terminal (ANSI)
CYAN = "\033[96m"    # cases fixes
GRIS = "\033[90m"    # séparateurs
RESET = "\033[0m"

os.system("")  # active les couleurs ANSI dans le terminal Windows


class TempsEcoule(Exception):
    """Levée dans le callback quand la limite de temps est dépassée."""


def afficher_grille(grid, mask, titre=""):
    """Affiche la grille 9x9. Cases fixes en cyan et en gras, les autres normales."""
    if titre:
        print(titre)
    for i in range(9):
        if i % 3 == 0:
            print(GRIS + "+-------+-------+-------+" + RESET)
        ligne = ""
        for j in range(9):
            if j % 3 == 0:
                ligne += GRIS + "|" + RESET + " "
            v = grid[i][j]
            texte = str(v) if v != 0 else "."
            if mask[i][j]:
                ligne += CYAN + "\033[1m" + texte + RESET + " "   # fixe
            else:
                ligne += texte + " "                                # libre
        print(ligne + GRIS + "|" + RESET)
    print(GRIS + "+-------+-------+-------+" + RESET)


def lancer_demo(run_ga, puzzle, mask, params, max_time=60, pas=10):
    """Lance l'AG, affiche la progression, puis le résultat contrôlé."""
    debut = time.time()
    dernier = {"grid": None, "gen": 0, "fit": None}

    def callback(gen, best_grid, best_fitness):
        # On garde la meilleure grille vue, au cas où on coupe l'AG.
        dernier.update(grid=best_grid, gen=gen, fit=best_fitness)
        if gen % pas == 0 or best_fitness == 0:
            print(f"Génération {gen:5d} | erreurs (fitness) = {best_fitness:3d}"
                  f" | {time.time() - debut:5.1f} s")
        if time.time() - debut > max_time:
            raise TempsEcoule()

    afficher_grille(puzzle, mask, "Grille de départ :")
    print()
    try:
        grille, nb_gen, historique = run_ga(puzzle, params, callback=callback)
    except TempsEcoule:
        print(f"\nLimite de {max_time} s atteinte : on affiche la meilleure grille trouvée.")
        grille, nb_gen = dernier["grid"], dernier["gen"]

    duree = time.time() - debut
    print()
    afficher_grille(grille, mask, f"Grille finale ({nb_gen} générations, {duree:.1f} s) :")

    # Contrôle final : deux vérifications différentes
    ok_regles = is_valid(grille)
    ok_fixes = respects_fixed(grille, puzzle, mask)
    print(f"\nRespecte les règles du Sudoku (is_valid)      : {ok_regles}")
    print(f"Respecte les cases fixes (respects_fixed)     : {ok_fixes}")
    if ok_regles and ok_fixes:
        print("=> SOLUTION TROUVÉE")
    else:
        print("=> Pas de solution complète (il reste des erreurs)")
    return ok_regles and ok_fixes


def main():
    parser = argparse.ArgumentParser(description="Démo AG pour le Sudoku")
    parser.add_argument("--seed", type=int, default=42, help="graine aléatoire")
    parser.add_argument("--max-time", type=float, default=60, help="limite de temps (s)")
    parser.add_argument("--puzzle", default=os.path.join(
        os.path.dirname(__file__), "..", "data", "puzzle.txt"))
    args = parser.parse_args()

    from ga import run_ga  # import ici : le fichier de Y doit exister

    puzzle = load_puzzle(args.puzzle)
    mask = make_mask(puzzle)
    params = {"seed": args.seed}  # TODO: se mettre d'accord avec Y sur les noms des paramètres
    lancer_demo(run_ga, puzzle, mask, params, max_time=args.max_time)


if __name__ == "__main__":
    main()