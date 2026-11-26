def _erreurs_groupe(valeurs):
    """
    Nombre d'erreurs d'un groupe de 9 cases :
    9 moins le nombre de chiffres différents. 
    0 = groupe correct.
    """
    return 9 - len(set(valeurs))


def fitness(grid):
    """
    Nombre total d'erreurs dans les colonnes et les blocs 3x3.
    0 = grille valide.
    Plus le nombre est petit, meilleure est la grille.
    """
    total = 0

    # 9 colonnes
    for j in range(9):
        colonne = [grid[i][j] for i in range(9)]
        total += _erreurs_groupe(colonne)

    # 9 blocs 3x3
    for bi in range(0, 9, 3):
        for bj in range(0, 9, 3):
            bloc = [] 
            for i in range (bi, bi + 3):
                for j in range (bj, bj + 3):
                    bloc.append(grid[i][j])
            total += _erreurs_groupe(bloc)

    return total