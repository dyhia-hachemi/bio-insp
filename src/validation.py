def verifier_puzzle(puzzle):
    """Renvoie la liste des problèmes de la grille de départ 
    liste vide = grille correcte."""
    problemes = []

    # forme : 9 lignes de 9 entiers entre 0 et 9
    if not isinstance(puzzle, list) or len(puzzle) != 9:
        return ["la grille doit avoir 9 lignes"]
    for i, ligne in enumerate(puzzle, start=1):
        if not isinstance(ligne, list) or len(ligne) != 9:
            problemes.append(f"la ligne {i} doit avoir 9 cases")
        elif any((not isinstance(v, int)) or v < 0 or v > 9 for v in ligne):
            problemes.append(f"la ligne {i} contient une valeur qui n'est pas un chiffre de 0 à 9")
    if problemes:
        return problemes

    # pas de doublon parmi les chiffres déjà placés
    def doublons(valeurs):
        vus, repetes = set(), set()
        for v in valeurs:
            if v != 0:
                (repetes if v in vus else vus).add(v)
        return sorted(repetes)

    for i in range(9):
        for v in doublons(puzzle[i]):
            problemes.append(f"ligne {i + 1} : le chiffre {v} apparaît plusieurs fois")
    for j in range(9):
        for v in doublons([puzzle[i][j] for i in range(9)]):
            problemes.append(f"colonne {j + 1} : le chiffre {v} apparaît plusieurs fois")
    for bi in range(0, 9, 3):
        for bj in range(0, 9, 3):
            bloc = [puzzle[i][j] for i in range(bi, bi + 3) for j in range(bj, bj + 3)]
            for v in doublons(bloc):
                problemes.append(
                    f"bloc (ligne {bi // 3 + 1}, colonne {bj // 3 + 1}) : "
                    f"le chiffre {v} apparaît plusieurs fois")
    return problemes