---
title: "Être alerté des nouvelles offres"
description: "Suivre les avis de vacance de poste par flux RSS : le flux général, ou un flux par famille de métier et par collectivité."
archetype: "page"
disableNextPrev: true
hidden: true

# Le corps de cette page est une LISTE produite par un shortcode : l'indexer en entier
# ferait répondre cette page à presque toutes les recherches. Seuls son titre et sa
# description sont indexés (voir assets/_relearn_searchindex.js).
index_contenu: false
---

Plutôt que de revenir vérifier, laissez les nouvelles offres venir à vous. Chaque famille
de métier et chaque collectivité a son propre flux.

### Comment ça marche

Un **flux RSS** est une adresse que votre lecteur d'actualités interroge à votre place.
Dès qu'une offre paraît, elle apparaît chez vous. C'est gratuit, il n'y a **rien à
créer, aucune adresse électronique à donner**, et vous pouvez vous désabonner en retirant
le flux de votre lecteur.

Il vous faut simplement une application capable de lire les flux : la plupart des
lecteurs d'actualités, certains navigateurs, et de nombreux clients de messagerie savent
le faire. Copiez l'adresse d'un flux ci-dessous, collez-la dans votre lecteur, c'est tout.

{{% notice style="tip" title="Le plus simple" icon="rss" %}}
Si vous voulez tout suivre, un seul flux suffit : [toutes les offres](/index.xml).
{{% /notice %}}

### Suivre un métier

Un flux par famille, avec le nombre d'offres actuellement ouvertes.

{{< avp-flux axe="familles" >}}

### Suivre un employeur

{{< avp-flux axe="collectivites" >}}

### Autres façons de suivre

- **Par commune, province ou corps** : chaque page d'étiquette a aussi son flux. Ouvrez-la
  et cliquez sur « S'abonner à ces offres ».
- **Recherche multicritère** : la page [Toutes les offres](/offres/) permet de filtrer par
  métier, employeur, commune, échéance, et de partager le résultat filtré par son adresse.
- **Réutiliser les données** : voir la section correspondante de la page
  [À propos](/a-propos/).
