# Logos des employeurs

Un fichier PNG par employeur, nommé d'après son **sigle slugifié en minuscules** :

```
static/logos/pvs.png          # Province Sud
static/logos/cht.png          # Centre hospitalier territorial
static/logos/ville-du-mont-dore.png
```

Le sigle est celui de la colonne `sigle` de la table BigQuery `avp_data.employeurs`,
alimentée automatiquement par le fetcher. Pour savoir lesquels manquent, par ordre de
priorité :

```sql
SELECT sigle, nom_source, nb_avp_actifs
FROM `avp-engine.avp_data.employeurs`
WHERE identifie ORDER BY nb_avp_actifs DESC
```

## À quoi ils servent

1. **Génération des bannières** — l'étape `banner` du moteur télécharge
   `https://avps.nc/logos/{sigle}.png` et l'injecte dans le prompt pour que le logo
   apparaisse dans le décor de l'illustration.
2. **JSON-LD** — le champ `hiringOrganization.logo` de l'offre, lu par Google Jobs.

## Deux choses à savoir

- **L'absence de logo est un cas normal**, pas une erreur : la bannière est alors générée
  avec une consigne explicite d'« aucun logo, aucun blason, aucun emblème », pour que le
  modèle n'invente pas un symbole institutionnel plausible mais faux.
- **Les AVP déjà publiés ne récupèrent pas un logo ajouté après coup.** Leur
  front-matter est figé jusqu'à leur prochaine modification. Ils expirent de toute façon
  sous deux mois : inutile de forcer un rejeu pour ça.

⚠️ N'ajoutez ici que des logos que l'employeur autorise à reproduire.
