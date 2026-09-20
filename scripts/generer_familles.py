#!/usr/bin/env python3
"""Régénère les fichiers de données des familles de métiers (data/familles_*.yml).

Source de vérité : le référentiel RESPNC versionné dans le moteur
(`avps-engine/src/pipeline/ref/famille-code-rome.csv`). Les deux dépôts partagent ce
référentiel : il définit à la fois l'arborescence du site (`content/{famille}/`) et
l'énumération qui contraint l'extraction Gemini. Le régénérer ici évite de recopier
41 libellés à la main, ce qui était le point faible de la chaîne d'origine.

Couleurs : des CAMAÏEUX PAR GRAND THÈME (décision du 20/09/2026). Les 8 lettres ROME ne
convenaient pas : la lettre K regroupe 24 familles à elle seule. Sept thèmes lisibles
remplacent les lettres, chacun avec sa teinte ; dans un thème, les familles vont du plus
foncé au plus clair avec un léger glissement de teinte. Un badge d'une même couleur
générale = un même univers de métiers, le libellé fait le reste.

Contraste : la palette d'origine échouait au seuil WCAG 4,5:1 dans au moins un usage pour
chacune de ses 8 couleurs (mesuré le 20/09/2026). Un seul ton ne PEUT PAS convenir aux
trois usages du site : assez foncé pour porter du texte blanc (badge) et servir de texte
sur fond clair, il est trop foncé pour servir de texte sur le thème sombre. D'où DEUX tons
par famille, dérivés de la même teinte, chacun ajusté automatiquement jusqu'à 4,5:1 :
  - `familles_couleurs.yml`         ton foncé : fond des badges (texte blanc), libellés
                                    et bordures en thème clair, marqueurs de la carte ;
  - `familles_couleurs_claires.yml` ton clair : libellés en thème sombre
                                    (assets/css/theme-avps-dark.css).
Les deux fichiers ont la même forme (`familles: {libellé: "#RRGGBB"}`) que l'unique
fichier d'avant : rien n'a changé pour les gabarits qui ne lisent que le ton foncé.
`familles_themes.yml` donne le thème de chaque famille (légendes, regroupements).

Le moteur utilise les MÊMES tons pour les bannières : ce script réécrit aussi le
référentiel CSV du moteur en y ajoutant les colonnes `theme`, `couleur` (ton foncé) et
`couleur_claire`, que `avps-engine/src/pipeline/schema.py` lit (`couleur_famille`). Une
seule source pour les deux dépôts, régénérée d'un seul geste. Une collectivité abonnée
garde la main : sa charte (`employeurs_partenaires.yml`) prime sur la couleur de famille.

Usage :
    python3 scripts/generer_familles.py [chemin/vers/famille-code-rome.csv]
"""
import colorsys
import csv
import pathlib
import sys

DEFAUT_CSV = "../avps-engine/src/pipeline/ref/famille-code-rome.csv"

# Fonds réels du site (assets/css/theme-avps-{light,dark}.css) et texte des badges.
BLANC = "#FFFFFF"
FOND_CLAIR = "#FFFDF9"
FOND_SOMBRE = "#141917"
CONTRASTE_MIN = 4.5  # WCAG AA, texte normal

