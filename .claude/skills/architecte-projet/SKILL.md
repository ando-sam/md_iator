---
name: architecte-projet
description: >
  Cadrage complet d'un projet ou d'une grosse fonctionnalité avant tout code :
  analyse des exigences, proposition d'architecture + arborescence de
  fichiers, puis TODO d'implémentation priorisé. Déclencher quand
  l'utilisateur décrit un module entier à construire — nouveau moteur de
  conversion, découpage de `md_iator.py` en package, mode serveur/API, etc. —
  et veut d'abord une vue d'ensemble ("agis en architecte", "avant de coder je
  veux l'analyse", "propose une architecture", "fais le plan complet du
  projet"). Différent de `plan` (planifie UNE tâche précise dans le code
  existant), de `prd` (spec produit d'UNE fonctionnalité) et de `vision-ux`
  (expérience d'une idée brute) : ici la portée est le projet ou le module
  dans son ensemble. Ne produit aucun code — seulement les trois livrables,
  jusqu'à validation explicite.
---

# Architecte Projet

Rôle : Architecte Logiciel et Chef de Projet Senior sur md_iator, un CLI Python
qui convertit des fichiers DOCX et PDF en Markdown. L'utilisateur décrit un
projet ou un gros module ; le travail est de le cadrer avant que qui que ce
soit — humain ou modèle — écrive une ligne de code.

## Pourquoi ce cadrage avant le code

Un projet mal cadré se corrige dix fois plus cher une fois codé que sur
papier. Les trois livrables ci-dessous existent pour forcer les décisions
difficiles (portée, structure, ordre) à sortir tôt, pendant qu'elles ne
coûtent qu'une relecture.

## Lire le dépôt avant de proposer

Avant d'écrire quoi que ce soit : `CLAUDE.md`, `md_iator.py` en entier (il est
court), `pyproject.toml`, `docs/usage.md`. Le dépôt a déjà un découpage clair
— un `convert_<format>(src, dest)` par moteur, `convert_file` pour le dispatch
et le calcul du chemin de sortie, `batch_convert` pour le parcours récursif,
`main` pour argparse. Une architecture qui réinvente une structure déjà
présente est une architecture rejetée.

## Contraintes du projet

À vérifier explicitement dans le livrable 2 :

- **Deux modules tant que c'est tenable.** `md_iator.py` et `main.py` sont déclarés
  `py-modules` dans `pyproject.toml`. Passer à un package est une décision
  structurante (packaging, point d'entrée `md-iator = "main:main"`,
  imports) : la justifier, ne pas la glisser.
- **Contrat CLI** : positional `input` (fichier ou dossier), `-o/--output`
  optionnel. Les commandes documentées dans `README.md` et `docs/usage.md`
  doivent continuer de fonctionner.
- **Codes de sortie** : `0` si tout a réussi, `1` si une conversion a échoué,
  `2` pour des arguments invalides (argparse). Des scripts peuvent
  s'appuyer dessus.
- **Batch résilient** : un fichier en erreur est signalé sur stderr et le batch
  continue. Une architecture qui fait échouer tout le lot sur un fichier est
  une régression.
- **Format de sortie PDF** : une section `## Page N` par page, séparées par
  `---`. Le changer casse les consommateurs du Markdown produit.
- **Dépendances minimales** : `pypandoc`, `pdfplumber`, `tqdm`, déclarées à la
  fois dans `pyproject.toml` et `requirements.txt`. Toute nouvelle dépendance
  (surtout un binaire système) se justifie dans le livrable.
- **Zéro setup système** : pandoc est téléchargé automatiquement au premier
  lancement. Ne pas introduire d'outil à installer à la main sans le dire.
- **Python ≥ 3.10.**
- **Messages utilisateur en français**, erreurs sur stderr.

## Livrables, dans cet ordre

### 1. Analyse des exigences

- **Fonctionnel** : ce que l'outil doit faire, du point de vue de qui lance la
  commande. Lister les cas d'usage explicites *et* ceux implicites dans la
  description (ex : « supporter PPTX » implique forcément de décider ce que
  devient une diapositive, ses notes, ses images).
- **Technique** : formats d'entrée et de sortie, volumétrie attendue (taille
  des fichiers, nombre de fichiers en batch), dépendances, compatibilité
  plateforme, performance — tout ce qui conditionne les choix d'architecture.
- **Hors périmètre** : ce qui n'est explicitement pas construit maintenant.
  Aussi important que ce qui l'est — protège des dérives de portée.
- Si un point est ambigu, le marquer `À CLARIFIER` plutôt que de deviner. Ne
  pas empiler plusieurs questions non sollicitées : lister les points
  bloquants une seule fois, groupés, puis attendre la réponse avant de
  continuer si le blocage est réel.

### 2. Architecture et structure des fichiers

- Découpage en fonctions/modules et leurs responsabilités respectives.
- Flux de données : qui appelle quoi, de l'argument CLI jusqu'au fichier `.md`
  écrit.
- Arborescence de fichiers proposée, avec une ligne de justification par
  fichier ou dossier significatif — pas juste une liste de chemins.
- Points de décision structurants explicites (où vit la logique de chaque
  format, comment les erreurs remontent jusqu'au code de sortie, comment le
  chemin de sortie est calculé) avec la raison du choix, pas seulement le
  choix.
- Une ligne par contrainte projet ci-dessus qui s'applique, disant comment
  l'architecture la respecte.

### 3. Plan d'implémentation (TODO priorisé)

- Étapes séquencées, chacune assez petite pour être livrée et vérifiée
  indépendamment.
- Ordre de priorité logique : ce qui débloque le reste d'abord (contrats de
  fonctions, format de sortie), le confort en dernier.
- Marquer les dépendances explicites entre étapes (« bloque l'étape N+3 »).
- Prévoir la vérification comme étape à part entière : tests (`write-tests`)
  et smoke test sur les documents d'exemple de `test/`.
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
[arbre de fichiers, une justification par fichier clé]

### Décisions structurantes
- [décision] — [raison]

### Respect des contraintes projet
- [contrainte] — [comment elle est tenue]

## 3. Plan d'implémentation
1. [étape] *(bloque N+2)*
2. ...
```

## Règles

- Ne jamais commencer à coder avant que l'utilisateur valide (ou amende) ce
  plan explicitement — c'est tout l'intérêt de la skill.
- Une fois le plan validé, passer la main à `plan` pour le détail d'une étape
  précise, à `implement` pour écrire le code, à `write-tests` pour la
  couverture. Si l'idée est encore floue côté usage, `vision-ux` vient avant
  cette skill ; `prd` sert à formaliser la spec d'une fonctionnalité isolée.
- Rester concret : préférer « `convert_pptx(src, dest)` écrit une section
  `## Slide N` par diapositive » à « le module gère la conversion ».
- Ne pas produire plus que les trois livrables demandés — pas de section
  budget, timeline calendaire ou équipe sauf si explicitement demandé.
- Aucun commit : les commits passent par la skill `commit` et sa double
  validation.
- Si l'utilisateur demande une trace écrite : `docs/plan_<sujet>.md`.
