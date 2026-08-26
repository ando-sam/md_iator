---
name: generate-docs
description: Crée ou met à jour de la documentation projet. Déclencher quand l'utilisateur dit "documente", "mets à jour le README", "écris les notes de déploiement", "documente ce changement", ou quand un comportement/API/commande change et que la doc n'est pas encore à jour.
---

# Generate Docs

Produit une documentation concise, orientée tâche, alignée sur la réalité du code.

Demander si non fourni :
- Type de document (tutoriel, how-to, référence, explication)
- Audience et contexte opérationnel
- Périmètre et exclusions

## Quand mettre à jour la doc

- Comportement, contrat d'API, ou setup qui change → documenter dans le même PR.
- Nouvelle variable d'env → la documenter avec sa portée (serveur seul ou `NEXT_PUBLIC_*`) et une valeur d'exemple non secrète.
- Nouvelle commande npm, nouvelle dépendance runtime, nouvelle étape de déploiement.
- Comportement d'erreur visible par l'utilisateur.
- Breaking change → note de migration explicite.

## Qualité attendue

- Langage concis, précis, orienté action.
- Commandes copiables et alignées sur les scripts réels de `package.json` (`npm run dev`, `build`, `start`, `lint`).
- Exemples alignés sur le comportement de production, pas sur un état local.
- Ne pas documenter d'API Next de mémoire — vérifier dans `node_modules/next/dist/docs/`.

## Surfaces

- **README** : ce que fait le projet, prérequis, install, lancement local, variables d'env, scripts disponibles.
- **AGENTS.md** : ne pas éditer le bloc `nextjs-agent-rules` — il est régénéré par `next dev`. Toute règle projet s'ajoute hors de ce bloc.
- **Notes de déploiement** : plateforme cible, variables d'env requises, commande de build.
- Doc livrée dans le même PR que le code concerné — si différée, documenter la dette explicitement.
