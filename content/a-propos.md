---
title: "À propos de la plateforme"
description: "Comment les fiches d'offres sont produites automatiquement à partir des données ouvertes."
archetype: "page"
disableNextPrev: true # Évite que les flèches de navigation cyclent sur cette page

hidden: true

---

### 🏛️ Ce que fait ce site — et ce qu'il ne fait pas

avps.nc **republie** les avis de vacance de poste (AVP) de la fonction publique
calédonienne, publiés en données ouvertes par la direction des ressources humaines et de
la fonction publique de Nouvelle-Calédonie (DRHFPNC) sur
[data.gouv.nc](https://data.gouv.nc/explore/dataset/avis-de-vacances-de-poste-avp-drhfpnc).

Ce site **n'est pas** un employeur, ni un intermédiaire de recrutement, et n'est édité
par aucune des collectivités dont il relaie les offres. Il n'enregistre aucune
candidature : les dossiers se déposent auprès de la collectivité qui recrute, selon les
modalités indiquées sur l'avis.

**Le PDF officiel de l'avis fait seul foi.** Les fiches de ce site sont produites
automatiquement : en cas de divergence, c'est le document d'origine qui prime.

### ⚙️ La démarche de production

1. **Données ouvertes d'abord.** Tout ce que la source fournit de façon structurée est
   repris tel quel : référence, dates, corps et grade, nombre de postes, contacts, et —
   quand la collectivité les renseigne — les missions, savoirs et savoir-faire.
2. **Lecture du PDF en complément (IA générative).** Ce que la source ne dit pas est
   extrait du document par un agent (Gemini) : contexte du poste, organisation,
   habilitations. La source l'emporte partout où les deux se recouvrent.
3. **Rattachement au référentiel métiers.** Chaque offre est rapprochée des 368 fiches
   d'emploi du référentiel RESPNC, ce qui détermine sa famille de métier — donc son rayon
   dans le menu — et son code ROME.
4. **Illustration.** La bannière de chaque offre est générée par un modèle d'image, avec
   le logo de la collectivité concernée lorsqu'il est disponible.
5. **Site statique.** Le site est compilé avec Hugo : chargement instantané, aucune base
   de données exposée, empreinte minimale.

Le code source du site est consultable sur GitHub :
[avps-content](https://github.com/Strategie-Zen-IT/avps-content).

---

### 🛠️ Informations de build (suivi technique)

Pour garantir la traçabilité de l'application, les indicateurs de révision système sont
injectés à chaque déploiement :

{{< build-info >}}
