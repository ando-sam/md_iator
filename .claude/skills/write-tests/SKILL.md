---
name: write-tests
description: Génère ou améliore des tests pytest pour md_iator (calcul des chemins de sortie, conversion PDF/DOCX, batch, codes de sortie du CLI). Déclencher quand l'utilisateur dit "écris les tests", "ajoute une couverture", "test de régression", "teste cette fonction", ou avant un merge sur un chemin risqué sans test.
---

# Write Tests

Génère des tests ciblés, déterministes, orientés comportement — pas couverture
de ligne.

Demander si non fourni :
- Périmètre (fonction, mode fichier unique, batch, CLI)
- Comportements prioritaires et edge cases

## Suite existante

- Dossier `tests/` à la racine — pas `test/`, qui contient les documents
  d'exemple locaux.
- `pytest` en dépendance de développement (`[project.optional-dependencies]
  dev` dans `pyproject.toml`), installé par `pip install -e ".[dev]"`.
- `tests/conftest.py` fournit les fixtures à réutiliser plutôt que d'en
  réécrire :
  - `engines` : faux pandoc et faux pdfplumber. Un faux `.docx` est du texte
    converti en `# <contenu>\n` ; un faux `.pdf` contient ses pages séparées
    par `\f` (page vide = `None`, comme une page scannée) ;
  - `make(path, content="contenu", corrupt=False)` : crée un fichier source,
    parents compris ; `corrupt=True` fait échouer les deux moteurs ;
  - `pandoc_checks` : remplace `_ensure_pandoc` et enregistre ses appels.
- `tests/test_cli.py` applique `pandoc_checks` à tous ses tests (autouse) :
  aucun test ne doit déclencher de téléchargement.

## Priorités de couverture

1. **Chemin de sortie** (`convert_file`) : sans `-o` (à côté de la source),
   `-o` fichier, `-o` dossier existant, dossier parent créé, extension non
   supportée qui lève `ValueError`.
2. **Format PDF** (`convert_pdf`) : `## Page N` par page, séparateur `---`,
   page sans texte.
3. **Batch** (`batch_convert`) : parcours récursif, arborescence miroir sous
   `-o`, un fichier en erreur n'arrête pas le lot, compteurs `(ok, errors)`.
4. **CLI** (`main`) : code de sortie `0` / `1`, chemin introuvable.
5. **Régression** : un test par bug confirmé.
6. **Edge cases** après le happy path et les modes d'échec principaux.

## Conventions

- Fichier : `tests/test_<sujet>.py`, fonctions `test_<comportement>_<scénario>`.
- Fichiers temporaires via la fixture `tmp_path`, jamais dans le dépôt.
- Pas de réseau ni de binaire pandoc : passer par `engines` et
  `pandoc_checks`, jamais par les vraies bibliothèques.
- CLI : helpers `run(monkeypatch, *args)` et `exit_code(monkeypatch, *args)` de
  `tests/test_cli.py` (ils remplacent `sys.argv` et capturent `SystemExit`) ;
  `capsys` pour stdout / stderr. En cas de succès en mode fichier unique,
  `main()` retourne sans `SystemExit`.
- Test de régression : vérifier qu'il échoue sur le code d'avant le fix.
- Assertions spécifiques — `assert dest.read_text(encoding="utf-8") == attendu`,
  jamais `assert result`.
- Tests indépendants de l'ordre d'exécution.

## Tests d'intégration (optionnels)

Une conversion réelle sur les documents de `test/` peut être ajoutée, marquée
`@pytest.mark.skipif` quand le dossier est absent (il n'est pas versionné), et
toujours avec une sortie dans `tmp_path`.

## Lancer les tests

```bash
python -m pytest -v

# Un seul test
python -m pytest tests/test_batch.py::test_batch_skips_word_lock_files -v
```

## Attentes de merge

- Nouveau comportement → tests du flux principal obligatoires.
- Refactor → confiance comportementale préservée.
- Changement d'un contrat (chemin de sortie, format, code de sortie) → tests
  du chemin négatif obligatoires.
- Si des tests sont différés, documenter le risque et le périmètre dans la PR.
