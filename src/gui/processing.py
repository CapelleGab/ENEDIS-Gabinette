"""
Module de traitement des données pour PMT Analytics.

author : CAPELLE Gabin
"""

import os
import threading
import pandas as pd
import config
from src.utils import (
    charger_donnees_csv,
    preparer_donnees,
    supprimer_doublons,
    appliquer_filtres_base,
    calculer_statistiques_employes,
    calculer_moyennes_equipe,
    formater_donnees_finales,
    analyser_codes_presence
)


class DataProcessor:
    """Gestionnaire du traitement des données."""
    
    def __init__(self, log_manager, on_success_callback, on_error_callback):
        self.log_manager = log_manager
        self.on_success = on_success_callback
        self.on_error = on_error_callback
    
    def process_data(self, csv_file_path):
        """Traite les données PMT (exécuté dans un thread séparé)."""
        try:
            # Mise à jour du chemin du fichier CSV dans la config
            absolute_path = os.path.abspath(csv_file_path)
            config.FICHIER_CSV = absolute_path
            
            self.log_manager.log_message("🔄 Chargement des données CSV...")
            df_originel = charger_donnees_csv(config.FICHIER_CSV)
            self.log_manager.log_message(f"✅ {len(df_originel)} lignes chargées")
            
            self.log_manager.log_message("🔄 Préparation des données...")
            df_equipe = preparer_donnees(df_originel)
            
            self.log_manager.log_message("🔄 Suppression des doublons...")
            df_unique = supprimer_doublons(df_equipe)
            
            self.log_manager.log_message("🔄 Application des filtres...")
            df_filtre = appliquer_filtres_base(df_unique)
            self.log_manager.log_message(f"✅ {len(df_filtre)} lignes après filtrage")
            
            self.log_manager.log_message("🔄 Analyse des codes de présence...")
            codes_uniques = analyser_codes_presence(df_filtre)
            
            self.log_manager.log_message("🔄 Calcul des statistiques par employé...")
            stats_employes = calculer_statistiques_employes(df_filtre)
            
            self.log_manager.log_message("🔄 Formatage des données finales...")
            stats_final = formater_donnees_finales(stats_employes)
            
            self.log_manager.log_message("🔄 Calcul des moyennes par équipe...")
            moyennes_equipe = calculer_moyennes_equipe(stats_final)
            
            self.log_manager.log_message("✅ Traitement terminé avec succès !")
            self.on_success(stats_final, moyennes_equipe)
            
        except Exception as e:
            error_msg = f"❌ Erreur lors du traitement :\n{str(e)}"
            self.on_error(error_msg)


