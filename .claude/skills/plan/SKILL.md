---
name: plan
description: Produit un plan d'implémentation avant de coder. Déclencher quand l'utilisateur dit "planifie", "propose une approche", "avant de coder", "analyse d'abord", ou quand la tâche touche le contrat CLI, le format de sortie, les dépendances, ou un refactor transversal. Ne génère aucun code — uniquement le plan.
---

# Plan

Analyse le problème, identifie les contraintes, produit un plan d'implémentation
ordonné et sûr pour UNE tâche dans le code existant. Pour cadrer un module
entier, utiliser `architecte-projet`.

## Processus

1. **Collecte de contexte** — lire `CLAUDE.md`, le paquet `md_iator/` et
   `docs/usage.md` ; identifier les contrats existants (arguments CLI, codes de
   sortie, calcul du chemin de sortie, format du Markdown produit, signatures
   des fonctions `convert_*`).
2. **Clarification** — si les exigences sont ambiguës, poser 2-3 questions
   ciblées avant de planifier.
3. **Plan d'implémentation** — livrer dans cet ordre :
   - **Vue d'ensemble** : ce qu'on construit et pourquoi.
   - **Contraintes et dépendances** : fonctions touchées, contrats concernés,
     nouvelles dépendances éventuelles, ordre de livraison.
   - **Étapes séquencées** : chacune petite, vérifiable, testable seule.
   - **Stratégie de test** : tests à écrire (`write-tests`) et smoke test sur
     les documents d'exemple de `test/`.
   - **Risques et fallbacks** : ce qui peut casser, alternatives, décisions à
     prendre avant d'implémenter.

## Règles

- Tout changement de contrat (argument, code de sortie, format de sortie,
  chemin de sortie) est une décision à faire valider, pas une étape.
- Nouvelle dépendance : la justifier, et prévoir sa déclaration dans
  `pyproject.toml` **et** `requirements.txt`.
- Garder les deux modules du paquet (`__init__.py` pour la conversion,
  `cli.py` pour la CLI) ; en ajouter un relève d'`architecte-projet`.
- Prévoir la mise à jour de `README.md`, `docs/usage.md` et `CLAUDE.md` comme
  étape si le comportement visible change.
- Ne pas planifier un refactor en même temps qu'un fix — séparer les deux.
- Si une décision produit est nécessaire avant de coder, la lister dans les
  risques.
- Si l'utilisateur veut une trace écrite : `docs/plan_<sujet>.md`.

## Format de sortie attendu

```
## Vue d'ensemble
[1 paragraphe]

## Contraintes
- [liste]

## Étapes
1. [étape] — fonctions : [...] — vérification : [...] *(bloque N+1 si applicable)*
2. ...

## Tests
- [test ou commande] — [ce qui est vérifié]

## Risques
- [risque] → [mitigation ou décision requise]
```
