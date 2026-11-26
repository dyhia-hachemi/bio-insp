def tournament(pop, fitnesses, k, rng):
    """
    Tire k individus au hasard et renvoie celui qui a le moins d'erreurs.
    """
    # k INDICES différents 
    indices = rng.sample(range(len(pop)), k)
    # l'indice dont le nombre d'erreurs est le plus petit
    meilleur = min(indices, key=lambda i: fitnesses[i])
    return pop[meilleur]


def crossover(p1, p2, rng):
    """
    Renvoie un enfant : chaque ligne vient de p1  de p2 (50 % chacun).
    """
    enfant = []
    for i in range(9):
        source = p1 if rng.random() < 0.5 else p2
        enfant.append(list(source[i]))
    return enfant


def mutate(ind, mask, pm, rng):
    """
    Avec probabilité pm, échange deux cases libres d'une même ligne.
    Modifie ind sur place et le renvoie."""
    # pas de mutation 
    if rng.random() >= pm:
        return ind

    # lignes qui ont au moins 2 cases libres
    lignes = [i for i in range(9)
              if sum(1 for j in range(9) if not mask[i][j]) >= 2]
    if not lignes:
        return ind

    i = rng.choice(lignes)
    libres = [j for j in range(9) if not mask[i][j]]
    a, b = rng.sample(libres, 2)          # deux positions différentes
    ind[i][a], ind[i][b] = ind[i][b], ind[i][a]
    return ind