class SummaryDisplayer:
    """Gestionnaire de l'affichage des résumés."""
    
    def __init__(self, log_manager):
        self.log_manager = log_manager
    
    def display_summary(self, stats_final, moyennes_equipe, csv_file_path):
        """Affiche le résumé de l'analyse dans le journal d'exécution."""
        if stats_final is None or moyennes_equipe is None:
            return
        
        # Calculer les statistiques globales
        nb_employes = len(stats_final)
        nb_equipes = len(moyennes_equipe)
        
        # Statistiques générales
        moy_heures = stats_final['Total_Heures_Travaillées'].mean()
        moy_jours = stats_final['Total_Jours_Travaillés'].mean()
        moy_presence = stats_final['Présence_%_365j'].mean()
        
        # Top 5 employés par heures travaillées
        top_employes = stats_final.nlargest(5, 'Total_Heures_Travaillées')
        
        # Trouver la meilleure équipe
        heures_col = self._find_hours_column(moyennes_equipe)
        best_team = None
        if heures_col and not moyennes_equipe.empty:
            best_team = moyennes_equipe.loc[moyennes_equipe[heures_col].idxmax()]
        
        # Afficher le résumé
        self._display_header()
        self._display_general_stats(nb_employes, nb_equipes, moy_heures, moy_jours, moy_presence)
        self._display_top_employees(top_employes)
        self._display_best_team(best_team, heures_col)
        self._display_team_breakdown(moyennes_equipe, heures_col)
        self._display_file_info(csv_file_path)
        self._display_footer()
    
    def _find_hours_column(self, moyennes_equipe):
        """Trouve la colonne des heures travaillées."""
        for col in moyennes_equipe.columns:
            if 'Heures_Travaillées' in col or 'heures' in col.lower():
                return col
        return None
    
    def _display_header(self):
        """Affiche l'en-tête du résumé."""
        self.log_manager.log_message("\n" + "="*60)
        self.log_manager.log_message("📊 RÉSUMÉ DE L'ANALYSE DES STATISTIQUES PMT")
        self.log_manager.log_message("="*60)
        self.log_manager.log_message("")
    
    def _display_general_stats(self, nb_employes, nb_equipes, moy_heures, moy_jours, moy_presence):
        """Affiche les statistiques générales."""
        self.log_manager.log_message("📈 STATISTIQUES GÉNÉRALES")
        self.log_manager.log_message(f"• Nombre d'employés analysés : {nb_employes}")
        self.log_manager.log_message(f"• Nombre d'équipes : {nb_equipes}")
        self.log_manager.log_message(f"• Moyenne d'heures travaillées par employé : {moy_heures:.1f}h")
        self.log_manager.log_message(f"• Moyenne de jours travaillés par employé : {moy_jours:.1f} jours")
        self.log_manager.log_message(f"• Taux de présence moyen : {moy_presence:.1f}%")
        self.log_manager.log_message("")
    
    def _display_top_employees(self, top_employes):
        """Affiche le top 5 des employés."""
        self.log_manager.log_message("🏆 TOP 5 EMPLOYÉS (par heures travaillées)")
        for i, (_, emp) in enumerate(top_employes.iterrows(), 1):
            self.log_manager.log_message(
                f"{i}. {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Total_Heures_Travaillées']:.1f}h"
            )
        self.log_manager.log_message("")
    
    def _display_best_team(self, best_team, heures_col):
        """Affiche la meilleure équipe."""
        if heures_col and best_team is not None:
            self.log_manager.log_message("🏢 MEILLEURE ÉQUIPE (par moyenne d'heures)")
            self.log_manager.log_message(f"• {best_team['Équipe']} : {best_team[heures_col]:.1f}h en moyenne")
            if 'Nb_Employés' in best_team:
                self.log_manager.log_message(f"• {best_team['Nb_Employés']:.0f} employés")
            self.log_manager.log_message("")
    
    def _display_team_breakdown(self, moyennes_equipe, heures_col):
        """Affiche la répartition par équipe."""
        self.log_manager.log_message("📋 RÉPARTITION PAR ÉQUIPE")
        for _, team in moyennes_equipe.iterrows():
            nb_emp = team.get('Nb_Employés', 'N/A')
            if heures_col:
                heures_moy = team[heures_col]
                self.log_manager.log_message(f"• {team['Équipe']} : {nb_emp} employés, {heures_moy:.1f}h moy.")
            else:
                self.log_manager.log_message(f"• {team['Équipe']} : {nb_emp} employés")
        self.log_manager.log_message("")
    
    def _display_file_info(self, csv_file_path):
        """Affiche les informations du fichier."""
        self.log_manager.log_message("📁 FICHIER SOURCE")
        self.log_manager.log_message(f"• {os.path.basename(csv_file_path)}")
        self.log_manager.log_message(f"• Traité le {pd.Timestamp.now().strftime('%d/%m/%Y à %H:%M')}")
        self.log_manager.log_message("")
    
    def _display_footer(self):
        """Affiche le pied de page."""
        self.log_manager.log_message("💾 EXPORT")
        self.log_manager.log_message("• Utilisez le bouton 'Exporter vers Excel' pour sauvegarder les résultats")
        self.log_manager.log_message("• Le fichier Excel contiendra tous les détails par employé et par équipe")
        self.log_manager.log_message("")
        self.log_manager.log_message("="*60) 