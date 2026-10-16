---
name: refactor-code
description: Améliore la maintenabilité du code existant sans changer le comportement. Déclencher quand l'utilisateur dit "refactor", "nettoie ce code", "simplifie", "réduit la complexité", "extrait une fonction", ou quand un changement de comportement déclenche du cleanup adjacent.
---

# Refactor Code

Refactore de manière incrémentale en préservant le comportement et les contrats
existants.

Demander si non fourni :
- Fonctions ou zone cible
- Objectif du refactor (lisibilité, complexité, duplication, testabilité)
- Tolérance au risque

## Règles

- Préserver le comportement et les interfaces publiques sauf demande explicite
  contraire : arguments CLI, codes de sortie, messages affichés, format du
  Markdown produit, signatures de `convert_docx`, `convert_pdf`,
  `convert_file` et `batch_convert`.
- Appliquer des changements petits et vérifiables, étape par étape.
- Respecter le découpage existant : un `convert_<format>(src, dest)` par
  moteur, dispatch et calcul du chemin dans `convert_file`, parcours dans
  `batch_convert`, argparse et sortie de processus dans `cli.main`.
- Garder les deux modules du paquet (`__init__.py`, `cli.py`) : en ajouter
  ou en scinder un est une décision d'architecture (`architecte-projet`), pas
  un refactor.
- Aucun formateur ni linter n'est configuré : ne pas reformater le fichier
  entier, garder le style en place (type hints, `pathlib`, f-strings).
- Ne jamais mélanger du feature work dans un refactor pur — séparer les deux.
- Mettre à jour ou ajouter des tests quand on refactore un chemin risqué.
- Vérifier après chaque étape : `python -m pytest` et un smoke test sur `test/` (voir `implement`, section
  Validation) dont la sortie doit rester identique à celle d'avant le refactor.
