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
    preparer_donnees_tip,
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
    supprimer_tip_insuffisants,
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
            
            # Traitement des équipes TIP (hors astreinte) et 3x8
            self.log_manager.log_message("🔄 Préparation des données TIP...")
            df_equipe_tip = preparer_donnees_tip(df_originel)
            
            # Variables pour stocker les résultats
            stats_final_tip = None
            moyennes_equipe_tip = None
            stats_final_3x8 = None
            moyennes_equipe_3x8 = None
            
            if not df_equipe_tip.empty:
                # Extraction des données 3x8 à partir des données TIP
                self.log_manager.log_message("🔄 Identification des employés en 3x8...")
                df_employes_3x8, df_employes_tip_standard = preparer_donnees_3x8(df_originel, df_equipe_tip)
                
                # Informer sur la séparation des 3x8 et TIP
                if not df_employes_3x8.empty:
                    nb_employes_3x8 = len(df_employes_3x8['Gentile'].unique())
                    nb_jours_3x8 = len(df_employes_3x8)
                    nb_employes_tip_total = len(df_equipe_tip['Gentile'].unique())
                    nb_employes_tip_standard = len(df_employes_tip_standard['Gentile'].unique())
                    
                    self.log_manager.log_message(f"✅ {nb_employes_3x8} employés en 3x8 identifiés avec {nb_jours_3x8} jours de données")
                    self.log_manager.log_message(f"📊 {nb_employes_tip_standard}/{nb_employes_tip_total} employés TIP après exclusion complète des employés 3x8")
                    
                    # Message explicite sur la méthode de séparation
                    self.log_manager.log_message("ℹ️ IMPORTANT: Les employés qui travaillent en 3x8 ont été complètement exclus des statistiques TIP")
                    self.log_manager.log_message("   Les employés 3x8 et TIP sont maintenant dans des catégories distinctes")
                
                # Traitement des données TIP (sans employés 3x8)
                self.log_manager.log_message("🔄 Traitement des données TIP (sans employés 3x8)...")
                if not df_employes_tip_standard.empty:
                    self.log_manager.log_message("🔄 Suppression des doublons TIP...")
                    df_unique_tip = supprimer_doublons(df_employes_tip_standard)
                    
                    self.log_manager.log_message("🔄 Application des filtres TIP...")
                    df_filtre_tip = appliquer_filtres_base(df_unique_tip)
                    self.log_manager.log_message(f"✅ {len(df_filtre_tip)} lignes TIP après filtrage")
                    
                    self.log_manager.log_message("🔄 Calcul des statistiques par employé TIP...")
                    stats_employes_tip = calculer_statistiques_employes(df_filtre_tip)
                    
                    self.log_manager.log_message("🔄 Formatage des données finales TIP...")
                    stats_final_tip = formater_donnees_finales(stats_employes_tip)
                    
                    self.log_manager.log_message("🔄 Suppression des employés TIP avec moins de 55 jours présents complets...")
                    stats_final_tip = supprimer_tip_insuffisants(stats_final_tip)
                    
                    self.log_manager.log_message("🔄 Calcul des moyennes par équipe TIP...")
                    moyennes_equipe_tip = calculer_moyennes_equipe(stats_final_tip)
                    
                    self.log_manager.log_message(f"✅ Statistiques TIP calculées pour {len(stats_final_tip)} employés (employés 3x8 exclus)")
                else:
                    self.log_manager.log_message("⚠️ Aucune donnée TIP (hors employés 3x8) trouvée")
                
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
                self.log_manager.log_message("⚠️ Aucune donnée TIP trouvée")
            
            self.log_manager.log_message("✅ Traitement terminé avec succès !")
            self.on_success(stats_final, moyennes_equipe, stats_final_tip, moyennes_equipe_tip, stats_final_3x8, moyennes_equipe_3x8)
            
        except Exception as e:
            error_msg = f"❌ Erreur lors du traitement :\n{str(e)}"
            self.on_error(error_msg)


