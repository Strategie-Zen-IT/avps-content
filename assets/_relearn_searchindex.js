{{- /* Surcharge de l'index de recherche du thème : même contenu, moins les offres
     CLÔTURÉES.

     Décision du 20/09/2026. La recherche est un outil pour trouver un poste auquel
     postuler : y faire remonter des offres dont la date limite est passée fait perdre du
     temps, d'autant qu'elles sont déjà retirées des listes, du menu, de la carte et des
     flux. Les pages restent publiées et accessibles par leur adresse — les liens partagés
     ou indexés continuent de fonctionner — elles ne sont simplement plus proposées.

     Ajout du 20/09/2026 : les taxonomies REDONDANTES sont également écartées.

     Une recherche sur « kanak » remontait quatre résultats pour une seule et même
     structure — sa page « direction », sa page « collectivité » et deux pages
     « mot-clé », l'une en capitales et l'autre non, parce que la source écrit son nom
     de deux façons. Devant ces quatre lignes quasi identiques, on ne sait pas laquelle
     cliquer, et aucune ne mène aux offres plus directement que les autres.

     Deux taxonomies sont donc retirées de l'index :

     - `tags`, qui est un fourre-tout : le moteur y recopie déjà la commune, la famille,
       le corps et l'employeur de chaque offre. Chacune de ses pages double donc une
       page de taxonomie dédiée, qui, elle, est mieux nommée.
     - `directions`, qui double `collectivites` pour toutes les structures n'ayant
       qu'une direction, et qui n'est pas un critère de recherche pour un candidat.

     Les pages restent publiées et accessibles : elles ne sont plus proposées ici.
     Restent indexées les taxonomies qui correspondent à une vraie question — famille de
     métier, collectivité, commune, province, corps. */ -}}
{{- $aujourdhui := now.Format "2006-01-02" }}
{{- $taxoExclues := slice "tags" "directions" }}
{{- $pages := slice }}
{{- range site.Pages }}
  {{- $offreClose := false }}
  {{- if .Params.ref }}
    {{- if eq .Params.archive true }}{{ $offreClose = true }}{{ end }}
    {{- with .Params.date_cloture }}
      {{- $d := string . }}
      {{- if and (eq (len $d) 10) (lt $d $aujourdhui) }}{{ $offreClose = true }}{{ end }}
    {{- end }}
  {{- end }}
  {{- $taxoRedondante := false }}
  {{- if in (slice "term" "taxonomy") .Kind }}
    {{- if in $taxoExclues .Data.Plural }}{{ $taxoRedondante = true }}{{ end }}
  {{- end }}
  {{- if $taxoRedondante }}
  {{- else if $offreClose }}
  {{- else if partial "_relearn/pageIsSpecial.gotmpl" . }}
  {{- else if and .Title .RelPermalink (or (ne site.Params.disableSearchHiddenPages true) (not (partialCached "_relearn/pageIsHiddenSelfOrAncestor.gotmpl" (dict "page" . "to" site.Home) .Path site.Home.Path) ) ) }}
    {{- /* Une page de LISTE n'est pas indexée sur son contenu, seulement sur son titre
           et sa description. Sa page affiche l'intitulé de dizaines d'offres : indexée
           en entier, elle répondait à presque toutes les recherches. « Toutes les
           offres » pesait à elle seule 25 000 caractères dans l'index.

           Plus grave, la page d'archives annulait en pratique l'exclusion des offres
           closes : chercher « infirmier » ne remontait plus la fiche close, mais
           remontait « Archives des offres clôturées », qui contient son titre.

           Les offres elles-mêmes restant indexées une par une, rien n'est perdu.

           Sont concernées : toutes les pages de section et de taxonomie, et les pages
           éditoriales qui portent `index_contenu: false` — celles dont le corps est
           produit par un shortcode de liste. */ -}}
    {{- $contenu := trim (.Plain | htmlUnescape) "\n\r\t " }}
    {{- if or (ne .Kind "page") (eq .Params.index_contenu false) }}{{ $contenu = "" }}{{ end }}
    {{- $tags := slice }}
    {{- range .GetTerms "tags" }}
      {{- $tags = $tags | append (partial "title.gotmpl" (dict "page" .Page "linkTitle" true) | plainify) }}
    {{- end }}
    {{- $pages = $pages | append (dict
      "uri" (partial "permalink.gotmpl" (dict "to" .))
      "title" (partial "title.gotmpl" (dict "page" .) | plainify)
      "tags" $tags
      "breadcrumb" (trim (partial "breadcrumbs.html" (dict "page" . "dirOnly" true) | plainify | htmlUnescape) "\n\r\t ")
      "description" (trim (or .Description .Summary | plainify | htmlUnescape) "\n\r\t " )
      "content" $contenu
    ) }}
  {{- end }}
{{- end -}}
var relearn_searchindex = {{ $pages | jsonify (dict "indent" "  ") }}
