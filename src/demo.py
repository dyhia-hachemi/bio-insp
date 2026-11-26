"""Démonstration de l'algorithme génétique pour le Sudoku.

Lance l'AG sur une grille, affiche la progression par génération, puis
contrôle le résultat. Si une tentative n'aboutit pas, la démo relance
automatiquement avec la graine suivante (graine, graine+1, ...) jusqu'à
trouver une solution ou atteindre la limite de temps. Pour une grille et une
graine de départ données, la suite des tentatives est toujours la même.
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


def lancer_demo(run_ga, puzzle, mask, params, max_time=60, pas=10,
                max_gen_par_essai=None, max_essais=1):
    """Lance l'AG, affiche la progression, puis le résultat contrôlé.

    max_essais = 1 : une seule tentative (comportement d'origine).
    max_essais = None : on relance avec la graine suivante, sans limite de
    nombre, jusqu'à la solution ou la limite de temps (max_time).
    max_gen_par_essai : nombre maximal de générations d'une tentative.
    """
    debut = time.time()
    # meilleure grille vue sur l'ensemble des tentatives (si on coupe l'AG)
    meilleur = {"grid": None, "gen": 0, "fit": None, "essai": 0, "graine": None}
    courant = {"essai": 0, "graine": None}
    graine_depart = params.get("seed")
    relances = max_essais != 1

    def callback(gen, best_grid, best_fitness):
        if meilleur["fit"] is None or best_fitness < meilleur["fit"]:
            meilleur.update(grid=best_grid, gen=gen, fit=best_fitness,
                            essai=courant["essai"], graine=courant["graine"])
        if gen % pas == 0 or best_fitness == 0:
            print(f"Génération {gen:5d} | erreurs (fitness) = {best_fitness:3d}"
                  f" | {time.time() - debut:5.1f} s")
        if time.time() - debut > max_time:
            raise TempsEcoule()

    afficher_grille(puzzle, mask, "Grille de départ :")
    print()

    essai = 0
    grille, nb_gen, graine = None, 0, graine_depart
    try:
        while True:
            essai += 1
            p = dict(params)
            if graine_depart is not None:
                graine = graine_depart + essai - 1
                p["seed"] = graine
            if max_gen_par_essai:
                p["max_gen"] = max_gen_par_essai
            courant.update(essai=essai, graine=graine)
            if relances:
                print(f"--- Tentative {essai} (graine {graine}) ---")
            grille, nb_gen, _ = run_ga(puzzle, p, callback=callback)
            if is_valid(grille) and respects_fixed(grille, puzzle, mask):
                break
            if max_essais is not None and essai >= max_essais:
                break
            print("Pas de solution cette fois : on relance avec la graine suivante.\n")
    except TempsEcoule:
        print(f"\nLimite de {max_time} s atteinte : on affiche la meilleure grille trouvée.")
        grille, nb_gen = meilleur["grid"], meilleur["gen"]
        essai, graine = meilleur["essai"], meilleur["graine"]

    duree = time.time() - debut
    print()
    detail = f"tentative {essai}, graine {graine}, " if relances else ""
    afficher_grille(grille, mask,
                    f"Grille finale ({detail}{nb_gen} générations, {duree:.1f} s) :")

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
    parser.add_argument("--seed", type=int, default=0,
                        help="graine de départ (les relances utilisent seed+1, seed+2, ...)")
    parser.add_argument("--max-time", type=float, default=60, help="limite de temps (s)")
    parser.add_argument("--gen-par-essai", type=int, default=300,
                        help="nombre maximal de générations d'une tentative")
    parser.add_argument("--puzzle", default=os.path.join(
        os.path.dirname(__file__), "..", "data", "puzzle.txt"))
    args = parser.parse_args()

    from ga import run_ga

    try:
        puzzle = load_puzzle(args.puzzle)
    except (OSError, ValueError) as e:
        print("Impossible de lire la grille :", e)
        return
    from validation import verifier_puzzle
    problemes = verifier_puzzle(puzzle)
    if problemes:
        print("Grille de départ invalide :")
        for pb in problemes:
            print(" -", pb)
        return
    mask = make_mask(puzzle)
    print("Graine de départ :", args.seed,
          "(en cas d'échec, la démo relance avec la graine suivante)\n")
    params = {"seed": args.seed}
    lancer_demo(run_ga, puzzle, mask, params, max_time=args.max_time,
                max_gen_par_essai=args.gen_par_essai, max_essais=None)


if __name__ == "__main__":
    main()