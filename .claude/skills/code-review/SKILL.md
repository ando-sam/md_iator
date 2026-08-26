---
name: code-review
description: Effectue une code review structurée par sévérité. Déclencher quand l'utilisateur dit "review", "relis ce code", "vérifie ce PR", "est-ce que c'est correct", ou avant un merge sur un chemin critique (auth, Server Actions, Route Handlers, données utilisateur).
---

# Code Review

Review security-first, findings classés par sévérité, guidance de remédiation actionnable.

## Priorités

- **Critique** : vulnérabilité de sécurité, fuite de secret côté client, contournement d'autorisation, corruption de données, build cassé.
- **Important** : tests manquants sur chemin risqué, régression de performance, accessibilité cassée, dérive d'architecture.
- **Suggestion** : lisibilité, nommage, cohérence, maintenabilité.

## Ce qu'il faut vérifier

### Correctness
- Le comportement correspond aux exigences ; edge cases couverts.
- APIs Next conformes à cette version — vérifier dans `node_modules/next/dist/docs/` en cas de doute, ne pas valider de mémoire.
- `params` / `searchParams` `await`és.
- Pas de logique non sérialisable franchissant la frontière serveur → client.

### Sécurité
- **Frontière serveur/client** : aucun secret, clé d'API, ou token dans un fichier `"use client"` ni dans une variable `NEXT_PUBLIC_*`.
- **Server Actions** : ce sont des endpoints publics — validation des inputs et vérification d'autorisation à l'intérieur de l'action, pas seulement dans l'UI.
- **Route Handlers** : authentification explicite, validation du body, pas de CORS permissif par défaut.
- Pas de `dangerouslySetInnerHTML` sur du contenu non assaini.
- Redirections et URLs d'images construites à partir d'input utilisateur : liste blanche obligatoire.
- Secrets hors du code et hors des logs.

### Performance
- Frontière `"use client"` placée le plus bas possible — pas de layout entier basculé client pour un widget.
- Fetchs parallélisés, pas en cascade ; `Suspense` et `loading.tsx` sur les segments lents.
- Directives de cache et de revalidation explicites et justifiées.
- `next/image` avec dimensions ; `priority` uniquement sur le LCP.
- Pas d'import lourd tiré dans un bundle client sans besoin.

### Accessibilité et UI
- Sémantique HTML correcte, `alt` sur les images, labels associés aux champs.
- Focus clavier visible, contraste suffisant en clair et en sombre.
- Classes Tailwind cohérentes avec les tokens de `@theme inline` — pas de valeurs arbitraires dupliquées.

### Tests et docs
- Nouveau comportement et bug fixes couverts (ou dette explicitement documentée).
- README ou docs mis à jour si le setup, les commandes, ou les variables d'env changent.

## Merge readiness

- Bloquer sur tout finding critique non résolu.
- Bloquer si `npm run lint` ou `npm run build` échoue.
- Exiger une acceptation de risque explicite pour les findings importants différés.

## Format de sortie

```
### Critique
- [fichier:ligne] : [problème] → [fix attendu]

### Important
- [fichier:ligne] : [problème] → [fix attendu]

### Suggestions
- [fichier:ligne] : [amélioration]

### Résumé
[Risque résiduel, décision de merge]
```
