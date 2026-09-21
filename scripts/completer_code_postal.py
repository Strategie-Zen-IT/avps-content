#!/usr/bin/env python3
"""Complète `jobLocation.address.postalCode` des fiches déjà publiées.

POURQUOI
La source open data ne renseigne jamais le code postal : 0 fiche sur 237 au
21/09/2026. La Search Console le signale comme « Champ postalCode manquant (dans
jobLocation.address) » sur 140 éléments — un avertissement, pas une erreur bloquante,
mais une adresse incomplète pour la recherche locale.

Le code se déduit du chef-lieu de la commune. La table fait autorité et vit dans le
moteur (`CODE_POSTAL_NC` de src/pipeline/main.py), à côté du référentiel des 33 communes
et de la table des provinces ; ce script l'importe plutôt que d'en faire une copie.

REPRISE PONCTUELLE
Le moteur remplit désormais le champ à l'écriture, donc toute fiche publiée après le
21/09/2026 est déjà complète. Ce script rattrape les fiches antérieures, une fois, et le
résultat est commité : le JSON exposé à la réutilisation dit alors la même chose que la
page, comme pour la casse des tags et le champ `logo`.

Une valeur déjà présente n'est JAMAIS écrasée : si la source finit par fournir un code,
c'est elle qui fait foi.

Usage :
    python3 scripts/completer_code_postal.py [--dry-run]
"""
import collections
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
MOTEUR = RACINE.parent / "avps-engine" / "src" / "pipeline"


def charger_table():
    import importlib.util
    import os

    chemin = MOTEUR / "main.py"
    if not chemin.exists():
        sys.exit(f"❌ Moteur introuvable : {chemin}\n   Les deux dépôts doivent être côte à côte.")
    sys.path.insert(0, str(MOTEUR))
    os.environ.setdefault("PROJECT_ID", "avp-engine")
    spec = importlib.util.spec_from_file_location("pipeline_cp", chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules["pipeline_cp"] = module
    spec.loader.exec_module(module)
    return module.CODE_POSTAL_NC


def main():
    essai = "--dry-run" in sys.argv
    codes = charger_table()

    bilan = collections.Counter()
    inconnues = collections.Counter()
    for f in sorted(RACINE.glob("data/avps/*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        adresse = ((d.get("jobLocation") or {}).get("address") or {})
        if not adresse:
            bilan["sans adresse"] += 1
            continue
        if adresse.get("postalCode"):
            bilan["déjà renseigné"] += 1
            continue
        commune = (adresse.get("addressLocality") or "").strip()
        code = codes.get(commune)
        if not code:
            bilan["commune non reconnue"] += 1
            inconnues[commune or "(vide)"] += 1
            continue
        adresse["postalCode"] = code
        bilan["complété"] += 1
        if not essai:
            f.write_text(
                json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )

    verbe = "seraient complétées" if essai else "complétées"
    print(f"✅ {bilan['complété']} fiches {verbe}.")
    for k, v in bilan.most_common():
        if k != "complété":
            print(f"   {k:24} {v}")
    if inconnues:
        print("\n   communes non reconnues (adresse mal extraite par la source) :")
        for nom, n in inconnues.most_common():
            print(f"     {n:3}  {nom[:70]}")


if __name__ == "__main__":
    main()
