def create_individual(puzzle, mask, rng):
    """Renvoie une grille 9x9 : chaque ligne est une permutation de 1..9
    qui contient déjà les chiffres fixes du puzzle."""
    grid = []
    for i in range(9):
        # liste des chiffres fixes de la ligne i
        fixes = []
        for j in range(9):
            if mask[i][j] :
                fixes.append(puzzle[i][j])
        
        # liste des chiffres manquants 
        manquants = []
        for v in range (1, 10):
            if v not in fixes:
                manquants.append(v)

        # mélanger les manquants pour avoir le meme resultat avec la graine
        rng.shuffle(manquants)

        # construire la ligne
        ligne = []
        k = 0 # position dans monquants
        for j in range (9):
            if mask[i][j]: # case fixe
                ligne.append(puzzle[i][j]) # garder le chiffre
            else: # case libre
                ligne.append(manquants[k])
                k += 1
        grid.append(ligne)
    return grid

def init_population(n, puzzle, mask, rng):
    """Renvoie une liste de n individus."""
    population = []
    for _ in range(n):
        population.append(create_individual(puzzle, mask,rng))

    return population
   