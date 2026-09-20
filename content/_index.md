---
title: "Les emplois de la fonction publique calédonienne"
weight: 1

# Les fiches d'offres — et elles seules — sont aussi servies en JSON-LD, à côté de leur
# page. Le motif `/*/*` ne vise que les pages à deux niveaux (`/famille/référence`) :
# les pages éditoriales de la racine (à propos, mentions légales…) n'ont pas de données
# structurées à exposer et ne doivent pas produire un fichier vide. `kind: page` écarte
# en plus les pages de tags (collectivités, communes…), qui sont elles aussi à deux
# niveaux mais n'ont pas de référence d'offre.
cascade:
  - target:
      path: '/*/*'
      kind: 'page'
    outputs: ['html', 'print', 'markdown', 'avp_json']
---

{{% notice style="note" title="Site en cours de validation" icon="circle-check" %}}
avps.nc est en phase de validation : toutes les offres publiées sont en ligne, et nous
vérifions encore la qualité des fiches et des illustrations. Si vous constatez une erreur,
le PDF officiel fait foi. Pour consulter l'ensemble des avis de vacance de poste,
référez-vous à la source officielle sur
[data.gouv.nc](https://data.gouv.nc/explore/dataset/avis-de-vacances-de-poste-avp-drhfpnc).
{{% /notice %}}

{{< avp-hero >}}

Les avis de vacance de poste (AVP) paraissent en données ouvertes sur
[data.gouv.nc](https://data.gouv.nc/explore/dataset/avis-de-vacances-de-poste-avp-drhfpnc)
et arrivent ici quelques heures après leur parution.

{{% notice style="tip" title="Première visite ?" icon="book-open" %}}
Corps, grade, famille de métier, code ROME, durée de résidence : le vocabulaire des avis
n'est pas évident quand on ne vient pas de la fonction publique.
**[Comprendre les AVP](/comprendre-les-avis/)** l'explique en quelques minutes.
{{% /notice %}}

### 🔎 Comment chercher

👈 **Le menu latéral classe les offres par famille de métier** — les 41 familles du
référentiel officiel de la fonction publique calédonienne (RESPNC). Cherchez donc
d'abord ce que vous voulez faire, pas qui recrute.

Vous pouvez ensuite filtrer par **collectivité**, **direction**, **commune**,
**province** ou **corps** : chaque offre porte ces étiquettes, et chacune donne accès à
la liste correspondante.

### 📄 Postuler

Chaque fiche renvoie au **PDF officiel** de l'avis, qui fait seule foi, ainsi qu'aux
coordonnées de candidature. Les dossiers se déposent auprès de la collectivité qui
recrute, jamais auprès de ce site.

{{< avp-dernieres nb="6" >}}

{{< avp-map >}}
