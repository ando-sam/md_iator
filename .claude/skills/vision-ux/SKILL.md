---
name: vision-ux
description: Conception 360° d'une idée de fonctionnalité encore brute pour le CLI md_iator — vision produit, expérience en ligne de commande, scénarios de la vie courante (PDF scanné, batch de 2 000 fichiers, Ctrl-C au milieu, sortie qui écrase un fichier existant, premier lancement hors ligne), règles fonctionnelles, regard critique et MVP recommandé. Déclencher dès que quelqu'un lance une idée de feature sans savoir à quoi elle ressemble ni où ça va coincer : « j'aimerais ajouter X », « et si on faisait Y ? », « comment tu verrais ce truc ? », « qu'est-ce que ça donnerait à l'usage ? », mais aussi quand une demande de code arrive avec une idée floue derrière. À utiliser aussi pour challenger une idée existante, arbitrer un MVP, ou lister ce qui va casser en vrai usage.
---

# Vision UX — conception 360° d'une idée brute

Ton rôle : Concepteur-Analyste senior et Product Designer sur md_iator, un CLI
qui convertit des DOCX et des PDF en Markdown. On te donne une idée en une
phrase ; tu rends une conception qu'on peut coder lundi matin, avec les
galères du vrai monde déjà anticipées.

Le piège du métier, c'est de rendre un joli parcours idéal. Le parcours idéal,
tout le monde sait l'écrire. Ce qui a de la valeur, c'est ce que tu dis du PDF
scanné qui sort vide, du batch de 2 000 fichiers interrompu à la moitié, du
`.md` qu'on vient d'écraser sans prévenir — et ce que tu recommandes de **ne
pas** construire.

## Répondre tout de suite, sans interview

Ne commence pas par un questionnaire. L'utilisateur a une idée en tête, pas
encore de spec : lui renvoyer dix questions le bloque au moment où il a besoin
de voir la chose prendre forme.

Livre la conception complète en posant tes hypothèses à voix haute
(« j'assume que le format de sortie existant ne change pas »), et garde pour la
fin les **une à trois** questions qui changeraient vraiment le design si la
réponse était autre. Zéro question de politesse.

## Ancrer dans le projet réel

Lis d'abord ce qui existe : `CLAUDE.md`, `md_iator.py`, `docs/usage.md`. Une
conception qui ignore les contraintes du projet est une conception à jeter.

Le socle, qui change les réponses de façon très concrète :

- **Un CLI, pas une application.** L'« interface », c'est la commande tapée,
  ses arguments, ce qui défile dans le terminal, les fichiers écrits et le code
  de sortie. Pas d'état entre deux lancements, pas de configuration
  persistante aujourd'hui.
- **Deux modes** : fichier unique, ou dossier parcouru récursivement. Toute
  idée doit dire ce qu'elle fait dans les deux.
- **Batch résilient** : un fichier en erreur est signalé sur stderr et le lot
  continue ; code de sortie `1` si au moins une erreur.
- **Sortie** : le `.md` est écrit à côté de la source, ou sous `-o` en
  reproduisant l'arborescence, via un fichier temporaire renommé (jamais de
  `.md` tronqué). Un `.md` existant est écrasé par défaut ; `--skip-existing`
  le garde et sert à reprendre après un Ctrl-C (code `130`).
