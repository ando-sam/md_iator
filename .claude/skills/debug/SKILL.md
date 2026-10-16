---
name: debug
description: Diagnostique et corrige un bug par root-cause analysis. Déclencher quand l'utilisateur donne un stack trace, une erreur, un comportement inattendu, ou dit "ça ne marche pas", "debug", "trouve le problème". Reproduire avant de corriger.
---

# Debug

Diagnostic systématique, de la reproduction à la correction vérifiée.

Demander si non fourni :
- Symptôme, stack trace, ou sortie Markdown erronée
- Commande exacte lancée (`md-iator ...` ou `python md_iator.py ...`) et code
  de sortie
- Fichier source : format, taille, nombre de pages, PDF texte ou scanné
- Mode : fichier unique ou batch (dossier)

## Workflow

1. **Reproduire** — établir des étapes fiables avant tout changement de code :
   la commande exacte sur le plus petit fichier qui déclenche le bug, avec `-o`
   vers un dossier temporaire pour ne rien écraser.
2. **Tracer le chemin** — suivre le flux de bout en bout : `main()` (argparse,
   `_ensure_pandoc`) → `convert_file()` ou `batch_convert()` → calcul du chemin
   de sortie → `convert_docx()` (pypandoc) ou `convert_pdf()` (pdfplumber) →
   écriture du `.md`.
3. **Root cause** — la cause fondamentale, pas le symptôme. Isoler la couche
   fautive : appeler directement `pypandoc.convert_file` ou
   `pdfplumber.open(...).pages[n].extract_text()` dans un shell Python pour
   distinguer un bug de md_iator d'une limite de la bibliothèque.
4. **Fix minimal** — le plus petit changement qui résout la cause. Pas de
   refactor en même temps.
5. **Valider** — rejouer la reproduction, lancer `python -m pytest`, puis un
   smoke test sur les documents d'exemple (voir `implement`, section
   Validation).
6. **Synthèse** — expliquer la cause racine, le fix et la prévention.

## Pistes fréquentes dans md_iator

- **Section PDF vide** : PDF scanné (image seule), pdfplumber n'extrait aucun
  texte. Ce n'est pas un bug de md_iator — OCR préalable avec `ocrmypdf`.
- **Régression d'un bug déjà corrigé** — extension en majuscules ignorée en
  batch, fichier verrou `~$*.docx` ramassé, `.md` écrasé par une source de même
  nom, `-o sortie/` traité comme nom de fichier, pandoc vérifié avant
  `parse_args()`. Chacun a son test dans `tests/test_batch.py` ou
  `tests/test_cli.py` : partir du test qui échoue.
- **`-o sortie` sans `/` crée un fichier `sortie`** : comportement voulu en mode
  fichier unique ; seul un `-o` terminé par `/` est créé comme dossier.
- **Sortie console mélangée avec la barre de progression** : `print` au lieu
  de `bar.write` dans une boucle `tqdm`.
- **Caractères corrompus** : vérifier l'encodage d'écriture (`utf-8`) et ce que
  renvoie la bibliothèque avant d'accuser le fichier source.

## Guardrails

- Ne pas corriger le symptôme quand la cause est ailleurs.
- Pas de refactor large pendant un bug fix — séparer les deux.
- Ajouter un test de régression ciblé dans `tests/` (`write-tests`), et
  vérifier qu'il échoue sans le fix.
- Ne jamais lancer de reproduction sans `-o` sur un dossier qui contient déjà
  des `.md` à garder : la conversion les écrase.
- Retirer les `print` de diagnostic avant de livrer.
