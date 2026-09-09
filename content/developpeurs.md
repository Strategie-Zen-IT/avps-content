---
title: "Les AVP pour les développeurs"
description: "Réutiliser les avis de vacance de poste de la fonction publique calédonienne : open data, JSON-LD, flux ATS, dataset Hugging Face."
archetype: "page"
disableNextPrev: true
hidden: true
---

### 🔓 Tout est réutilisable, sans clé ni compte

Il n'y a **pas d'API** sur ce site, et c'est délibéré : les données sont exposées sous
forme de fichiers statiques, que n'importe quel client HTTP peut lire directement. Rien à
demander, rien à s'abonner, aucune limite de débit.

| Ressource | Adresse | Format |
|---|---|---|
| Données source officielles | [data.gouv.nc](https://data.gouv.nc/explore/dataset/avis-de-vacances-de-poste-avp-drhfpnc) | Parquet, CSV, JSON, API ODS |
| Fiche structurée d'une offre | `JSON-LD` embarqué dans chaque page | Schema.org/JobPosting |
| Flux des dernières offres | `/index.xml` | RSS |
| Flux pour ATS / agrégateurs | `/flux_ats.xml` | XML façon Indeed |
| Plan de site des offres | `/jobs-sitemap.xml` | Google Jobs |
| Corpus complet | dataset Hugging Face | JSONL + Parquet (embeddings) |

### 📄 Le JSON-LD, le plus simple pour une offre

Chaque page d'offre embarque son balisage `Schema.org/JobPosting` dans un
`<script type="application/ld+json">`. C'est la même structure que celle lue par Google
Jobs, donc directement exploitable :

```bash
curl -s https://avps.nc/administration-generale/26-1301/ \
  | sed -n '/application\/ld+json/,/<\/script>/p' \
  | sed '1d;$d' | jq '.title, .hiringOrganization.name, .validThrough'
```

### 🧭 Ce que contient une fiche

Au-delà des champs Schema.org standard, chaque offre porte :

- `collectivite` — la collectivité qui recrute (elle seule est l'employeur) ;
- `direction` — la direction de rattachement en son sein ;
- `famille` — l'une des 41 familles du référentiel RESPNC, et `famille_source` qui dit
  comment elle a été déterminée (`respnc` = appariement sur le référentiel,
  `gemini` = classification par le modèle, `defaut` = non rattachée) ;
- `code_rome` — la classification ROME quand elle est connue ;
- `latitude` / `longitude` — le géocodage du lieu de travail.

### ⚠️ Deux mises en garde

**Le PDF officiel fait seul foi.** Ces fiches sont produites automatiquement : en cas de
divergence, référez-vous au document d'origine, dont l'URL est dans chaque offre.

**Ne réutilisez pas ce site comme employeur.** Chaque offre a la sienne
(`hiringOrganization`) : un agrégateur qui afficherait « avps.nc » comme entreprise
recruteuse enverrait les candidats au mauvais endroit.

### 🤖 Et un serveur MCP ?

Pas encore. Un endpoint MCP et une recherche sémantique (« trouve-moi les postes proches
de celui-ci ») sont prévus le jour où un service dynamique sera déployé ; les vecteurs
sont déjà calculés pour chaque offre en attendant.