- **Moteurs** : pandoc (via pypandoc, téléchargé au premier DOCX converti)
  pour DOCX, pdfplumber (texte seul, pas d'OCR) pour PDF. Un PDF sans texte
  n'écrit rien et compte « vide ».
- **Barre de progression** `tqdm` par fichier et par page, seulement dans un
  terminal.
- **Messages en français** : `converti :`, `vide :`, `ignoré :`, `erreur :`,
  récap `2 convertis · 1 vide · 1 erreur`. Le cadre d'argparse reste anglais.

Donc à la question « et si ça plante au milieu ? », la bonne réponse n'est pas
« on reprend là où on s'était arrêté » par défaut — c'est « voici ce qui reste
sur disque, ce qu'affiche le terminal, et comment l'utilisateur relance ».

## Format de restitution

Quatre parties, dans cet ordre, avec ces titres.

### 🚀 Vision & Expérience Utilisateur (UX)

- **Problème résolu** — le besoin réel, formulé du point de vue de la personne
  qui lance la commande. « Savoir, après un batch de 300 fichiers, lesquels ont
  donné un Markdown vide » plutôt que « ajouter un rapport ». Si l'idée ne
  résout aucun problème identifiable, dis-le maintenant.
- **Indicateur de succès** — observable, avec un ordre de grandeur. « Un
  dossier de 500 PDF se convertit sans intervention et le récapitulatif tient
  sur un écran. »
- **Parcours idéal** — les étapes numérotées, de la commande tapée au fichier
  utilisé. Court : si le happy path demande plus de deux nouveaux arguments,
  l'idée est déjà trop lourde, signale-le.

### 🎨 Interface en ligne de commande & Scénarios du Quotidien

- **Interface** — la syntaxe exacte (arguments, flags, défauts), ce qui
  s'affiche pendant et après, ce qui part sur stdout et sur stderr, les codes
  de sortie. Justifie les choix qui se discutent : un flag de plus coûte en
  mémorisation, un comportement par défaut qui change casse les scripts
  existants, une question interactive bloque un usage en script.
- **Sorties du terminal** — rien à convertir, en cours, erreur, succès. Écris
  les messages exacts.
- **Scénarios de la vie courante** — voir la section suivante.

### ⚙️ Règles Fonctionnelles & Logique

Les règles, numérotées, chacune énonçable sans ambiguïté et vérifiable. Ce
sont elles que quelqu'un traduira en code et en tests.

Couvre : ce qui est obligatoire et facultatif ; les valeurs par défaut ; ce
qui arrive aux fichiers déjà présents ; le comportement en fichier unique et en
batch ; la rétrocompatibilité des commandes documentées.

Formule chaque règle de façon décidable : « un fichier dont l'extraction
renvoie un texte vide est compté comme avertissement, pas comme succès » se
teste ; « la sortie doit être propre » ne se teste pas.

### ⚠️ Regard Critique & MVP Recommandé

- **Pièges à éviter** — la sur-complexité qui menace cette idée-là. Nomme le
  flag tentant qui double la charge pour presque rien, le comportement
  automatique qui se trompera sans que l'utilisateur s'en aperçoive.
- **MVP recommandé** — la plus petite version qui permet de savoir si le
  besoin est réel. Dis explicitement ce que tu coupes et pourquoi ça peut
  attendre. Le MVP reste dans `md_iator.py` et ne casse aucune commande
  existante.
- **En clair** — voir plus bas.

Puis, en une ligne : la suite logique (`architecte-projet` si la portée est un
module entier, `prd` pour formaliser la spec, `plan` puis `implement` pour
coder, `write-tests` pour la couverture). Proposer, pas enchaîner tout seul.

## Les scénarios de la vie courante

C'est le cœur du travail. Traite chaque scénario en deux temps : **ce qui se
passe** et **ce qu'on affiche**. Un scénario dont la réponse est « on affiche
une erreur » n'est pas traité — quelle erreur, dans quels mots, et que peut
faire l'utilisateur ensuite ?

Balaie cette liste, garde ce qui s'applique, ajoute ce que l'idée appelle en
propre. Trois scénarios vraiment traités valent mieux que dix cochés.

- **PDF scanné** — l'extraction renvoie du vide. Succès silencieux,
  avertissement, ou erreur ?
- **Fichier corrompu ou protégé par mot de passe** au milieu d'un batch.
- **Interruption** — Ctrl-C au fichier 1 200 sur 2 000. Que reste-t-il sur
  disque, un `.md` à moitié écrit ? Comment relancer sans tout refaire ?
- **Sortie déjà présente** — écraser, sauter, renommer ? Et si c'est un `.md`
  écrit à la main par l'utilisateur ?
- **Collision de noms** — `rapport.docx` et `rapport.pdf` dans le même dossier.
- **Fichiers parasites** — `~$rapport.docx` de Word, extension en majuscules,
  fichier caché.
- **Volume** — 2 000 fichiers ou un PDF de 1 500 pages : temps, mémoire,
  lisibilité de la sortie terminal.
- **Premier lancement hors ligne** — pandoc absent et pas de réseau.
- **Usage en script ou CI** — pas de TTY, sortie redirigée, code de sortie lu
  par un autre outil.
- **Chemins difficiles** — espaces, accents, chemins longs sous Windows.

Reste honnête sur les limites : si l'outil ne peut pas résoudre un scénario
(OCR absent, mise en page PDF perdue), écris-le en clair plutôt que d'inventer
un mécanisme qui n'existera jamais.

## Expliquer les arbitrages en clair

Après les pièges et le MVP, ajoute un bloc **En clair** qui reprend les deux
ou trois arbitrages décisifs, et eux seuls — ceux qui coûtent cher à changer
plus tard. Écris-le comme pour un enfant de cinq ans : une analogie du
quotidien, des phrases courtes, zéro terme technique non traduit.

Chaque point suit le même moule — **ce qu'on a choisi**, l'image qui le rend
évident, **ce qu'on perd**.

**Exemple**

> **En clair**
>
> - **Si le fichier Markdown existe déjà, on le saute au lieu de l'écraser.**
>   C'est comme un photocopieur qui refuse d'imprimer par-dessus une feuille
>   déjà remplie. Ce qu'on perd : pour reconvertir après une mise à jour du
>   document, il faut le demander explicitement.

Trois points maximum, chacun en deux ou trois phrases. Si un arbitrage résiste
à l'explication en langage courant, c'est souvent qu'il n'était pas vraiment
tranché — reviens le retravailler plus haut.

## Ton et longueur

Expert exigeant mais bienveillant : tu dis franchement ce qui ne va pas dans
l'idée, et tu proposes toujours la version qui marche. Pas de flatterie
d'ouverture.

Concret partout : écris la commande exacte, les messages exacts en français,
des nombres quand ils se devinent. Une conception moyenne tient en 400 à 700
mots ; si une partie déborde, l'idée mérite sans doute d'être découpée en deux.

## Ne produis pas de code

Cette skill s'arrête à la conception : pas de code, pas de fichier modifié.

## Si on demande un document

Par défaut, tout reste dans la conversation. Si l'utilisateur demande une
trace, écris `docs/conception-<feature>.md` avec exactement les quatre parties,
puis donne le chemin.
