---
name: commit
description: Analyse le diff stagé et crée un commit Conventional Commits. Déclencher quand l'utilisateur dit "commit", "commite", "/commit". Messages en anglais, pas de co-author.
---

# Commit

## Principes

- **Atomique** : un commit = un seul changement logique cohérent. Ne pas mélanger `feat` et `fix`, ni deux domaines sans rapport.
- **Incrémental** : si le diff couvre plusieurs changements logiques indépendants, les découper en plusieurs commits successifs. Chaque commit doit rester compréhensible et buildable isolément.

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
git commit -m "$(cat <<'MSG'
<type>(<scope>): <description>
MSG
)"

# 4. Répéter 2-3 pour chaque changement logique restant
```

## Format

```
<type>(<scope>): <description courte, impératif, anglais, < 72 chars>

[corps optionnel — le POURQUOI, pas le QUOI]
```

**Pas de ligne Co-Authored-By.**

## Types

| Type | Usage |
| --- | --- |
| `feat` | New feature |
| `fix` | Bug fix |
| `perf` | Performance improvement |
| `refactor` | Refactor without feature or fix |
| `style` | Styling / CSS only, no behavior change |
| `test` | Add or update tests |
| `docs` | Documentation only |
| `chore` | Maintenance, config, dependencies |
| `ci` | CI / GitHub Actions |

## Scopes projet

| Scope | Quand |
| --- | --- |
| `app` | Routing, layouts, pages de l'App Router |
| `ui` | Composants réutilisables et présentation |
| `styles` | `globals.css`, tokens de thème, Tailwind |
| `lib` | Helpers, accès données, types partagés |
| `actions` | Server Actions |
| `api` | Route Handlers |
| `config` | `next.config.ts`, `tsconfig.json`, `eslint.config.mjs`, `postcss.config.mjs` |
| `deps` | `package.json` / `package-lock.json` |

Ajouter un scope au tableau dès qu'un nouveau domaine stable apparaît dans le repo.

## Exemples

```
feat(app): add family dashboard route with server-rendered summary
fix(actions): validate invite payload before persisting member
perf(ui): move member list below the client boundary
style(styles): expose surface tokens in @theme inline
chore(deps): bump next to 16.3.1
```

## Règles de sécurité git

- Ne jamais `--no-verify`, `--force`, `reset --hard` sans demande explicite.
- Ne jamais commiter `.env`, `.env.local`, credentials, ou clés privées.
- Ne jamais commiter `.next/` ni `node_modules/`.
- Si un hook pre-commit échoue : corriger, re-stager, **nouveau commit** (jamais `--amend`).
- Ne jamais force-push sur `main` (branche principale).
- Le bloc `nextjs-agent-rules` de `AGENTS.md` est régénéré par `next dev` — le commiter avec le travail plutôt que de le retirer du diff.
