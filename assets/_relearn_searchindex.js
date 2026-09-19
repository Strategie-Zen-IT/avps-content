{{- /* Surcharge de l'index de recherche du thème : même contenu, moins les offres
     CLÔTURÉES.

     Décision du 20/09/2026. La recherche est un outil pour trouver un poste auquel
     postuler : y faire remonter des offres dont la date limite est passée fait perdre du
     temps, d'autant qu'elles sont déjà retirées des listes, du menu, de la carte et des
     flux. Les pages restent publiées et accessibles par leur adresse — les liens partagés
     ou indexés continuent de fonctionner — elles ne sont simplement plus proposées.

     Le reste du fichier reprend la version du thème à l'identique. */ -}}
{{- $aujourdhui := now.Format "2006-01-02" }}
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
  {{- if $offreClose }}
  {{- else if partial "_relearn/pageIsSpecial.gotmpl" . }}
  {{- else if and .Title .RelPermalink (or (ne site.Params.disableSearchHiddenPages true) (not (partialCached "_relearn/pageIsHiddenSelfOrAncestor.gotmpl" (dict "page" . "to" site.Home) .Path site.Home.Path) ) ) }}
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
      "content" (trim (.Plain | htmlUnescape) "\n\r\t ")
    ) }}
  {{- end }}
{{- end -}}
var relearn_searchindex = {{ $pages | jsonify (dict "indent" "  ") }}