# Grands thèmes : (teinte °, saturation, familles du plus foncé au plus clair).
# Les rattachements hors lettre ROME (laboratoire -> santé, restauration -> social,
# imprimerie -> administration, patrimoine bâti -> technique, météo -> sécurité) ont été
# validés le 20/09/2026.
THEMES = {
    "Nature et cadre de vie": (135, 0.42, [
        "Agriculture et mer", "Espaces verts", "Environnement", "Propreté et gestion des déchets",
    ]),
    "Technique et infrastructures": (198, 0.55, [
        "Infrastructures, réseaux, eaux et assainissements", "Ingénierie industrielle minière et énergétique",
        "Transports terrestres et maritimes", "Aviation civile", "Ateliers et véhicules",
        "Postes et télécommunications", "Topographie et foncier", "Patrimoine bâti",
    ]),
    "Santé et laboratoire": (172, 0.60, [
        "Santé publique soins", "Santé publique équipements de santé", "Politique de santé publique",
        "Santé publique inspection et contrôle", "Laboratoire",
    ]),
    "Social, éducation et culture": (292, 0.35, [
        "Action sociale", "Education", "Formation professionnelle", "Animation", "Culture",
        "Habitat et logement", "Travail", "Restauration collective / hôtellerie",
    ]),
    "Administration et territoire": (222, 0.38, [
        "Administration générale", "Pilotage", "Ingénierie juridique", "Développement du territoire",
        "Urbanisme", "Population et affaires funéraires", "Communication", "Imprimerie",
    ]),
    "Sécurité et secours": (8, 0.55, [
        "Incendie et secours", "Prévention et sécurité", "Entretien, surveillance et logistique", "Météo",
    ]),
    "Finances, RH et numérique": (38, 0.62, [
        "Finances et budget", "Fiscalité et Trésor / douanes / affaires économiques",
        "Ressources Humaines", "Système d'information",
    ]),
}
DEFAUT = "#6B7280"          # famille absente des thèmes : gris neutre (ton foncé)
DEFAUT_CLAIR = "#B4B9C2"    # et son pendant pour le thème sombre
THEME_DEFAUT = "Autres métiers"


def _hex_vers_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def luminance(h: str) -> float:
    def lin(v):
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(x) for x in _hex_vers_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a: str, b: str) -> float:
    """Rapport de contraste WCAG entre deux couleurs hexadécimales."""
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hsl_vers_hex(h: float, s: float, l: float) -> str:
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l, s)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def ton_fonce(h: float, s: float, l: float) -> str:
    """Assombrit jusqu'à 4,5:1 à la fois avec du texte blanc et sur le fond clair."""
    while l > 0.08 and min(contraste(hsl_vers_hex(h, s, l), BLANC), contraste(hsl_vers_hex(h, s, l), FOND_CLAIR)) < CONTRASTE_MIN:
        l -= 0.005
    return hsl_vers_hex(h, s, l)


def ton_clair(h: float, s: float, l: float) -> str:
    """Éclaircit jusqu'à 4,5:1 sur le fond du thème sombre."""
    while l < 0.92 and contraste(hsl_vers_hex(h, s, l), FOND_SOMBRE) < CONTRASTE_MIN:
        l += 0.005
    return hsl_vers_hex(h, s, l)


def palette() -> dict:
    """{famille: (thème, ton foncé, ton clair)} pour toutes les familles des thèmes."""
    out = {}
    for theme, (teinte, sat, familles) in THEMES.items():
        n = len(familles)
        for i, famille in enumerate(familles):
            t = i / max(n - 1, 1)
            h = teinte - 8 + 16 * t          # glissement de teinte le long du camaïeu
            l = 0.24 + 0.22 * t              # du foncé au moyen
            s = sat * (1 - 0.25 * t)         # les tons clairs un peu moins saturés
            out[famille] = (theme, ton_fonce(h, s, l), ton_clair(h, s, l + 0.28))
    return out


ENTETE = """# ⚙️ FICHIER GÉNÉRÉ — ne pas éditer à la main.
#
# Source : avps-engine/src/pipeline/ref/famille-code-rome.csv (référentiel RESPNC,
# 41 familles de métiers de la fonction publique calédonienne).
# Régénérer avec : python3 scripts/generer_familles.py
#
"""

