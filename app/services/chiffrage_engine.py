def calcular_chiffrage_inverse(prix_actuel: float, marge_cible_pct: float = 20.0):
    prix_cible = prix_actuel * (1 - (marge_cible_pct / 100))
    marge_actuelle = 15.0
    niveau_risque = "FAIBLE" if prix_actuel > 10000 else "MOYEN"
    
    return {
        "prix_actuel": prix_actuel,
        "prix_cible": round(prix_cible, 2),
        "marge_actuelle_pct": marge_actuelle,
        "marge_recommandee_pct": marge_cible_pct,
        "niveau_risque": niveau_risque,
        "niveau_confiance": "FORT"
    }
