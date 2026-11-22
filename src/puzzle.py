#Chargement et vérification d'une grille de Sudoku  deja declare dans data/puzzle.txt

#load_puzzle transforme le texte en une liste de listes
def load_puzzle(path):
    #Lit un fichier texte : 9 lignes de 9 chiffres (0 = case vide)
    grid = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:  # on ignore les lignes vides
                grid.append([int(c) for c in line.split()])
    return grid

#Le masque dit quelles cases on n'a pas le droit de changer les chiffres deja declares.
#L'AG de Y a besoin du masque pour savoir où il peut modifier.
def make_mask(puzzle):
    #Masque : True si la case est fixe (chiffre donné), False si elle est libre on peut la modifier.
    return [[v != 0 for v in row] for row in puzzle]

#cette fonction est utilisée pour vérifier si une grille est valide (complète et respectant les règles du Sudoku) et si elle respecte les cases fixes du puzzle initial.
"""Un « groupe » est une ligne, une colonne ou un bloc, soit 9 chiffres. 
   Il est correct s'il contient 1, 2, 3... 9 sans doublon.
   On trie les 9 chiffres et on regarde s'ils donnent exactement 1 à 9."""
def _groupe_ok(valeurs):
    #Un groupe (ligne, colonne ou bloc) est correct s'il contient 1..9 une seule fois.
    return sorted(valeurs) == list(range(1, 10))

"""Règle du Sudoku : dans chaque ligne, chaque colonne et chaque bloc 3×3, 
   il faut les chiffres 1 à 9, chacun une seule fois."""
def is_valid(grid):
    #True si la grille est complète et respecte les règles du Sudoku.
    # 9 lignes
    for i in range(9):
        if not _groupe_ok(grid[i]):
            return False
    # 9 colonnes
    for j in range(9):
        if not _groupe_ok([grid[i][j] for i in range(9)]):
            return False
    # 9 sous-grilles 3x3
    for bi in range(0, 9, 3):
        for bj in range(0, 9, 3):
            bloc = [grid[i][j] for i in range(bi, bi + 3) for j in range(bj, bj + 3)]
            if not _groupe_ok(bloc):
                return False
    return True #On arrive ici seulement si aucun des 27 groupes n'a renvoyé False


def respects_fixed(grid, puzzle, mask):
    #True si toutes les cases fixes ont gardé leur valeur de départ.
    # Vérifie que les chiffres donnés au départ n'ont pas été modifiés.
    # grid = grille à tester, puzzle = grille de départ, mask = cases fixes (True)
    for i in range(9): # on parcourt les 9 lignes
        for j in range(9): # et les 9 colonnes de chaque ligne
             # si la case est fixe ET que sa valeur a changé par rapport au départ
            if mask[i][j] and grid[i][j] != puzzle[i][j]:
                return False # un chiffre donné a été modifié : on s'arrête
    return True               # aucune case fixe modifiée : c'est bon