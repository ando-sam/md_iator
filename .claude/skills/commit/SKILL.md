---
name: commit
description: Analyse le diff stagé et crée un commit Conventional Commits. Déclencher quand l'utilisateur dit "commit", "commite", "/commit". Messages en anglais, pas de co-author.
---

# Commit

## Double validation — obligatoire avant tout commit

Aucun `git commit` n'est lancé sans deux validations explicites de l'utilisateur,
dans cet ordre :

1. Présenter la liste des fichiers concernés et le message de commit **proposé**.
   Le message est une proposition, pas une décision : l'utilisateur peut le
   réécrire avant qu'il soit utilisé.
2. Attendre une **première validation explicite** sur ces fichiers et ce message.
3. Redemander une **seconde validation dédiée**, juste avant d'exécuter la
   commande, en citant le message final retenu. Tant que cette seconde
   confirmation n'est pas donnée, la commande n'est pas exécutée.

Une double validation vaut pour un seul commit : elle ne s'étend jamais aux
commits suivants, même dans la même session, même pour un changement voisin.
Les mêmes règles s'appliquent à `git push`, `git rebase`, `git reset --hard` et
à tout amend d'un commit existant.

## Principes

- **Atomique** : un commit = un seul changement logique cohérent. Ne pas mélanger `feat` et `fix`, ni deux sujets sans rapport, dans le même commit.
- **Incrémental** : si le diff couvre plusieurs changements logiques indépendants, les découper en plusieurs commits successifs plutôt qu'un seul gros commit. Chaque commit doit rester compréhensible et fonctionnel isolément.

## Workflow

```bash
# 1. Voir ce qui est modifié
git status --short
git diff --staged   # si déjà stagé
git diff            # sinon

# 2. Identifier les changements logiques distincts dans le diff,
#    puis pour CHAQUE changement logique : stager uniquement ses fichiers/hunks
git add path/to/file1 path/to/file2
# git add -p pour stager des hunks spécifiques si un fichier contient plusieurs changements logiques

# 3. Créer le commit pour ce changement logique
git commit -m "$(cat <<'EOF'
<type>(<scope>): <description>
EOF
)"

# 4. Répéter 2-3 pour chaque changement logique restant
```

## Format

```
<type>(<scope>): <description courte, impératif, anglais, < 72 chars>

[corps optionnel — le POURQUOI, pas le QUOI]
```

**Pas de ligne Co-Authored-By.**

- Présent impératif : « add », jamais « added » ni « adds ».
- Description sous 72 caractères.
- Référencer une issue dans le footer quand il y en a une : `Closes #123`, `Refs #456`.

## Types

| Type | Usage |
| --- | --- |
| `feat` | New feature |
| `fix` | Bug fix |
| `perf` | Performance improvement |
| `refactor` | Refactor without feature or fix |
| `test` | Add or update tests |
| `docs` | Documentation only |
| `chore` | Maintenance, config, dependencies |
| `ci` | CI / GitHub Actions |

## Scopes projet

Le scope est optionnel : un changement transverse s'écrit sans scope
(`feat: show progress bars during conversion`).

| Scope | Quand |
| --- | --- |
| `cli` | `main()`, arguments argparse, messages et codes de sortie |
| `docx` | `convert_docx`, intégration pypandoc / pandoc |
| `pdf` | `convert_pdf`, extraction pdfplumber, format des pages |
| `batch` | `batch_convert`, parcours récursif, arborescence de sortie |
| `deps` | `pyproject.toml`, `requirements.txt`, packaging |
| `claude` | Configuration `.claude/` (skills, settings) |

Ajouter un scope au tableau dès qu'un nouveau sujet stable apparaît dans le dépôt.

## Exemples

```
feat(pdf): extract tables as GitHub-flavored Markdown
fix(batch): match file extensions case-insensitively
fix(cli): exit with code 1 when output directory is not writable
chore(deps): package as installable CLI
docs: reflect md-iator command and tqdm dependency
```

## Règles de sécurité git

- Ne jamais modifier la config git.
- Ne jamais `--no-verify`, `--force`, `reset --hard` sans demande explicite.
- Ne jamais commiter `.env`, credentials, clés privées.
- Ne jamais commiter les documents d'exemple de `test/` ni les `.md` générés à
  partir d'eux : ce sont des fichiers locaux, potentiellement confidentiels.
- Ne jamais commiter `__pycache__/` ni `*.egg-info/`.
- Si un hook pre-commit échoue : corriger, re-stager, **nouveau commit** (jamais `--amend`).
- Ne jamais force-push sur `main` (branche principale).
