---
name: prd
description: Génère un Product Requirements Document structuré. Déclencher quand l'utilisateur dit "écris un PRD", "documente les exigences", "planifie cette feature", "user stories", ou quand une nouvelle fonctionnalité nécessite une spécification avant l'implémentation.
---

# PRD

Produit un PRD complet qui fait le lien entre la vision produit et l'exécution technique.

## Phase 1 — Discovery (obligatoire avant d'écrire)

Poser au minimum :
- **Le problème central** : pourquoi construire cela maintenant ?
- **Les métriques de succès** : comment sait-on que ça marche ?
- **Les contraintes** : délai, scope hors-périmètre, dépendances externes ?

Ne pas assumer le contexte. Si une contrainte n'est pas spécifiée, demander ou marquer `TBD`.

## Phase 2 — Analyse et scope

- Cartographier le parcours utilisateur écran par écran.
- Définir les **Non-Goals** pour protéger la timeline.
- Identifier les routes existantes touchées et les nouvelles routes nécessaires.

## Schéma PRD (structure obligatoire)

### 1. Résumé exécutif
- **Problème** : 1-2 phrases.
- **Solution proposée** : 1-2 phrases.
- **Critères de succès** : 3-5 KPIs mesurables.

### 2. Expérience utilisateur et fonctionnalités
- **Personas** : qui utilise cette fonctionnalité ?
- **User stories** : `En tant que [utilisateur], je veux [action] afin de [bénéfice].`
- **Critères d'acceptance** : définition de "done" par story, testable.
- **États à couvrir** : chargement, vide, erreur, hors ligne.
- **Non-Goals** : ce qu'on ne construit PAS dans cette itération.

### 3. Spécifications techniques
- **Routes** : arborescence App Router visée, et ce que rend chaque segment.
- **Frontière serveur/client** : quels écrans sont interactifs et pourquoi.
- **Données** : source, forme, fraîcheur attendue, stratégie de cache et de revalidation.
- **Mutations** : Server Actions ou Route Handlers, avec les règles de validation.
- **Auth et confidentialité** : qui accède à quoi, données sensibles, variables d'env requises.
- **Responsive et accessibilité** : breakpoints cibles, mode sombre, exigences clavier.

### 4. Risques et roadmap
- **Phases de livraison** : MVP → v1.1 → v2.0.
- **Risques techniques** : performance, dépendances bloquantes, migration de données.

## Standards de qualité

Utiliser des critères concrets et mesurables :
```diff
- "La page doit être rapide" ← vague
+ "LCP < 2.5s sur mobile 4G, liste de 200 éléments" ← concret
```
