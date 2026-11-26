## Vérification de grille et démonstration (X)

### Lancer les tests
    pip install pytest
    python -m pytest -q tests

### Comment `demo.py` a été testé
Le vrai algorithme génétique (`ga.py`, par Y) n'était pas encore prêt.
On a donc testé `demo.py` avec un "faux AG" (voir `tests/test_demo.py`) :
- `faux_ga_qui_reussit` renvoie une solution connue -> la démo doit afficher "SOLUTION TROUVÉE"
- `faux_ga_qui_echoue` renvoie la grille de départ -> la démo doit répondre "pas de solution"

### Lancer la démo (quand ga.py existe)
    python src/demo.py --seed 42 --max-time 60

Paramètres : `--seed` (graine aléatoire, pour refaire le même résultat),
`--max-time` (limite de temps en secondes).