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

## Logos présents

Récupérés depuis les sites institutionnels des employeurs. ⚠️ Autorisation de
reproduction à confirmer auprès de chacun.

| Fichier | Employeur | Clé de résolution |
|---|---|---|
| `pvn.png` | Province Nord | sigle `PVN` |
| `pvs.png` | Province Sud | sigle `PVS` |
| `pil.png` | Province des îles Loyauté | sigle `PIL` |
| `nouvelle-caledonie.png` | Gouvernement de la Nouvelle-Calédonie | slug de collectivité — couvre TOUTES ses directions (DASS, DITTT, DAVAR, DRHFPNC…) |
| `cnc.png` | Congrès de la Nouvelle-Calédonie | sigle `CNC` |
| `cht.png` | Centre hospitalier territorial « Gaston Bourret » | sigle `CHT` |
| `chn.png` | Centre hospitalier du Nord | sigle `CHN` |
| `chs.png` | Centre hospitalier spécialisé « Albert Bousquet » | sigle `CHS` |
| `opt.png` | Office des postes et télécommunications | sigle `OPT` |
| `giep-nc.png` | Groupement insertion évolution professionnelles | sigle `GIEP NC` |
| `adck.png` | Agence de développement de la culture kanak | sigle `ADCK` — logo du Centre culturel Tjibaou, qu'elle gère |
| `autorite-de-la-concurrence-de-nouvelle-caledonie.png` | Autorité de la concurrence de Nouvelle-Calédonie | slug de collectivité |
| `ville-du-mont-dore.png` | Ville du Mont-Dore | slug de collectivité |
| `ville-de-noumea.png` | Ville de Nouméa | slug de collectivité — **pas encore employeur** dans la source, seuls ses établissements y figurent |

## Employeurs sans logo

- **Université de Nouvelle-Calédonie** (`unc`) : logo introuvable sur unc.nc, la page
  d'accueil ne l'expose ni en image ni en SVG.
- **ISEE** : le site ne publie qu'une version **blanche** du logo, illisible sur fond
  clair. Mieux vaut pas de logo qu'un logo dénaturé — le site affiche alors une icône.
- **Commune de Poya**, **Caisse des écoles de Nouméa** : pas de site accessible.
- **`A-TRIER`** : par définition sans employeur identifié.

## Où ils apparaissent

Un logo déposé ici est repris **immédiatement** sur les pages de taxonomie et la ligne
« Employeur » des fiches, grâce à un repli sur le fichier local (`fileExists`). En
revanche, le champ `hiringOrganization.logo` du JSON-LD et les bannières ne le prennent
qu'à la **prochaine publication** de l'offre : le front-matter des offres déjà publiées
est figé jusqu'à modification.
