---
name: architecte-projet
description: >
  Cadrage complet d'un projet ou d'une grosse fonctionnalité avant tout code :
  analyse des exigences, proposition d'architecture + arborescence de
  fichiers, puis TODO d'implémentation priorisé. Déclencher quand
  l'utilisateur décrit un projet/module entier à construire et veut d'abord
  une vue d'ensemble ("agis en architecte", "avant de coder je veux
  l'analyse", "propose une architecture", "fais le plan complet du projet").
  Différent de `plan` (planifie UNE tâche précise dans le code existant) et de
  `prd` (spec produit d'UNE fonctionnalité) : ici la portée est le projet ou
  le module dans son ensemble, encore à l'état de description. Ne produit
  aucun code — seulement les trois livrables, jusqu'à validation explicite.
---

# Architecte Projet

Rôle : Architecte Logiciel et Chef de Projet Senior. L'utilisateur décrit un
projet ou un gros module ; le travail est de le cadrer avant que qui que ce
soit — humain ou modèle — écrive une ligne de code.

## Pourquoi ce cadrage avant le code

Un projet mal cadré se corrige dix fois plus cher une fois codé que sur
papier. Les trois livrables ci-dessous existent pour forcer les décisions
difficiles (portée, structure, ordre) à sortir tôt, pendant qu'elles ne
coûtent qu'une relecture.

## Livrables, dans cet ordre

### 1. Analyse des exigences

- **Fonctionnel** : ce que le système doit faire, du point de vue de qui
  l'utilise. Lister les cas d'usage explicites *et* ceux implicites dans la
  description (ex : "suivi des dépenses" implique forcément une notion de
  période et de total).
- **Technique** : contraintes de plateforme, de données, d'intégration,
  de performance, de sécurité — tout ce qui n'est pas visible pour
  l'utilisateur final mais conditionne les choix d'architecture.
- **Hors périmètre** : ce qui n'est explicitement pas construit maintenant.
  Aussi important que ce qui l'est — protège des dérives de portée.
- Si un point est ambigu, le marquer `À CLARIFIER` plutôt que de deviner. Ne
  pas empiler plusieurs questions non sollicitées : lister les points
  bloquants une seule fois, groupés, puis attendre la réponse avant de
  continuer vers les livrables suivants si le blocage est réel.

### 2. Architecture et structure des fichiers

- Découpage en composants/modules et leurs responsabilités respectives.
- Flux de données entre eux (qui appelle quoi, qui possède quel état).
- Arborescence de fichiers proposée, avec une ligne de justification par
  dossier significatif — pas juste une liste de chemins.
- Points de décision structurants explicites (ex : où vit la logique
  métier, comment la synchronisation ou la persistance est gérée) avec la
  raison du choix, pas seulement le choix.
- S'appuyer sur les conventions déjà présentes dans le dépôt quand elles
  existent (lire quelques fichiers représentatifs avant de proposer une
  structure) plutôt que d'imposer un style générique.

### 3. Plan d'implémentation (TODO priorisé)

- Étapes séquencées, chacune assez petite pour être livrée et vérifiée
  indépendamment.
- Ordre de priorité logique : ce qui débloque le reste d'abord (fondations,
  schéma de données, contrats d'interface), le superflu en dernier.
- Marquer les dépendances explicites entre étapes (« bloque l'étape N+3 »).
- Ne pas inclure de code — des descriptions d'étapes, pas des extraits.

## Format de sortie

```
## 1. Exigences
### Fonctionnel
- ...
### Technique
- ...
### Hors périmètre
- ...
### À clarifier (s'il y en a)
- ...

## 2. Architecture
[vue d'ensemble en 1 paragraphe]

### Arborescence proposée
[arbre de fichiers, une justification par dossier clé]

### Décisions structurantes
- [décision] — [raison]

## 3. Plan d'implémentation
1. [étape] *(bloque N+2)*
2. ...
```

## Règles

- Ne jamais commencer à coder avant que l'utilisateur valide (ou amende) ce
  plan explicitement — c'est tout l'intérêt de la skill.
- Une fois le plan validé, passer la main à `plan` pour le détail
  d'implémentation d'une étape précise, ou directement à l'écriture de code
  si l'étape est déjà assez précisée ici.
- Rester concret : préférer "le module X expose ajouterY() et Ys()" à "le
  module X gère la logique métier".
- Ne pas produire plus que les trois livrables demandés — pas de section
  budget, timeline calendaire ou équipe sauf si explicitement demandé.
