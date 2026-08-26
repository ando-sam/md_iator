---
name: plan
description: Produit un plan d'implémentation avant de coder. Déclencher quand l'utilisateur dit "planifie", "propose une approche", "avant de coder", "analyse d'abord", ou quand la tâche touche plusieurs routes, la frontière serveur/client, ou un refactor transversal. Ne génère aucun code — uniquement le plan.
---

# Plan

Analyse le problème, identifie les contraintes, produit un plan d'implémentation ordonné et sûr.

## Processus

1. **Collecte de contexte** — lire les fichiers concernés dans `app/`, tracer les dépendances entre routes et composants, identifier les contrats existants (props, types, endpoints).
2. **Vérification des APIs** — ce projet est sur Next.js 16 ; confirmer les conventions dans `node_modules/next/dist/docs/` avant de planifier une approche qui repose sur une API précise.
3. **Clarification** — si les exigences sont ambiguës, poser 2-3 questions ciblées avant de planifier.
4. **Plan d'implémentation** — livrer dans cet ordre :
   - **Vue d'ensemble** : ce qu'on construit et pourquoi.
   - **Contraintes et dépendances** : routes touchées, données requises, ordre de livraison.
   - **Étapes séquencées** : chaque étape petite, vérifiable, livrable indépendamment si possible.
   - **Stratégie de test** : quoi tester et à quel niveau.
   - **Risques et fallbacks** : ce qui peut casser, alternatives, décisions à prendre avant d'implémenter.

## Décisions à trancher explicitement dans le plan

- **Server ou Client Component** pour chaque nouveau composant, avec la raison — c'est la décision structurante de l'App Router.
- **Où vivent les données** : fetch serveur, Server Action, ou Route Handler.
- **Stratégie de cache et de revalidation** : statique, dynamique, ou revalidation par tag.
- **Impact sur le bundle client** : toute nouvelle dépendance tirée côté navigateur.

## Règles

- Un fetch de données reste le plus proche possible du serveur ; ne pas planifier un `useEffect` de fetch par défaut.
- Ne pas planifier un refactor en même temps qu'un fix — séparer les deux.
- Toute nouvelle variable d'environnement doit apparaître dans le plan, avec sa portée (serveur seul ou `NEXT_PUBLIC_*`).
- Si une décision produit est nécessaire avant de coder, la lister explicitement dans les risques.

## Format de sortie attendu

```
## Vue d'ensemble
[1 paragraphe]

## Contraintes
- [liste]

## Étapes
1. [étape] *(bloque N+1 si applicable)*
2. ...

## Tests
- [ce qu'il faut tester et comment]

## Risques
- [risque] → [mitigation ou décision requise]
```
