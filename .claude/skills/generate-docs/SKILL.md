---
name: generate-docs
description: Crée ou met à jour de la documentation projet. Déclencher quand l'utilisateur dit "documente", "mets à jour le README", "documente ce changement", ou quand un argument, un format, un message, un code de sortie ou une dépendance change et que la doc n'est pas encore à jour.
---

# Generate Docs

Produit une documentation concise, orientée tâche, alignée sur la réalité du
code.

Demander si non fourni :
- Type de document (tutoriel, how-to, référence, explication)
- Audience et contexte d'usage
- Périmètre et exclusions

## Quand mettre à jour la doc

- Nouvel argument ou changement de comportement CLI → documenter dans le même
  PR.
- Nouveau format d'entrée, ou changement du Markdown produit.
- Changement de message, de code de sortie ou de gestion d'erreur visible.
- Nouvelle dépendance runtime, nouvelle étape d'installation, changement du
  téléchargement automatique de pandoc.
- Breaking change → ajouter une note de migration explicite.

## Où écrire

| Contenu | Emplacement | Langue |
| --- | --- | --- |
| Présentation, installation, exemples courants | `README.md` | anglais |
| Référence CLI complète (arguments, modes, codes de sortie, format de sortie) | `docs/usage.md` | anglais |
| Environnement, architecture, commandes pour Claude | `CLAUDE.md` | français |
| Changements visibles par version, ruptures et migration | `CHANGELOG.md` (section de la version en cours) | anglais |

Ces trois fichiers se recoupent : un changement de commande ou d'argument se
répercute dans les trois.

## Qualité attendue

- Langage concis, précis, orienté action.
- Commandes copiables : `md-iator` (après `pip install -e .`) en forme
  principale, `python -m md_iator` en fallback sans installation.
- Exemples de sortie copiés d'une vraie exécution, pas inventés. Lancer la
  commande avec `-o` vers un dossier temporaire pour les capturer.
- Messages cités exactement comme le code les affiche (`converti : ...`,
  `vide : ...`, `ignoré : ...`, `erreur : ...`, récap
  `2 convertis · 1 vide · 1 erreur`).
- Dépendances : vérifier que `pyproject.toml` et `requirements.txt` disent la
  même chose avant de les documenter.

## Surfaces requises

- **README** : installation et usage à jour.
- **docs/usage.md** : synchronisé avec `main()` — chaque argument argparse y
  figure, avec ses défauts.
- **CLAUDE.md** : section Architecture alignée sur les fonctions réelles du
  paquet `md_iator/`.
- Doc livrée dans le même PR que le code concerné — si différée, documenter la
  dette explicitement.
