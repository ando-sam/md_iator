---
name: implement
description: Implémente une fonctionnalité Python production-ready dans md_iator. Déclencher pour toute tâche d'écriture de code : nouvel argument CLI, nouveau format d'entrée, changement du Markdown produit, correction d'une logique de conversion ou de batch. Analyse d'abord, implémente une étape à la fois, valide avant de passer à la suivante.
---

# Implement

Livre des changements production-ready dans md_iator, vérifiés et cohérents
avec le code existant : comprendre → planifier → implémenter une étape →
vérifier.

## Avant d'écrire

- Lire `md_iator.py` en entier (il est court) et la section concernée de
  `docs/usage.md`.
- Exposer brièvement ce qui est compris, les contrats concernés, puis le plan
  de l'étape courante.

## Conventions du code

- Fichier unique `md_iator.py`, Python ≥ 3.10.
- Type hints sur toutes les fonctions (`Path`, `Path | None`,
  `tuple[int, int]`).
- Chemins avec `pathlib.Path`, jamais de concaténation de chaînes.
- Messages utilisateur en français ; erreurs sur stderr ; dans une boucle
  `tqdm`, écrire via `bar.write(...)` et pas `print`.
- Une erreur de conversion lève une exception ; c'est `batch_convert` qui la
  capture, l'affiche et continue, et `main` qui la traduit en code de sortie.
- Écriture des fichiers en `utf-8`.

## Ajouter un format d'entrée

1. Ajouter l'extension à `SUPPORTED_EXTENSIONS`.
2. Écrire `convert_<format>(src: Path, dest: Path) -> None`, sur le modèle de
   `convert_docx` / `convert_pdf`.
3. Brancher le dispatch dans `convert_file`.
4. Nouvelle bibliothèque : l'ajouter dans `pyproject.toml` **et**
   `requirements.txt`, avec une borne minimale comme les autres.
5. Documenter le format dans `README.md`, `docs/usage.md` et `CLAUDE.md`.

## Contrats à préserver

- Arguments CLI : positional `input`, `-o/--output`.
- Codes de sortie : `0` si tout a réussi, `1` sinon.
- Batch : une erreur sur un fichier n'arrête pas le lot.
- Format PDF : `## Page N` par page, séparateur `---`.
- Chemin de sortie : à côté de la source sans `-o`, arborescence miroir sous
  `-o` en batch, dossier parent créé automatiquement.
- Le fichier source n'est jamais modifié.

Un changement de l'un de ces contrats est une décision à faire valider par
l'utilisateur avant d'écrire le code.

## Validation

Après chaque étape : relire le diff, vérifier les effets de bord, puis :

```bash
python -m pytest

# Smoke test sur les documents d'exemple (dossier test/, non versionné).
# Toujours avec -o : sans -o, les .md déjà présents dans test/ sont écrasés.
out="$(mktemp -d)"
md-iator test/ -o "$out"; echo "exit=$?"
ls -R "$out"
```

- En cas d'échec : s'arrêter, trouver la cause racine, corriger, relancer. Ne
  pas passer à l'étape suivante.
- Pas de commit en fin de travail : la skill `commit` et sa double validation
  s'en chargent, sur demande de l'utilisateur.

## Gates qualité

- Comportement conforme aux exigences et aux contrats existants.
- Aucun écrasement de fichier non voulu, aucune exception non gérée qui
  interrompt un batch.
- Comportement modifié couvert par des tests (`write-tests`) ou, à défaut, par
  un smoke test décrit.
- Doc à jour si le comportement visible change (`generate-docs`).
