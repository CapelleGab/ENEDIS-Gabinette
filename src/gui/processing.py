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
    preparer_donnees_pit,
    preparer_donnees_3x8,
    supprimer_doublons,
    appliquer_filtres_base,
    appliquer_filtres_astreinte,
    calculer_statistiques_employes,
    calculer_moyennes_equipe,
    calculer_statistiques_3x8,
    calculer_moyennes_equipe_3x8,
    formater_donnees_finales,
    analyser_codes_presence,
    supprimer_astreinte_insuffisants,
    supprimer_pit_insuffisants,
    supprimer_3x8_insuffisants
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
            
            self.log_manager.log_message("🔄 Application des filtres spécifiques astreinte (garde les jours avec 'I')...")
            df_filtre = appliquer_filtres_astreinte(df_unique)
            self.log_manager.log_message(f"✅ {len(df_filtre)} lignes après filtrage (jours d'astreinte inclus)")
            
            self.log_manager.log_message("🔄 Analyse des codes de présence...")
            codes_uniques = analyser_codes_presence(df_filtre)
            
            self.log_manager.log_message("🔄 Calcul des statistiques par employé...")
            stats_employes = calculer_statistiques_employes(df_filtre)
            
            self.log_manager.log_message("🔄 Formatage des données finales...")
            stats_final = formater_donnees_finales(stats_employes)
            
            self.log_manager.log_message("🔄 Suppression des employés d'astreinte avec moins de 50 jours présents complets...")
            stats_final = supprimer_astreinte_insuffisants(stats_final)
            
            self.log_manager.log_message("🔄 Calcul des moyennes par équipe...")
            moyennes_equipe = calculer_moyennes_equipe(stats_final)
            
            # Traitement des équipes PIT (hors astreinte) et 3x8
            self.log_manager.log_message("🔄 Préparation des données PIT...")
            df_equipe_pit = preparer_donnees_pit(df_originel)
            
            # Variables pour stocker les résultats
            stats_final_pit = None
            moyennes_equipe_pit = None
            stats_final_3x8 = None
            moyennes_equipe_3x8 = None
            
            if not df_equipe_pit.empty:
                # Extraction des données 3x8 à partir des données PIT
                self.log_manager.log_message("🔄 Identification des employés en 3x8...")
                df_employes_3x8, df_employes_pit_standard = preparer_donnees_3x8(df_originel, df_equipe_pit)
                
                # Informer sur la séparation des 3x8 et PIT
                if not df_employes_3x8.empty:
                    nb_employes_3x8 = len(df_employes_3x8['Gentile'].unique())
                    nb_jours_3x8 = len(df_employes_3x8)
                    nb_employes_pit_total = len(df_equipe_pit['Gentile'].unique())
                    nb_employes_pit_standard = len(df_employes_pit_standard['Gentile'].unique())
                    
                    self.log_manager.log_message(f"✅ {nb_employes_3x8} employés en 3x8 identifiés avec {nb_jours_3x8} jours de données")
                    self.log_manager.log_message(f"📊 {nb_employes_pit_standard}/{nb_employes_pit_total} employés PIT après exclusion complète des employés 3x8")
                    
                    # Message explicite sur la méthode de séparation
                    self.log_manager.log_message("ℹ️ IMPORTANT: Les employés qui travaillent en 3x8 ont été complètement exclus des statistiques PIT")
                    self.log_manager.log_message("   Les employés 3x8 et PIT sont maintenant dans des catégories distinctes")
                
                # Traitement des données PIT (sans employés 3x8)
                self.log_manager.log_message("🔄 Traitement des données PIT (sans employés 3x8)...")
                if not df_employes_pit_standard.empty:
                    self.log_manager.log_message("🔄 Suppression des doublons PIT...")
                    df_unique_pit = supprimer_doublons(df_employes_pit_standard)
                    
                    self.log_manager.log_message("🔄 Application des filtres PIT...")
                    df_filtre_pit = appliquer_filtres_base(df_unique_pit)
                    self.log_manager.log_message(f"✅ {len(df_filtre_pit)} lignes PIT après filtrage")
                    
                    self.log_manager.log_message("🔄 Calcul des statistiques par employé PIT...")
                    stats_employes_pit = calculer_statistiques_employes(df_filtre_pit)
                    
                    self.log_manager.log_message("🔄 Formatage des données finales PIT...")
                    stats_final_pit = formater_donnees_finales(stats_employes_pit)
                    
                    self.log_manager.log_message("🔄 Suppression des employés PIT avec moins de 55 jours présents complets...")
                    stats_final_pit = supprimer_pit_insuffisants(stats_final_pit)
                    
                    self.log_manager.log_message("🔄 Calcul des moyennes par équipe PIT...")
                    moyennes_equipe_pit = calculer_moyennes_equipe(stats_final_pit)
                    
                    self.log_manager.log_message(f"✅ Statistiques PIT calculées pour {len(stats_final_pit)} employés (employés 3x8 exclus)")
                else:
                    self.log_manager.log_message("⚠️ Aucune donnée PIT (hors employés 3x8) trouvée")
                
                # Traitement des données 3x8 avec le nouveau calculateur spécifique
                self.log_manager.log_message("🔄 Traitement des données 3x8...")
                if not df_employes_3x8.empty:
                    self.log_manager.log_message("🔄 Suppression des doublons 3x8...")
                    df_unique_3x8 = supprimer_doublons(df_employes_3x8)
                    
                    # Calcul des statistiques spécifiques 3x8 (jours travaillés, absences, postes)
                    self.log_manager.log_message("🔄 Calcul des statistiques spécifiques 3x8...")
                    stats_final_3x8 = calculer_statistiques_3x8(df_unique_3x8)
                    
                    self.log_manager.log_message("🔄 Suppression des employés 3x8 selon les critères spécifiques...")
                    stats_final_3x8 = supprimer_3x8_insuffisants(stats_final_3x8)
                    
                    self.log_manager.log_message("🔄 Calcul des moyennes par équipe 3x8...")
                    moyennes_equipe_3x8 = calculer_moyennes_equipe_3x8(stats_final_3x8)
                    
                    # Afficher un résumé des postes 3x8
                    total_matin = stats_final_3x8['Postes_Matin'].sum() if 'Postes_Matin' in stats_final_3x8.columns else 0
                    total_apres_midi = stats_final_3x8['Postes_Apres_Midi'].sum() if 'Postes_Apres_Midi' in stats_final_3x8.columns else 0
                    total_nuit = stats_final_3x8['Postes_Nuit'].sum() if 'Postes_Nuit' in stats_final_3x8.columns else 0
                    
                    self.log_manager.log_message(f"✅ Statistiques 3x8 calculées pour {len(stats_final_3x8)} employés")
                    self.log_manager.log_message(f"📊 Répartition des postes 3x8: {total_matin} matin, {total_apres_midi} après-midi, {total_nuit} nuit")
                else:
                    self.log_manager.log_message("⚠️ Aucun employé en 3x8 trouvé")
            else:
                self.log_manager.log_message("⚠️ Aucune donnée PIT trouvée")
            
            self.log_manager.log_message("✅ Traitement terminé avec succès !")
            self.on_success(stats_final, moyennes_equipe, stats_final_pit, moyennes_equipe_pit, stats_final_3x8, moyennes_equipe_3x8)
            
        except Exception as e:
            error_msg = f"❌ Erreur lors du traitement :\n{str(e)}"
            self.on_error(error_msg)