class SummaryDisplayer:
    """Gestionnaire de l'affichage des résumés."""
    
    def __init__(self, log_manager):
        self.log_manager = log_manager
    
    def display_summary(self, stats_final, moyennes_equipe, csv_file_path, stats_tip=None, moyennes_tip=None, stats_3x8=None, moyennes_3x8=None):
        """Affiche le résumé de l'analyse dans le journal d'exécution et retourne le contenu."""
        if stats_final is None or moyennes_equipe is None:
            return None
        
        # Liste pour capturer le contenu du résumé
        summary_lines = []
        
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
        
        # Afficher le résumé et capturer le contenu
        summary_lines.extend(self._display_header())
        summary_lines.extend(self._display_general_stats(nb_employes, nb_equipes, moy_heures, moy_jours, moy_presence))
        summary_lines.extend(self._display_top_employees(top_employes))
        summary_lines.extend(self._display_best_team(best_team, heures_col))
        summary_lines.extend(self._display_team_breakdown(moyennes_equipe, heures_col))
        
        # Afficher les statistiques TIP si disponibles
        if stats_tip is not None and moyennes_tip is not None:
            summary_lines.extend(self._display_tip_section(stats_tip, moyennes_tip, heures_col))
        
        # Afficher les statistiques 3x8 si disponibles
        if stats_3x8 is not None and moyennes_3x8 is not None:
            summary_lines.extend(self._display_3x8_section(stats_3x8, moyennes_3x8, heures_col))
        
        summary_lines.extend(self._display_file_info(csv_file_path))
        summary_lines.extend(self._display_footer())
        
        # Retourner le contenu du résumé
        return '\n'.join(summary_lines)
    
    def _find_hours_column(self, moyennes_equipe):
        """Trouve la colonne des heures travaillées."""
        for col in moyennes_equipe.columns:
            if 'Heures_Travaillées' in col or 'heures' in col.lower():
                return col
        return None
    
    def _display_header(self):
        """Affiche l'en-tête du résumé."""
        lines = [
            "\n" + "="*60,
            "📊 RÉSUMÉ DE L'ANALYSE DES STATISTIQUES PMT",
            "="*60,
            ""
        ]
        for line in lines:
            self.log_manager.log_message(line)
        return lines
    
    def _display_general_stats(self, nb_employes, nb_equipes, moy_heures, moy_jours, moy_presence):
        """Affiche les statistiques générales."""
        lines = [
            "📈 STATISTIQUES GÉNÉRALES",
            f"• Nombre d'employés analysés : {nb_employes}",
            f"• Nombre d'équipes : {nb_equipes}",
            f"• Moyenne d'heures travaillées par employé : {moy_heures:.1f}h",
            f"• Moyenne de jours travaillés par employé : {moy_jours:.1f} jours",
            f"• Taux de présence moyen : {moy_presence:.1f}%",
            ""
        ]
        for line in lines:
            self.log_manager.log_message(line)
        return lines
    
    def _display_top_employees(self, top_employes):
        """Affiche le top 5 des employés."""
        lines = ["🏆 TOP 5 EMPLOYÉS (par heures travaillées)"]
        for i, (_, emp) in enumerate(top_employes.iterrows(), 1):
            lines.append(f"{i}. {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Total_Heures_Travaillées']:.1f}h")
        lines.append("")
        
        for line in lines:
            self.log_manager.log_message(line)
        return lines
    
    def _display_best_team(self, best_team, heures_col):
        """Affiche la meilleure équipe."""
        if heures_col and best_team is not None:
            lines = [
                "🏢 MEILLEURE ÉQUIPE (par moyenne d'heures)",
                f"• {best_team['Équipe']} : {best_team[heures_col]:.1f}h en moyenne"
            ]
            if 'Nb_Employés' in best_team:
                lines.append(f"• {best_team['Nb_Employés']:.0f} employés")
            lines.append("")
            
            for line in lines:
                self.log_manager.log_message(line)
            return lines
        return []
    
    def _display_team_breakdown(self, moyennes_equipe, heures_col):
        """Affiche la répartition par équipe."""
        lines = ["📋 RÉPARTITION PAR ÉQUIPE"]
        for _, team in moyennes_equipe.iterrows():
            nb_emp = team.get('Nb_Employés', 'N/A')
            if heures_col:
                heures_moy = team[heures_col]
                lines.append(f"• {team['Équipe']} : {nb_emp} employés, {heures_moy:.1f}h moy.")
            else:
                lines.append(f"• {team['Équipe']} : {nb_emp} employés")
        lines.append("")
        
        for line in lines:
            self.log_manager.log_message(line)
        return lines
    
    def _display_tip_section(self, stats_tip, moyennes_tip, heures_col):
        """Affiche la section TIP (équipes hors astreinte)."""
        lines = [
            "🔧 ÉQUIPES TIP (HORS ASTREINTE ET SANS EMPLOYÉS 3x8)",
            "",
            f"• Nombre d'employés TIP (sans employés 3x8) : {len(stats_tip)}",
            f"• Nombre d'équipes TIP : {len(moyennes_tip)}",
            f"• Moyenne d'heures travaillées TIP : {stats_tip['Total_Heures_Travaillées'].mean():.1f}h",
            f"• Taux de présence moyen TIP : {stats_tip['Présence_%_365j'].mean():.1f}%",
            "",
            "🏆 TOP 3 EMPLOYÉS TIP (par heures travaillées)"
        ]
        
        # Top 3 employés TIP
        top_employes_tip = stats_tip.nlargest(3, 'Total_Heures_Travaillées')
        for i, (_, emp) in enumerate(top_employes_tip.iterrows(), 1):
            lines.append(f"{i}. {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Total_Heures_Travaillées']:.1f}h")
        
        lines.extend([
            "",
            "📋 RÉPARTITION PAR ÉQUIPE TIP"
        ])
        
        # Répartition par équipe TIP
        for _, team in moyennes_tip.iterrows():
            nb_emp = team.get('Nb_Employés', 'N/A')
            if heures_col:
                heures_moy = team[heures_col]
                lines.append(f"• {team['Équipe']} : {nb_emp} employés, {heures_moy:.1f}h moy.")
            else:
                lines.append(f"• {team['Équipe']} : {nb_emp} employés")
        lines.append("")
        
        for line in lines:
            self.log_manager.log_message(line)
        return lines
    
    def _display_3x8_section(self, stats_3x8, moyennes_3x8, heures_col):
        """Affiche la section 3x8."""
        lines = [
            "🔄 ÉQUIPES EN 3x8",
            "",
            f"• Nombre d'employés en 3x8 : {len(stats_3x8)}",
            f"• Nombre d'équipes en 3x8 : {len(moyennes_3x8)}",
            "",
            "📅 STATISTIQUES DE PRÉSENCE 3x8",
            f"• Total jours travaillés : {stats_3x8['Jours_Travaillés'].sum():.1f}",
            f"• Total jours d'absence partielle : {stats_3x8['Jours_Absents_Partiels'].sum():.1f}",
            f"• Total jours d'absence : {stats_3x8['Total_Jours_Absents'].sum():.1f}",
            f"• Moyenne jours travaillés par employé : {stats_3x8['Jours_Travaillés'].mean():.1f}",
            f"• Moyenne jours d'absence partielle par employé : {stats_3x8['Jours_Absents_Partiels'].mean():.1f}",
            f"• Moyenne jours d'absence totale par employé : {stats_3x8['Total_Jours_Absents'].mean():.1f}",
            "",
            "⏰ RÉPARTITION DES POSTES 3x8",
            f"• Total postes du matin (7h30-15h30) : {stats_3x8['Postes_Matin'].sum()}",
            f"• Total postes d'après-midi (15h30-23h30) : {stats_3x8['Postes_Apres_Midi'].sum()}",
            f"• Total postes de nuit (23h30-7h30) : {stats_3x8['Postes_Nuit'].sum()}",
            f"• Moyenne postes du matin par employé : {stats_3x8['Postes_Matin'].mean():.1f}",
            f"• Moyenne postes d'après-midi par employé : {stats_3x8['Postes_Apres_Midi'].mean():.1f}",
            f"• Moyenne postes de nuit par employé : {stats_3x8['Postes_Nuit'].mean():.1f}",
            "",
            "🏆 TOP EMPLOYÉS 3x8 (par jours travaillés)"
        ]
        
        # Top employés 3x8 par jours travaillés
        if len(stats_3x8) > 0:
            top_employes_3x8 = stats_3x8.nlargest(min(3, len(stats_3x8)), 'Jours_Travaillés')
            for i, (_, emp) in enumerate(top_employes_3x8.iterrows(), 1):
                lines.append(
                    f"{i}. {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Jours_Travaillés']:.1f} jours travaillés, "
                    f"Absences: {emp['Jours_Absents_Partiels']:.1f} partiels - "
                    f"Postes: Matin: {emp['Postes_Matin']}, Après-midi: {emp['Postes_Apres_Midi']}, Nuit: {emp['Postes_Nuit']}"
                )
        
        lines.extend([
            "",
            "📋 RÉPARTITION PAR ÉQUIPE 3x8"
        ])
        
        # Répartition par équipe 3x8
        for _, team in moyennes_3x8.iterrows():
            nb_emp = team.get('Nb_Employés', 'N/A')
            moy_jours = team.get('Moy_Jours_Travaillés', 0)
            moy_absents_partiels = team.get('Moy_Jours_Absents_Partiels', 0)
            
            # Vérifier si nous avons les totaux ou les moyennes des postes
            if 'Total_Postes_Matin' in team:
                matin = team.get('Total_Postes_Matin', 0)
                apres_midi = team.get('Total_Postes_Apres_Midi', 0) 
                nuit = team.get('Total_Postes_Nuit', 0)
                lines.append(
                    f"• {team['Équipe']} : {nb_emp} employés, {moy_jours:.1f} jours travaillés, "
                    f"Absences: {moy_absents_partiels:.1f} partiels - "
                    f"Total postes: Matin: {matin}, Après-midi: {apres_midi}, Nuit: {nuit}"
                )
            else:
                matin = team.get('Moy_Postes_Matin', 0)
                apres_midi = team.get('Moy_Postes_Apres_Midi', 0) 
                nuit = team.get('Moy_Postes_Nuit', 0)
                lines.append(
                    f"• {team['Équipe']} : {nb_emp} employés, {moy_jours:.1f} jours travaillés, "
                    f"Absences: {moy_absents_partiels:.1f} partiels - "
                    f"Moyenne postes: Matin: {matin:.1f}, Après-midi: {apres_midi:.1f}, Nuit: {nuit:.1f}"
                )
        lines.append("")
        
        for line in lines:
            self.log_manager.log_message(line)
        return lines
    
    def _display_file_info(self, csv_file_path):
        """Affiche les informations du fichier."""
        lines = [
            "📁 FICHIER SOURCE",
            f"• {os.path.basename(csv_file_path)}",
            f"• Traité le {pd.Timestamp.now().strftime('%d/%m/%Y à %H:%M')}",
            ""
        ]
        for line in lines:
            self.log_manager.log_message(line)
        return lines
    
    def _display_footer(self):
        """Affiche le pied de page."""
        lines = [
            "💾 EXPORT",
            "• Utilisez le bouton 'Exporter vers Excel' pour sauvegarder les données complètes",
            "• Utilisez le bouton 'Exporter le résumé' pour sauvegarder ce résumé en fichier texte",
            "• Le fichier Excel contiendra tous les détails par employé et par équipe",
            "",
            "="*60
        ]
        for line in lines:
            self.log_manager.log_message(line)
        return lines 