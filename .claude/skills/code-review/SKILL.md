---
name: code-review
description: Effectue une code review structurée par sévérité. Déclencher quand l'utilisateur dit "review", "relis ce code", "vérifie ce PR", "est-ce que c'est correct", ou avant un merge qui touche le contrat CLI, le format de sortie, le calcul des chemins ou les dépendances.
---

# Code Review

Review security-first, findings classés par sévérité, guidance de remédiation
actionnable.

## Priorités

- **Critique** : écrasement ou perte de fichier non voulu (source ou sortie),
  vulnérabilité, rupture de contrat (arguments CLI, codes de sortie, format du
  Markdown produit), exception qui interrompt un batch entier.
- **Important** : tests manquants sur un chemin risqué, régression de
  performance sur gros fichiers, dérive d'architecture, doc désynchronisée.
- **Suggestion** : lisibilité, nommage, cohérence, maintenabilité.

## Ce qu'il faut vérifier

### Correctness
- Le comportement correspond aux exigences et préserve les contrats existants.
- Edge cases : fichier vide, PDF scanné (texte vide), extension en majuscules,
  fichier temporaire Word (`~$*.docx`), chemin avec espaces ou accents,
  `-o` vers un dossier inexistant, deux sources de même nom (`a.docx` et
  `a.pdf`) qui visent le même `.md`.

### Invariants md_iator (chacun = Critique s'il est violé)
- Codes de sortie : `0` seulement si tout a réussi, `1` sinon.
- Batch : une erreur sur un fichier est écrite sur stderr et le batch continue.
- Format PDF : `## Page N` par page, séparateur `---`.
- Calcul du chemin de sortie : à côté de la source sans `-o` ; arborescence
  miroir sous `-o` en batch ; dossier parent créé automatiquement.
- Le fichier source n'est jamais modifié.
- Nouvelle dépendance déclarée à la fois dans `pyproject.toml` et
  `requirements.txt`.

### Sécurité
- Pas de `subprocess` avec `shell=True` ni de chemin utilisateur interpolé dans
  une commande shell.
- Pas d'exécution ni d'évaluation de contenu extrait des documents.
- Chemins construits avec `pathlib`, pas par concaténation de chaînes.
- Téléchargement de binaire (pandoc) uniquement via `pypandoc`, pas d'URL
  maison.
- Pas de secret ni de contenu de document dans les logs au-delà du nécessaire.

### Performance
- Pas de chargement inutile d'un document entier en mémoire quand un
  traitement page par page suffit.
- Pas de travail coûteux répété par fichier dans une boucle de batch quand il
  peut être fait une fois (ex : vérification de pandoc).
- Sorties dans une boucle `tqdm` via `bar.write`, pas `print`.

### Tests et docs
- Nouveau comportement et bug fixes couverts dans `tests/`, sans réseau ni
  vrai pandoc (fixtures de `tests/conftest.py`).
- `README.md`, `docs/usage.md` et `CLAUDE.md` à jour si un argument, un format,
  un message ou une dépendance change.

## Merge readiness

- Bloquer sur tout finding critique non résolu.
- Bloquer si `python -m pytest` échoue ou si un smoke test sur `test/`
  régresse.
- Exiger une acceptation de risque explicite pour les findings importants
  différés.

## Format de sortie

```
### Critique
- [fichier:ligne] : [problème] → [fix attendu]

### Important
- [fichier:ligne] : [problème] → [fix attendu]

### Suggestions
- [fichier:ligne] : [amélioration]

### Résumé
[Risque résiduel, décision de merge]
```
