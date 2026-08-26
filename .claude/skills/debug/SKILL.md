---
name: debug
description: Diagnostique et corrige un bug par root-cause analysis. Déclencher quand l'utilisateur donne un stack trace, une erreur, un comportement inattendu, ou dit "ça ne marche pas", "debug", "trouve le problème". Reproduire avant de corriger.
---

# Debug

Diagnostic systématique de la reproduction à la correction vérifiée.

Demander si non fourni :
- Symptôme, stack trace, ou comportement erroné
- Où ça casse : dev (`npm run dev`), build (`npm run build`), ou runtime production
- Serveur ou navigateur (l'erreur apparaît dans le terminal ou dans la console DevTools ?)

## Workflow

1. **Reproduire** — étapes fiables avant tout changement de code. Noter si l'erreur survient au premier rendu, à la navigation, ou après une interaction.
2. **Localiser la frontière** — l'erreur vient-elle d'un Server Component, d'un Client Component, d'une Server Action, ou du build ? C'est la question la plus discriminante dans l'App Router.
3. **Tracer le chemin** — suivre le flux : route → layout → page → fetch → composant.
4. **Root cause** — cause fondamentale, pas symptôme.
5. **Fix minimal** — le plus petit changement qui résout la cause. Pas de refactor simultané.
6. **Valider** — rejouer la reproduction, puis `npm run lint` et `npm run build`.
7. **Synthèse** — root cause, fix, prévention.

## Pièges fréquents Next.js 16 / React 19

- **Hydration mismatch** — rendu serveur ≠ rendu client. Causes usuelles : `Date.now()`, `Math.random()`, `window`/`localStorage` lus pendant le rendu, HTML invalide imbriqué.
- **`"use client"` manquant** — un hook ou un handler `onClick` dans un Server Component échoue au build.
- **Fonction passée à un Client Component** — les props traversant la frontière serveur/client doivent être sérialisables.
- **`params` / `searchParams` non `await`és** — ils sont asynchrones.
- **Données périmées après mutation** — `revalidatePath` / `revalidateTag` manquant après une Server Action.
- **Variable d'env `undefined` côté navigateur** — il manque le préfixe `NEXT_PUBLIC_`.
- **Cache trompeur** — supprimer `.next/` et relancer avant de conclure à un bug de code.

Vérifier la sémantique exacte dans `node_modules/next/dist/docs/` avant de conclure — cette version a des breaking changes.

## Guardrails

- Ne pas corriger le symptôme quand la cause est ailleurs.
- Pas de broad refactor pendant un bug fix.
- Retirer les `console.log` de diagnostic avant de livrer.
