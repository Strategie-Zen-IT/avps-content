# avps-content — le site avps.nc

Site [Hugo](https://gohugo.io/) des avis de vacance de poste (AVP) de la fonction
publique calédonienne, publié sur **[avps.nc](https://avps.nc)** via GitHub Pages.

**Ce dépôt n'est pas rédigé à la main.** Les fiches d'offres y sont déposées par
[`avps-engine`](https://github.com/Strategie-Zen-IT/avps-engine), qui ouvre une pull
request par AVP et l'auto-merge. Ce qui se modifie ici : les gabarits (`layouts/`), les
pages éditoriales (`content/*.md`), les logos des employeurs (`static/logos/`) et la
présentation (`assets/css/`).

## 🗂️ Comment le contenu est organisé

```
content/
  {famille-de-metier}/          41 rubriques = les familles du référentiel RESPNC
    _index.md                   créé automatiquement à la 1re offre de la famille
    {reference-avp}.md          une fiche par offre
  archives/                     offres clôturées, jamais supprimées
  _index.md  a-propos.md  developpeurs.md  stats.md  mentions-legales.md  404.md
static/logos/{sigle}.png        logos des employeurs — voir le README du dossier
data/familles_*.yml             GÉNÉRÉS depuis le référentiel du moteur
data/avps/{reference}.json      fiche JSON-LD de chaque offre (déposée par le moteur)
```

Le menu se lit **par métier**, et non par employeur : un candidat cherche ce qu'il veut
faire. L'employeur devient une taxonomie transverse — avec 29 employeurs actifs et 84
dans l'historique, un menu par employeur serait illisible.

### Les six taxonomies

| Taxonomie | Contenu |
|---|---|
| `familles` | la famille de métier RESPNC (axe principal, structure `content/`) |
| `collectivites` | **l'employeur juridique** : Nouvelle-Calédonie, Province Sud, une commune, un hôpital… |
| `directions` | la direction de rattachement **au sein** de cette collectivité |
| `communes` | la commune du lieu de travail (référentiel des 33 communes) |
| `provinces` | province Sud / Nord / des îles Loyauté |
| `corps` | corps, grade ou domaine d'emploi |
| `tags` | tout ce qui précède, pour la recherche plein-texte |

Distinguer `collectivites` de `directions` est essentiel : `DASS` et `DITTT` sont des
directions **de** la Nouvelle-Calédonie, alors que `CHT` ou `PVS` sont des collectivités
entières. C'est la collectivité qui recrute juridiquement — c'est donc elle, et pas la
direction, qui figure dans `hiringOrganization` du JSON-LD et dans `<company>` du flux ATS.

## 🧬 Origine du projet

Ce site est dérivé d'un portail d'AVP conçu pour un employeur public unique (le site
`odata-avps` de l'OPT-NC, publié sur GitHub). La transposition à l'ensemble de la fonction
publique calédonienne a imposé les changements suivants :

1. **Arborescence par famille de métier** et non par direction : les 41 familles RESPNC
   remplacent les 15 directions de l'organigramme de l'employeur d'origine.
2. **Taxonomies séparées.** L'ancien site n'avait qu'un `tags` fourre-tout mélangeant
   ville, province, corps et familles : impossible d'y lister « tous les AVP de la
   Province Sud » sans voir aussi les corps et les métiers.
3. **Les bannières ne sont plus dans Git.** Elles vivent dans un bucket GCS public et le
   front-matter n'en porte que l'URL. Mesure faite sur le site d'origine : 240 Mo de blobs PNG
   dans l'historique pour 46 bannières vivantes, `.git` à 1,6 Go en quatre mois — au
   rythme de 2333 AVP/an, le dépôt prendrait plus de 3 Go par an.
4. **Plus de « mot de la DRH ».** C'était un édito signé par la DRH de l'employeur
   d'origine ; personne ne peut le signer pour une trentaine d'employeurs.
5. **Plus de lien vers le référentiel des métiers de l'employeur d'origine.** Remplacé par un badge de famille
   RESPNC avec son code ROME (le référentiel RESPNC n'a pas de page par famille, seulement
   un PDF par fiche, déjà lié depuis chaque offre).
6. **Page « développeurs » refaite** : il n'y a pas d'API, donc plus de portail ni de clé
   — les données sont exposées en fichiers statiques (JSON-LD, RSS, flux ATS, dataset
   Hugging Face).

### Les flux produits au build

| Adresse | Pour qui | Contenu |
|---|---|---|
| `/index.xml` et 449 flux par section et par terme | lecteurs de flux | nouvelles offres |
| `/offres.json` | **le site lui-même** | toutes les offres, archives comprises, pour les filtres de « Toutes les offres » et les compteurs du menu |
| `/app-v1.json` | **l'application mobile** (`avps-app`) | les offres **ouvertes** seulement |
| `/{famille}/{ref}/index.json` | réutilisateurs | le JSON-LD complet d'une offre |
| `/flux_ats.xml` | agrégateurs d'emploi | format Indeed élargi |
| `/jobs-sitemap.xml` | moteurs | sitemap des offres |

⚠️ **`/offres.json` et `/app-v1.json` ne sont pas redondants**, et fusionner les deux
serait une régression. `/offres.json` porte **toutes** les offres parce que la
recherche du site doit retrouver une offre close dont on a la référence, et que les
archives ne sont jamais supprimées : à 723 octets par offre et 2333 AVP/an, il grossit
d'environ 1,6 Mo par an. L'application, elle, le retéléchargerait presque chaque jour
sur un forfait calédonien. Son flux est donc limité aux offres ouvertes et reste de
taille constante — 130 Ko pour 169 offres, mesuré le 21/09/2026.

⚠️ **`/app-v1.json` part sur des téléphones qui ne se mettent pas à jour.** On peut y
ajouter un champ, jamais en retirer ni en renommer un. Son contrat fait foi et vit
dans le dépôt qui le consomme : `avps-app/docs/contrat-flux-app.md`.

## 🛠️ Développer en local

```bash
git clone --recurse-submodules https://github.com/Strategie-Zen-IT/avps-content.git
cd avps-content
hugo server            # http://localhost:1313
```

Le thème [Relearn](https://mcshelby.github.io/hugo-theme-relearn/) est un sous-module :
sans `--recurse-submodules`, le build échoue.

Régénérer les données de familles après une mise à jour du référentiel du moteur :

```bash
python3 scripts/generer_familles.py
```

## ⚠️ Ne jamais reformater `layouts/`

Un formateur HTML/JS lancé sur `layouts/**/*.html` **corrompt les templates Go** : il
prend les `{{ … }}` pour du JavaScript et les réécrit. Deux familles de dégâts, et c'est
la moins visible qui est la plus dangereuse (constaté le 09/09/2026 sur le site d'origine) :

- **bruyant** — un `}}` coupé en `}` + `}` : Hugo échoue sur `unexpected "}" in operand`,
  on le voit tout de suite ;
- **silencieux** — un espace inséré *dans une chaîne littérale* :
  `{{ "vendor/leaflet/leaflet.css" }}` devenu `{{ " vendor/leaflet/leaflet.css" }}`.
  `relURL` émet alors une URL en `%20` qui répond **404**, la carte ne charge plus, et
  **le build passe au vert**. Ce dégât part en production sans aucun signal.

`.editorconfig` et `.vscode/settings.json` désactivent le formatage pour ces fichiers.
Après tout reformatage malgré tout, vérifier :

```bash
grep -rnE '\{\{ *" +[^"]' layouts/            # espaces en tête de chaîne Go
git diff                                       # SANS -w : c'est lui qui masque ce dégât
curl -o /dev/null -w '%{http_code}' <asset>    # le HTML publié est minifié : greper ne suffit pas
```

## ✅ Reste à faire

La liste complète et ordonnée est dans [`TODO.md`](TODO.md).
