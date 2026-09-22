# avps-content — reste à faire

État au 09/09/2026. Le site est porté et compile (`hugo --minify`, 39 pages à vide,
70 avec une fiche d'AVP de test, aucune erreur). **Rien n'est encore committé ni
déployé.**

Voir aussi [`avps-engine/TODO.md`](../avps-engine/TODO.md) pour le moteur.

---

## A. À savoir avant de commencer

**Ce dépôt se fait remplir, il ne se rédige pas.** Les fiches d'offres y sont déposées
par le moteur (une pull request par AVP, auto-mergée). Ce qui se modifie à la main :
`layouts/`, les pages éditoriales de `content/*.md`, `static/logos/`, `assets/css/`.

**Ne jamais lancer un formateur HTML sur `layouts/`.** Il prend les `{{ … }}` de Hugo
pour du JavaScript et les réécrit. Le dégât grave est le **silencieux** : un espace
inséré dans une chaîne littérale produit une URL en `%20` qui répond 404, et **le build
passe au vert**. `.editorconfig` et `.vscode/settings.json` désactivent le formatage pour
ces fichiers — détails et commandes de vérification dans le README.

---

## B. Mise en ligne (à faire AVANT le premier run du moteur)

Le moteur ouvre ses pull requests sur ce dépôt : il doit exister d'abord.

- [ ] **Pousser le dépôt** sur `Strategie-Zen-IT/avps-content`, sous-module compris :
      le thème Relearn est un sous-module, et sans lui le build échoue.
- [ ] **Activer GitHub Pages** — `Settings > Pages`, source **GitHub Actions** (le
      workflow `deploy_site.yaml` publie l'artefact, il ne pousse pas sur `gh-pages`).
- [ ] **Brancher le domaine `avps.nc`.** Le fichier `static/CNAME` est en place. La zone
      DNS est gérée dans Google Cloud DNS (hors de ce projet) : enregistrements **A** de
      l'apex vers les IP de GitHub Pages (`185.199.108.153`, `.109.153`, `.110.153`,
      `.111.153`), **AAAA** (`2606:50c0:8000::153` à `8003::153`), `www` en CNAME vers
      `strategie-zen-it.github.io`, TXT `_github-pages-challenge-strategie-zen-it` pour la
      vérification du domaine côté organisation. Puis domaine personnalisé côté dépôt et
      **Enforce HTTPS** une fois le certificat émis.
- [ ] **Vérifier que `baseURL` de `hugo.toml` correspond bien au domaine servi.** Un
      `baseURL` qui ne colle pas produit des liens et des assets cassés sans erreur de
      build.

## C. Identité visuelle (tout est provisoire)

Le site est fonctionnel mais n'a pas de charte. Rien ici n'est bloquant.

- [ ] **`themeVariant`** utilise `zen-light` / `zen-dark`, deux variantes livrées par
      Relearn, en attendant la charte d'avps.nc. ⚠️ Attention en y touchant : une variante
      dont le CSS est absent fait **échouer** le build Hugo, ce n'est pas un simple
      avertissement.
- [ ] **`static/assets/logo-avps.svg`** est un monogramme provisoire. Volontairement
      neutre : il ne doit évoquer aucune des collectivités agrégées, sous peine de
      laisser croire que l'une d'elles édite le site.
      ⚠️ **C'est la SOURCE de l'icône de l'application mobile** : `avps-app` en dérive
      par `scripts/generer_icones.py`, pour les deux stores et l'écran de lancement
      iOS. Le reprendre ici sans relancer ce script ferait diverger les deux
      identités. Suivi commun dans `avps-app` issue #26, à traiter en fin de projet.
- [x] **Couleurs des familles** (20/09/2026) : camaïeux par grand thème, sept univers de
      métiers au lieu des huit lettres ROME, deux tons par famille avec contraste WCAG
      4,5:1 garanti (`familles_couleurs.yml` pour les badges et le thème clair,
      `familles_couleurs_claires.yml` pour les libellés du thème sombre,
      `familles_themes.yml` pour le rattachement). Générés par
      `scripts/generer_familles.py`, ne pas éditer les YAML.
- [ ] **Aligner la palette des bannières** dans `avps-engine/src/pipeline/schema.py`
      (encore par lettre ROME) sur le ton foncé de `familles_couleurs.yml` : à faire dans
      le chantier bannières, pas ailleurs.
- [ ] **Déposer les logos** dans `static/logos/{sigle}.png` (voir le README du dossier
      pour la convention et la requête SQL qui donne les manquants par priorité). Le
      moteur essaie `{sigle}.png` puis `{collectivité-slug}.png` : déposer
      `nouvelle-caledonie.png` couvre d'un coup toutes les directions du gouvernement
      (DASS, DITTT, DAVAR…), il n'y a pas besoin d'un fichier par direction.
- [ ] N'ajouter que des logos dont la reproduction est autorisée par l'employeur.

## E. Contenu éditorial à relire

Les pages ont été réécrites pour la cible, mais elles engagent le site : à relire avant
la mise en ligne.

- [ ] **`content/a-propos.md`** — porte les mentions qui protègent le site : avps.nc
      n'est ni un employeur ni un intermédiaire de recrutement, n'est édité par aucune
      collectivité, n'enregistre aucune candidature, et **le PDF officiel fait seul foi**.
      Vérifier que la formulation te convient juridiquement.
- [ ] **`content/_index.md`** — page d'accueil : explique que le menu classe par métier
      et que les étiquettes filtrent par collectivité, commune, province, corps.
- [ ] **`content/developpeurs.md`** — refaite : il n'y a pas d'API, donc plus de portail
      ni de clé ; les données sont exposées en fichiers statiques (JSON-LD, RSS, flux
      ATS, dataset Hugging Face). Raccrochée au menu le 14/09/2026.
- [ ] **`content/mentions-legales.md`** — adaptée des mentions légales de
      strategiezenit.com (éditeur SARL Stratégie Zen IT, hébergeur GitHub Pages, aucun
      cookie, données de contact issues des avis officiels). À relire.
- [ ] **`params.dataset_url`** dans `hugo.toml` : renseigner l'URL du dataset Hugging
      Face une fois créé, pour que le lien du pied de page apparaisse.
- [x] `a-propos`, `stats`, `developpeurs` et `mentions-legales` sont dans les raccourcis du
      menu (14/09/2026). Elles restent `hidden: true` pour ne pas encombrer l'arborescence.

## F. Correctifs mineurs

- [x] `params.author.name` dans `hugo.toml` (14/09/2026).
- [ ] Quelques avertissements de dépréciation Hugo restent (`.Site.Data`,
      `.Language.LanguageCode`, `.Site.Languages`) : ils viennent du thème et des
      gabarits repris, et n'empêchent pas le build. À traiter lors d'une montée de
      version de Relearn.
- [ ] L'avertissement `relearnOutputFormat` concerne les formats de sortie personnalisés
      (`jobs_sitemap`, `flux_ats`, `sitemap-index`) sous Relearn 8. Inoffensif, mais à
      corriger si Relearn le durcit.

## G. Après la première ingestion

- [ ] **Vérifier une fiche réelle** de bout en bout : la collectivité et la direction
      s'affichent bien sur deux lignes distinctes, le badge de famille porte son code
      ROME, la bannière charge depuis le bucket public, le JSON-LD annonce la
      **collectivité** comme `hiringOrganization` (et pas le site).
- [ ] **Vérifier le flux ATS** : `<company>` doit porter la collectivité de chaque offre.
      Un flux qui annoncerait « avps.nc » comme entreprise recruteuse enverrait les
      candidats au mauvais endroit.
- [ ] **Regarder la tête du menu** quand les 41 familles commencent à se remplir : les
      `_index.md` sont créés à la demande par le moteur, donc le menu grossit avec le
      contenu. Si une rubrique reste quasi vide, c'est peut-être un problème de seuil
      d'appariement côté moteur, pas de contenu.
- [ ] **Surveiller le poids du dépôt.** Les bannières sont hors Git (bucket public), donc
      il ne devrait rester que du Markdown et du JSON — quelques Mo par an. Si `.git`
      enfle, c'est le signe que quelque chose remet des binaires dedans : c'est
      exactement ce qui a porté le site d'origine à 1,6 Go en quatre mois.

## H. En attente d'arbitrage

- [ ] **Durée de conservation des archives.** Les AVP clos sont déplacés dans
      `content/archives/` et jamais supprimés — décision motivée par 46 URL passées en
      404 sur le site d'origine, qui dégradaient l'indexation. À 2333 AVP/an, il faudra trancher une
      rétention et ce qu'on fait au-delà. Aucune durée n'est arrêtée à ce jour.
