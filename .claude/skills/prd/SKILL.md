---
name: prd
description: Génère un Product Requirements Document structuré pour une fonctionnalité de md_iator. Déclencher quand l'utilisateur dit "écris un PRD", "documente les exigences", "spécifie cette feature", "user stories", ou quand une nouvelle fonctionnalité nécessite une spécification avant l'implémentation.
---

# PRD

Produit un PRD qui fait le lien entre le besoin et l'exécution technique, pour
une fonctionnalité isolée. Idée encore floue côté usage : `vision-ux` d'abord.
Module entier : `architecte-projet`.

## Phase 1 — Discovery (obligatoire avant d'écrire)

Poser au minimum ces questions :
- **Le problème central** : pourquoi construire cela maintenant ?
- **Les métriques de succès** : comment sait-on que ça marche ?
- **Les contraintes** : formats concernés, volumétrie, délai, hors-périmètre ?

Ne pas assumer le contexte. Si un point n'est pas spécifié, demander ou marquer
`TBD`.

## Phase 2 — Analyse et scope

- Cartographier l'usage de bout en bout : la commande tapée, ce qui s'affiche
  pendant la conversion, ce qui est écrit sur disque, le code de sortie.
- Définir les **Non-Goals** pour protéger la timeline.
- Identifier les dépendances : bibliothèques (pypandoc, pdfplumber, tqdm,
  nouvelle lib ?), binaire pandoc, consommateurs du Markdown produit.

## Schéma PRD (structure obligatoire)

### 1. Résumé exécutif
- **Problème** : 1-2 phrases.
- **Solution proposée** : 1-2 phrases.
- **Critères de succès** : 3-5 KPIs mesurables.

### 2. Expérience utilisateur et fonctionnalités
- **Personas** : qui lance la commande, dans quel contexte (poste local,
  script, CI, préparation de documents pour un LLM) ?
- **User stories** : `En tant que [utilisateur], je veux [action] afin de [bénéfice].`
- **Critères d'acceptance** : définition de "done" pour chaque story, testable.
- **Non-Goals** : ce qu'on ne construit PAS dans cette itération.

### 3. Spécifications techniques
- **Interface CLI** : nouveaux arguments, valeurs par défaut, interaction avec
  `input` et `-o/--output`, rétrocompatibilité des commandes existantes.
- **Entrées et sorties** : formats acceptés, structure exacte du Markdown
  produit (avec un exemple), règle de nommage et d'emplacement des fichiers de
  sortie.
- **Erreurs** : messages affichés (texte exact, en français, sur stderr),
  comportement en batch, codes de sortie.
- **Dépendances** : nouvelle bibliothèque ou binaire, impact sur
  l'installation, déclaration dans `pyproject.toml` et `requirements.txt`.
- **Performance** : volumétrie cible (pages, fichiers en batch), mémoire.
- **Compatibilité** : Python ≥ 3.10, macOS / Linux / Windows.

### 4. Risques et roadmap
- **Phases de livraison** : MVP → v1.1 → v2.0.
- **Risques techniques** : limites des bibliothèques d'extraction, fichiers
  mal formés, régression du format de sortie existant, téléchargement de
  pandoc hors ligne.

## Standards de qualité

Utiliser des critères concrets et mesurables :
```diff
- "La conversion doit être rapide" ← vague
+ "Un PDF texte de 300 pages se convertit en < 30 s sur un poste standard" ← concret
```

## Livrable

Par défaut dans la conversation. Si l'utilisateur demande un fichier :
`docs/prd_<feature>.md`.
