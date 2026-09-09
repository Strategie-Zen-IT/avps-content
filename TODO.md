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
- [ ] **Brancher le domaine `avps.nc`.** Le fichier `CNAME` est déjà en place. Il reste,
      chez le registrar `.nc`, les enregistrements **A** de l'apex vers les IP de GitHub
      Pages (`185.199.108.153`, `.109.153`, `.110.153`, `.111.153` — à revérifier dans la
      doc GitHub le jour J), puis l'activation du domaine personnalisé côté dépôt et
      **Enforce HTTPS** une fois le certificat émis.
- [ ] **Vérifier que `baseURL` de `hugo.toml` correspond bien au domaine servi.** Un
      `baseURL` qui ne colle pas produit des liens et des assets cassés sans erreur de
      build.

## C. Identité visuelle (tout est provisoire)

Le site est fonctionnel mais n'a pas de charte. Rien ici n'est bloquant.

- [ ] **`themeVariant`** utilise `zen-light` / `zen-dark`, deux variantes livrées par
      Relearn. Les variantes `opt-light` / `opt-dark` de la chaîne OPT n'ont pas été
      reprises (c'était la charte de l'OPT). ⚠️ Attention en y touchant : une variante
      dont le CSS est absent fait **échouer** le build Hugo, ce n'est pas un simple
      avertissement.
- [ ] **`static/assets/logo-avps.svg`** est un monogramme provisoire. Volontairement
      neutre : il ne doit évoquer aucune des collectivités agrégées, sous peine de
      laisser croire que l'une d'elles édite le site.
- [ ] **`data/familles_couleurs.yml`** porte une palette provisoire : **une couleur par
      domaine ROME** (8 présents) et non par famille — 41 couleurs ne se distinguent pas
      à l'œil. Ce fichier est **généré** : éditer `scripts/generer_familles.py`, pas le
      YAML. Les mêmes valeurs sont dupliquées dans `avps-engine/src/pipeline/schema.py`
      (palette des prompts de bannière) : **garder les deux alignées**.

## D. Logos des employeurs

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
      ATS, dataset Hugging Face). Page `hidden: true`, à raccrocher au menu si tu veux
      qu'elle soit visible.
- [ ] Décider si `a-propos` et `stats` restent `hidden: true` (héritage de l'OPT) ou
      rejoignent les raccourcis du menu.

## F. Correctifs mineurs

- [ ] **`params.author` → `params.author.name`** dans `hugo.toml` (déprécié par
      Relearn 5.23). Simple avertissement au build pour l'instant.
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
      exactement ce qui a porté `odata-avps` à 1,6 Go en quatre mois.

## H. En attente d'arbitrage

- [ ] **Durée de conservation des archives.** Les AVP clos sont déplacés dans
      `content/archives/` et jamais supprimés — décision motivée par 46 URL passées en
      404 côté OPT, qui dégradaient l'indexation. À 2333 AVP/an, il faudra trancher une
      rétention et ce qu'on fait au-delà. Aucune durée n'est arrêtée à ce jour.