class SummaryDisplayer:
    """Gestionnaire de l'affichage des résumés."""
    
    def __init__(self, log_manager):
        self.log_manager = log_manager
    
    def display_summary(self, stats_final, moyennes_equipe, csv_file_path, stats_pit=None, moyennes_pit=None, stats_3x8=None, moyennes_3x8=None):
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
        
        # Afficher les statistiques PIT si disponibles
        if stats_pit is not None and moyennes_pit is not None:
            self._display_pit_section(stats_pit, moyennes_pit, heures_col)
        
        # Afficher les statistiques 3x8 si disponibles
        if stats_3x8 is not None and moyennes_3x8 is not None:
            self._display_3x8_section(stats_3x8, moyennes_3x8, heures_col)
        
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
    
    def _display_pit_section(self, stats_pit, moyennes_pit, heures_col):
        """Affiche la section PIT (équipes hors astreinte)."""
        self.log_manager.log_message("🔧 ÉQUIPES PIT (HORS ASTREINTE ET SANS EMPLOYÉS 3x8)")
        
        # Statistiques générales PIT
        nb_employes_pit = len(stats_pit)
        nb_equipes_pit = len(moyennes_pit)
        moy_heures_pit = stats_pit['Total_Heures_Travaillées'].mean()
        moy_presence_pit = stats_pit['Présence_%_365j'].mean()
        
        self.log_manager.log_message(f"• Nombre d'employés PIT (sans employés 3x8) : {nb_employes_pit}")
        self.log_manager.log_message(f"• Nombre d'équipes PIT : {nb_equipes_pit}")
        self.log_manager.log_message(f"• Moyenne d'heures travaillées PIT : {moy_heures_pit:.1f}h")
        self.log_manager.log_message(f"• Taux de présence moyen PIT : {moy_presence_pit:.1f}%")
        
        # Top 3 employés PIT
        top_employes_pit = stats_pit.nlargest(3, 'Total_Heures_Travaillées')
        self.log_manager.log_message("")
        self.log_manager.log_message("🏆 TOP 3 EMPLOYÉS PIT (par heures travaillées)")
        for i, (_, emp) in enumerate(top_employes_pit.iterrows(), 1):
            self.log_manager.log_message(
                f"{i}. {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Total_Heures_Travaillées']:.1f}h"
            )
        
        # Répartition par équipe PIT
        self.log_manager.log_message("")
        self.log_manager.log_message("📋 RÉPARTITION PAR ÉQUIPE PIT")
        for _, team in moyennes_pit.iterrows():
            nb_emp = team.get('Nb_Employés', 'N/A')
            if heures_col:
                heures_moy = team[heures_col]
                self.log_manager.log_message(f"• {team['Équipe']} : {nb_emp} employés, {heures_moy:.1f}h moy.")
            else:
                self.log_manager.log_message(f"• {team['Équipe']} : {nb_emp} employés")
        self.log_manager.log_message("")
    
    def _display_3x8_section(self, stats_3x8, moyennes_3x8, heures_col):
        """Affiche la section 3x8."""
        self.log_manager.log_message("🔄 ÉQUIPES EN 3x8")
        
        # Statistiques générales 3x8
        nb_employes_3x8 = len(stats_3x8)
        nb_equipes_3x8 = len(moyennes_3x8)
        
        # Calcul des totaux des postes 3x8 (avec vérification de l'existence des colonnes)
        total_jours_travailles = stats_3x8['Jours_Travaillés'].sum() if 'Jours_Travaillés' in stats_3x8.columns else 0
        total_jours_absents_complets = stats_3x8['Jours_Absents_Complets'].sum() if 'Jours_Absents_Complets' in stats_3x8.columns else 0
        total_jours_absents_partiels = stats_3x8['Jours_Absents_Partiels'].sum() if 'Jours_Absents_Partiels' in stats_3x8.columns else 0
        total_jours_absents = stats_3x8['Total_Jours_Absents'].sum() if 'Total_Jours_Absents' in stats_3x8.columns else 0
        total_postes_matin = stats_3x8['Postes_Matin'].sum() if 'Postes_Matin' in stats_3x8.columns else 0
        total_postes_apres_midi = stats_3x8['Postes_Apres_Midi'].sum() if 'Postes_Apres_Midi' in stats_3x8.columns else 0
        total_postes_nuit = stats_3x8['Postes_Nuit'].sum() if 'Postes_Nuit' in stats_3x8.columns else 0
        
        # Calcul des moyennes par employé
        moy_jours_travailles = stats_3x8['Jours_Travaillés'].mean() if 'Jours_Travaillés' in stats_3x8.columns else 0
        moy_jours_absents_complets = stats_3x8['Jours_Absents_Complets'].mean() if 'Jours_Absents_Complets' in stats_3x8.columns else 0
        moy_jours_absents_partiels = stats_3x8['Jours_Absents_Partiels'].mean() if 'Jours_Absents_Partiels' in stats_3x8.columns else 0
        moy_total_jours_absents = stats_3x8['Total_Jours_Absents'].mean() if 'Total_Jours_Absents' in stats_3x8.columns else 0
        moy_postes_matin = stats_3x8['Postes_Matin'].mean() if 'Postes_Matin' in stats_3x8.columns else 0
        moy_postes_apres_midi = stats_3x8['Postes_Apres_Midi'].mean() if 'Postes_Apres_Midi' in stats_3x8.columns else 0
        moy_postes_nuit = stats_3x8['Postes_Nuit'].mean() if 'Postes_Nuit' in stats_3x8.columns else 0
        
        # Affichage des statistiques générales
        self.log_manager.log_message(f"• Nombre d'employés en 3x8 : {nb_employes_3x8}")
        self.log_manager.log_message(f"• Nombre d'équipes en 3x8 : {nb_equipes_3x8}")
        
        self.log_manager.log_message("\n📅 STATISTIQUES DE PRÉSENCE 3x8")
        self.log_manager.log_message(f"• Total jours travaillés : {total_jours_travailles:.1f}")
        self.log_manager.log_message(f"• Total jours d'absence complète : {total_jours_absents_complets:.1f}")
        self.log_manager.log_message(f"• Total jours d'absence partielle : {total_jours_absents_partiels:.1f}")
        self.log_manager.log_message(f"• Total jours d'absence (complets+partiels) : {total_jours_absents:.1f}")
        self.log_manager.log_message(f"• Moyenne jours travaillés par employé : {moy_jours_travailles:.1f}")
        self.log_manager.log_message(f"• Moyenne jours d'absence complète par employé : {moy_jours_absents_complets:.1f}")
        self.log_manager.log_message(f"• Moyenne jours d'absence partielle par employé : {moy_jours_absents_partiels:.1f}")
        self.log_manager.log_message(f"• Moyenne jours d'absence totale par employé : {moy_total_jours_absents:.1f}")
        
        self.log_manager.log_message("\n⏰ RÉPARTITION DES POSTES 3x8")
        self.log_manager.log_message(f"• Total postes du matin (7h30-15h30) : {total_postes_matin}")
        self.log_manager.log_message(f"• Total postes d'après-midi (15h30-23h30) : {total_postes_apres_midi}")
        self.log_manager.log_message(f"• Total postes de nuit (23h30-7h30) : {total_postes_nuit}")
        self.log_manager.log_message(f"• Moyenne postes du matin par employé : {moy_postes_matin:.1f}")
        self.log_manager.log_message(f"• Moyenne postes d'après-midi par employé : {moy_postes_apres_midi:.1f}")
        self.log_manager.log_message(f"• Moyenne postes de nuit par employé : {moy_postes_nuit:.1f}")
        
        # Top 3 employés 3x8 par jours travaillés
        if nb_employes_3x8 > 0:
            top_employes_3x8 = stats_3x8.nlargest(min(3, nb_employes_3x8), 'Jours_Travaillés')
            self.log_manager.log_message("")
            self.log_manager.log_message("🏆 TOP EMPLOYÉS 3x8 (par jours travaillés)")
            for i, (_, emp) in enumerate(top_employes_3x8.iterrows(), 1):
                self.log_manager.log_message(
                    f"{i}. {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Jours_Travaillés']:.1f} jours travaillés, "
                    f"Absences: {emp['Jours_Absents_Complets']:.1f} complets + {emp['Jours_Absents_Partiels']:.1f} partiels - "
                    f"Postes: Matin: {emp['Postes_Matin']}, Après-midi: {emp['Postes_Apres_Midi']}, Nuit: {emp['Postes_Nuit']}"
                )
        
        # Répartition par équipe 3x8
        if nb_equipes_3x8 > 0:
            self.log_manager.log_message("")
            self.log_manager.log_message("📋 RÉPARTITION PAR ÉQUIPE 3x8")
            for _, team in moyennes_3x8.iterrows():
                nb_emp = team.get('Nb_Employés', 'N/A')
                moy_jours = team.get('Moy_Jours_Travaillés', 0)
                moy_absents_complets = team.get('Moy_Jours_Absents_Complets', 0)
                moy_absents_partiels = team.get('Moy_Jours_Absents_Partiels', 0)
                
                # Vérifier si nous avons les totaux ou les moyennes des postes
                if 'Total_Postes_Matin' in team:
                    matin = team.get('Total_Postes_Matin', 0)
                    apres_midi = team.get('Total_Postes_Apres_Midi', 0) 
                    nuit = team.get('Total_Postes_Nuit', 0)
                    self.log_manager.log_message(
                        f"• {team['Équipe']} : {nb_emp} employés, {moy_jours:.1f} jours travaillés, "
                        f"Absences: {moy_absents_complets:.1f} complets + {moy_absents_partiels:.1f} partiels - "
                        f"Total postes: Matin: {matin}, Après-midi: {apres_midi}, Nuit: {nuit}"
                    )
                else:
                    matin = team.get('Moy_Postes_Matin', 0)
                    apres_midi = team.get('Moy_Postes_Apres_Midi', 0) 
                    nuit = team.get('Moy_Postes_Nuit', 0)
                    self.log_manager.log_message(
                        f"• {team['Équipe']} : {nb_emp} employés, {moy_jours:.1f} jours travaillés, "
                        f"Absences: {moy_absents_complets:.1f} complets + {moy_absents_partiels:.1f} partiels - "
                        f"Moyenne postes: Matin: {matin:.1f}, Après-midi: {apres_midi:.1f}, Nuit: {nuit:.1f}"
                    )
        
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