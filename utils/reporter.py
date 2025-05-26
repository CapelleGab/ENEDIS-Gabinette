"""
Module de génération de rapports PMT.

author : CAPELLE Gabin
"""

from config import HORAIRE_DEBUT_REFERENCE, HORAIRE_FIN_REFERENCE, FICHIER_EXCEL, NOMS_FEUILLES


def afficher_resume_final(stats_final):
    """
    Affiche le résumé final des résultats.
    
    Args:
        stats_final (pd.DataFrame): DataFrame avec les statistiques finales
    """
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES RÉSULTATS - STATISTIQUES PMT")
    print("=" * 80)
    
    print("🔧 LOGIQUE APPLIQUÉE :")
    print("   • Tous les codes sont conservés")
    print("   • Code avec valeur : 8h - valeur = heures travaillées")
    print("   • Code sans valeur : 0h travaillées (8h d'absence)")
    print(f"   • Filtrage horaires : {HORAIRE_DEBUT_REFERENCE} à {HORAIRE_FIN_REFERENCE}")
    
    print(f"\n👥 ANALYSE DES EMPLOYÉS :")
    print(f"   • Nombre d'employés analysés : {len(stats_final)}")
    print(f"   • Moyenne jours présents complets : {stats_final['Jours_Présents_Complets'].mean():.1f} jours")
    print(f"   • Moyenne jours partiels : {stats_final['Jours_Partiels'].mean():.1f} jours")
    print(f"   • Moyenne total jours travaillés : {stats_final['Total_Jours_Travaillés'].mean():.1f} jours")
    print(f"   • Moyenne jours complets (8h) : {stats_final['Jours_Complets'].mean():.1f} jours")
    print(f"   • Moyenne jours absents : {stats_final['Jours_Absents'].mean():.1f} jours")
    
    print(f"\n⏰ ANALYSE DES HEURES :")
    print(f"   • Moyenne heures totales travaillées : {stats_final['Total_Heures_Travaillées'].mean():.1f} heures")
    print(f"   • Moyenne heures d'absence : {stats_final['Total_Heures_Absence'].mean():.1f} heures")
    print(f"   • Moyenne présence (% sur 365j) : {stats_final['Présence_%_365j'].mean():.1f}%")
    
    print(f"\n📁 FICHIER GÉNÉRÉ :")
    print(f"   • Nom : {FICHIER_EXCEL}")
    print(f"   • Feuilles : {NOMS_FEUILLES['statistiques']}, {NOMS_FEUILLES['moyennes']}")
    
    print("\n" + "=" * 80)
    print("✅ TRAITEMENT TERMINÉ AVEC SUCCÈS !")
    print("🎯 Vous pouvez maintenant ouvrir le fichier Excel pour consulter les résultats.")
    print("=" * 80) 