SORTIES = (
    (
        "data/familles_couleurs.yml",
        "# TON FONCÉ de chaque famille : fond des badges (texte blanc), libellés et bordures en\n"
        "# thème clair, marqueurs de la carte. Camaïeux par grand thème (voir familles_themes.yml),\n"
        "# contraste >= 4,5:1 garanti avec du blanc et sur le fond clair. Pendant pour le thème\n"
        "# sombre : familles_couleurs_claires.yml. Le moteur (schema.py) doit rester aligné.\n",
        lambda fam, rome, pal: pal.get(fam, (None, DEFAUT, None))[1],
    ),
    (
        "data/familles_couleurs_claires.yml",
        "# TON CLAIR de chaque famille : libellés colorés en thème sombre uniquement\n"
        "# (assets/css/theme-avps-dark.css). Même teinte que le ton foncé, contraste >= 4,5:1\n"
        "# garanti sur le fond sombre. Ne pas l'utiliser comme fond de badge.\n",
        lambda fam, rome, pal: pal.get(fam, (None, None, DEFAUT_CLAIR))[2],
    ),
    (
        "data/familles_themes.yml",
        "# Grand thème de chaque famille : sept univers de métiers qui portent les camaïeux.\n",
        lambda fam, rome, pal: pal.get(fam, (THEME_DEFAUT,))[0],
    ),
    (
        "data/familles_rome.yml",
        "# Code ROME de rattachement de chaque famille. Trois codes sont partagés par deux\n"
        "# familles (K1201, K1402, K2501) : c'est normal, la famille est la clé, pas le ROME.\n",
        lambda fam, rome, pal: rome,
    ),
)


def main() -> int:
    chemin = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else DEFAUT_CSV)
    if not chemin.exists():
        print(f"❌ Référentiel introuvable : {chemin}", file=sys.stderr)
        print("   Passez son chemin en argument si le moteur n'est pas dans le dossier voisin.", file=sys.stderr)
        return 1

    with open(chemin, encoding="utf-8-sig") as fh:
        familles = sorted(
            (ligne["id_famille"].strip(), ligne["code_rome"].strip())
            for ligne in csv.DictReader(fh)
            if ligne.get("id_famille")
        )
    if not familles:
        print(f"❌ Aucune famille lue dans {chemin}", file=sys.stderr)
        return 1

    pal = palette()
    noms = {f for f, _ in familles}
    sans_theme = sorted(noms - set(pal))
    hors_ref = sorted(set(pal) - noms)
    if sans_theme:
        print(f"⚠️ {len(sans_theme)} famille(s) sans thème, en gris neutre : {sans_theme}", file=sys.stderr)
    if hors_ref:
        print(f"⚠️ {len(hors_ref)} famille(s) des thèmes absentes du référentiel : {hors_ref}", file=sys.stderr)

    for fichier, commentaire, valeur in SORTIES:
        lignes = [ENTETE + commentaire, "familles:"]
        lignes += [f'  "{famille}": "{valeur(famille, rome, pal)}"' for famille, rome in familles]
        pathlib.Path(fichier).write_text("\n".join(lignes) + "\n", encoding="utf-8")
        print(f"✅ {fichier} — {len(familles)} familles")

    # Référentiel du moteur : mêmes familles, mêmes codes, plus les colonnes de couleur.
    # Réécrit trié, en UTF-8 sans BOM, fins de ligne \n. Les colonnes id_famille et
    # code_rome ne changent jamais ici : ce script n'invente aucune famille.
    with open(chemin, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["id_famille", "code_rome", "theme", "couleur", "couleur_claire"])
        for famille, rome in familles:
            theme, fonce, clair = pal.get(famille, (THEME_DEFAUT, DEFAUT, DEFAUT_CLAIR))
            w.writerow([famille, rome, theme, fonce, clair])
    print(f"✅ {chemin} — colonnes theme / couleur / couleur_claire réécrites pour le moteur")

    pire_fonce = min(min(contraste(f, BLANC), contraste(f, FOND_CLAIR)) for _, f, _ in pal.values())
    pire_clair = min(contraste(c, FOND_SOMBRE) for _, _, c in pal.values())
    print(f"🎨 {len(pal)} familles dans {len(THEMES)} thèmes ; contraste minimal : foncé {pire_fonce:.2f}, clair {pire_clair:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
