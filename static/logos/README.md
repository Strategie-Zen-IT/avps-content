# Logos des employeurs : seulement sur accord écrit

Ce dossier ne contient aucun logo, et n'en reçoit un que lorsque l'employeur concerné a
donné son accord par écrit.

## Pourquoi

Reproduire l'emblème d'une collectivité sur un site qu'elle n'édite pas suppose son
autorisation. avps.nc republie des avis de vacance de poste ouverts, ce qui est licite,
mais cela ne vaut pas licence sur les marques et logos des employeurs cités. Les fichiers
déposés ici l'avaient été sans demande préalable ; ils ont été retirés le 20/09/2026.

## L'emplacement existe toujours

Rien n'a été supprimé côté affichage. Les fiches, les cartes, la page « Toutes les
offres », les pages de tags et les résultats de recherche réservent tous une place au
logo de l'employeur — elle affiche un symbole neutre tant qu'aucun accord n'a été obtenu.
La mise en page ne bougera donc pas le jour où un employeur s'abonne.

Le rendu est centralisé dans `layouts/partials/avp-logo-bloc.html`, et la résolution du
fichier dans `layouts/partials/avp-logo.html`.

## Pour ajouter un logo

1. Obtenir l'accord écrit de l'employeur. La page publique
   `content/employeurs-publics.md` explique la démarche et ce qu'elle finance.
2. Déposer le fichier ici, en PNG à fond transparent.
3. Déclarer l'employeur dans **`data/employeurs_partenaires.yml`**, le fichier unique où
   sont notés les accords obtenus, leur date, leur échéance et les consignes de couleur
   pour les illustrations.

Un fichier présent ici mais absent de `employeurs_partenaires.yml` n'est **pas** affiché :
la déclaration fait foi, pas la présence du fichier. C'est délibéré — un dépôt par
inadvertance ne doit pas suffire à publier un logo.

## Retrait

Un employeur peut retirer son accord à tout moment. Supprimer son entrée dans
`data/employeurs_partenaires.yml` suffit à faire disparaître le logo du site à la
publication suivante ; supprimer aussi le fichier PNG évite qu'il reste accessible à son
adresse.
