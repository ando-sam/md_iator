---
name: refactor-code
description: Améliore la maintenabilité du code existant sans changer le comportement. Déclencher quand l'utilisateur dit "refactor", "nettoie ce code", "simplifie", "réduit la complexité", "extrait un composant", ou quand un changement de comportement déclenche du cleanup adjacent.
---

# Refactor Code

Refactore de manière incrémentale en préservant le comportement et le rendu.

Demander si non fourni :
- Fichiers ou route cible
- Objectif (lisibilité, complexité, duplication, frontière serveur/client, taille de bundle)
- Tolérance au risque et timeline

## Règles

- Préserver le comportement, le rendu, et les interfaces publiques sauf demande explicite contraire.
- Changements petits et vérifiables, étape par étape ; `npm run lint` et `npm run build` après chaque étape.
- Ne jamais mélanger du feature work dans un refactor pur.
- Mettre à jour ou ajouter des tests quand on refactore un chemin risqué.

## Cibles de refactor propres à ce projet

- **Descendre la frontière `"use client"`** — extraire la partie interactive dans un composant client dédié et laisser le parent en Server Component.
- **Sortir la logique métier des composants** vers `app/lib/`, là où elle est testable.
- **Factoriser les classes Tailwind répétées** en composant réutilisable, ou en token dans `@theme inline` de `app/globals.css` — pas en chaîne dupliquée.
- **Éliminer les `useEffect` de fetch** au profit d'un fetch serveur quand la donnée n'est pas dépendante d'une interaction.
- **Remplacer les chemins relatifs profonds** par l'alias `@/*`.
- **Renforcer le typage** : supprimer les `any`, utiliser les types de route générés par Next.
