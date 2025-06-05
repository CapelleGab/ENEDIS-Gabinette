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
    supprimer_3x8_insuffisants,
    enrichir_stats_avec_heures_supplementaires_hors_astreinte,
    enrichir_stats_avec_arrets_maladie,
    enrichir_moyennes_avec_nouvelles_stats,
    calculer_statistiques_arrets_maladie_tous_employes
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
            
            # Créer l'identifiant unique Gentile pour tous les employés
            self.log_manager.log_message("🔄 Création de l'identifiant unique pour tous les employés...")
            if 'Nom' in df_originel.columns and 'Prénom' in df_originel.columns and 'Equipe (Lib.)' in df_originel.columns:
                df_originel['Gentile'] = (df_originel['Nom'] + ' ' + 
                                         df_originel['Prénom'] + ' ' + 
                                         df_originel['Equipe (Lib.)'])
                self.log_manager.log_message("✅ Identifiant unique créé")
            else:
                self.log_manager.log_message("⚠️ Impossible de créer l'identifiant unique (colonnes manquantes)")
            
            # Calcul des statistiques d'arrêts maladie et heures supplémentaires pour TOUS les employés
            self.log_manager.log_message("🔄 Calcul des statistiques d'arrêts maladie et heures supplémentaires pour tous les employés...")
            try:
                arrets_maladie_tous = calculer_statistiques_arrets_maladie_tous_employes(df_originel)
                if not arrets_maladie_tous.empty:
                    self.log_manager.log_message(f"✅ Statistiques calculées pour {len(arrets_maladie_tous)} employés (arrêts maladie et heures supplémentaires)")
                else:
                    self.log_manager.log_message("⚠️ Aucune statistique d'arrêts maladie n'a pu être calculée")
                    arrets_maladie_tous = pd.DataFrame()
            except Exception as e:
                self.log_manager.log_message(f"⚠️ Erreur lors du calcul des statistiques d'arrêts maladie et heures supplémentaires : {str(e)}")
                self.log_manager.log_message("⚠️ L'analyse va continuer sans les statistiques complètes pour tous les employés")
                arrets_maladie_tous = pd.DataFrame()
            
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
            
            # ===== NOUVELLES STATISTIQUES POUR ASTREINTE (AVANT FORMATAGE) =====
            self.log_manager.log_message("🔄 Enrichissement avec heures supplémentaires hors astreinte...")
            stats_employes = enrichir_stats_avec_heures_supplementaires_hors_astreinte(stats_employes, df_unique, 'Gentile')
            
            self.log_manager.log_message("🔄 Enrichissement avec statistiques d'arrêts maladie et heures supplémentaires...")
            stats_employes = enrichir_stats_avec_arrets_maladie(stats_employes, df_unique, 'Gentile')
            
            self.log_manager.log_message("🔄 Formatage des données finales...")
            stats_final = formater_donnees_finales(stats_employes)
            
            self.log_manager.log_message("🔄 Suppression des employés d'astreinte avec moins de 50 jours présents complets...")
            stats_final = supprimer_astreinte_insuffisants(stats_final)
            
            self.log_manager.log_message("🔄 Calcul des moyennes par équipe...")
            moyennes_equipe = calculer_moyennes_equipe(stats_final)
            
            # Enrichir les moyennes avec les nouvelles statistiques
            self.log_manager.log_message("🔄 Enrichissement des moyennes avec nouvelles statistiques...")
            moyennes_equipe = enrichir_moyennes_avec_nouvelles_stats(moyennes_equipe, stats_final)
            
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
                    
                    # ===== NOUVELLES STATISTIQUES POUR TIP (AVANT FORMATAGE) =====
                    self.log_manager.log_message("🔄 Enrichissement TIP avec heures supplémentaires hors astreinte...")
                    stats_employes_tip = enrichir_stats_avec_heures_supplementaires_hors_astreinte(stats_employes_tip, df_unique_tip, 'Gentile')
                    
                    self.log_manager.log_message("🔄 Enrichissement TIP avec statistiques d'arrêts maladie et heures supplémentaires...")
                    stats_employes_tip = enrichir_stats_avec_arrets_maladie(stats_employes_tip, df_unique_tip, 'Gentile')
                    
                    self.log_manager.log_message("🔄 Formatage des données finales TIP...")
                    stats_final_tip = formater_donnees_finales(stats_employes_tip)
                    
                    self.log_manager.log_message("🔄 Suppression des employés TIP avec moins de 55 jours présents complets...")
                    stats_final_tip = supprimer_tip_insuffisants(stats_final_tip)
                    
                    # ===== NOUVELLES STATISTIQUES POUR TIP =====
                    self.log_manager.log_message("🔄 Calcul des moyennes par équipe TIP...")
                    moyennes_equipe_tip = calculer_moyennes_equipe(stats_final_tip)
                    
                    # Enrichir les moyennes TIP avec les nouvelles statistiques
                    self.log_manager.log_message("🔄 Enrichissement des moyennes TIP avec nouvelles statistiques...")
                    moyennes_equipe_tip = enrichir_moyennes_avec_nouvelles_stats(moyennes_equipe_tip, stats_final_tip)
                    
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
                    
                    # ===== NOUVELLES STATISTIQUES POUR 3x8 (AVANT SUPPRESSION) =====
                    self.log_manager.log_message("🔄 Enrichissement 3x8 avec heures supplémentaires hors astreinte...")
                    stats_final_3x8 = enrichir_stats_avec_heures_supplementaires_hors_astreinte(stats_final_3x8, df_unique_3x8, 'Gentile')
                    
                    self.log_manager.log_message("🔄 Enrichissement 3x8 avec statistiques d'arrêts maladie et heures supplémentaires...")
                    stats_final_3x8 = enrichir_stats_avec_arrets_maladie(stats_final_3x8, df_unique_3x8, 'Gentile')
                    
                    self.log_manager.log_message("🔄 Suppression des employés 3x8 selon les critères spécifiques...")
                    stats_final_3x8 = supprimer_3x8_insuffisants(stats_final_3x8)
                    
                    # ===== NOUVELLES STATISTIQUES POUR 3x8 =====
                    self.log_manager.log_message("🔄 Calcul des moyennes par équipe 3x8...")
                    moyennes_equipe_3x8 = calculer_moyennes_equipe_3x8(stats_final_3x8)
                    
                    # Enrichir les moyennes 3x8 avec les nouvelles statistiques
                    self.log_manager.log_message("🔄 Enrichissement des moyennes 3x8 avec nouvelles statistiques...")
                    moyennes_equipe_3x8 = enrichir_moyennes_avec_nouvelles_stats(moyennes_equipe_3x8, stats_final_3x8)
                    
                    # Afficher un résumé des postes 3x8
                    total_matin = stats_final_3x8['Postes_Matin'].sum() if 'Postes_Matin' in stats_final_3x8.columns else 0
                    total_apres_midi = stats_final_3x8['Postes_Apres_Midi'].sum() if 'Postes_Apres_Midi' in stats_final_3x8.columns else 0
                    total_nuit = stats_final_3x8['Postes_Nuit'].sum() if 'Postes_Nuit' in stats_final_3x8.columns else 0
                    
                    self.log_manager.log_message(f"✅ Statistiques 3x8 calculées pour {len(stats_final_3x8)} employés")
                    self.log_manager.log_message(f"📊 Répartition des postes 3x8: {total_matin} matin, {total_apres_midi} après-midi, {total_nuit} nuit")
                    
                    # Afficher un résumé des nouvelles statistiques
                    if 'Heures_Supp' in stats_final_3x8.columns:
                        total_hs_hors_astreinte_3x8 = stats_final_3x8['Heures_Supp'].sum()
                        self.log_manager.log_message(f"📊 Total heures supplémentaires 3x8 (hors jours avec 'I'): {total_hs_hors_astreinte_3x8:.1f}h")
                    
                    if 'Nb_Périodes_Arrêts' in stats_final_3x8.columns:
                        total_periodes_3x8 = stats_final_3x8['Nb_Périodes_Arrêts'].sum()
                        self.log_manager.log_message(f"📊 Total périodes d'arrêts maladie 3x8: {total_periodes_3x8}")
                    
                    if 'Nb_Jours_Arrêts_41' in stats_final_3x8.columns and 'Nb_Jours_Arrêts_5H' in stats_final_3x8.columns:
                        total_jours_41_3x8 = stats_final_3x8['Nb_Jours_Arrêts_41'].sum()
                        total_jours_5h_3x8 = stats_final_3x8['Nb_Jours_Arrêts_5H'].sum()
                        self.log_manager.log_message(f"📊 Total jours arrêts maladie 3x8: 41={total_jours_41_3x8}, 5H={total_jours_5h_3x8}")
                else:
                    self.log_manager.log_message("⚠️ Aucun employé en 3x8 trouvé")
            else:
                self.log_manager.log_message("⚠️ Aucune donnée TIP trouvée")
            
            # Afficher un résumé des nouvelles statistiques pour astreinte
            if 'Heures_Supp' in stats_final.columns:
                total_hs_hors_astreinte = stats_final['Heures_Supp'].sum()
                self.log_manager.log_message(f"📊 Total heures supplémentaires (hors jours avec 'I'): {total_hs_hors_astreinte:.1f}h")
            
            if 'Nb_Périodes_Arrêts' in stats_final.columns:
                total_periodes = stats_final['Nb_Périodes_Arrêts'].sum()
                self.log_manager.log_message(f"📊 Total périodes d'arrêts maladie: {total_periodes}")
                
            if 'Nb_Jours_Arrêts_41' in stats_final.columns:
                total_jours_41 = stats_final['Nb_Jours_Arrêts_41'].sum()
                self.log_manager.log_message(f"📊 Total jours arrêts maladie (code 41): {total_jours_41}")
            
            if 'Nb_Jours_Arrêts_5H' in stats_final.columns:
                total_jours_5h = stats_final['Nb_Jours_Arrêts_5H'].sum()
                self.log_manager.log_message(f"📊 Total jours arrêts maladie (code 5H): {total_jours_5h}")
            
            if 'Moy_Heures_Par_Arrêt_Maladie' in stats_final.columns:
                moy_heures_arret = stats_final['Moy_Heures_Par_Arrêt_Maladie'].mean()
                self.log_manager.log_message(f"📊 Moyenne heures par jour d'arrêt: {moy_heures_arret:.1f}h")
            
            self.log_manager.log_message("✅ Traitement terminé avec succès !")
            self.on_success(stats_final, moyennes_equipe, stats_final_tip, moyennes_equipe_tip, stats_final_3x8, moyennes_equipe_3x8, arrets_maladie_tous)
            
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
        summary_lines.extend(self._display_general_stats(nb_employes, nb_equipes, moy_heures, moy_jours, moy_presence, moyennes_equipe, heures_col))
        summary_lines.extend(self._display_best_team(best_team, heures_col))
        summary_lines.extend(self._display_team_breakdown(moyennes_equipe, heures_col))
        
        # Afficher les statistiques TIP si disponibles
        if stats_tip is not None and moyennes_tip is not None:
            summary_lines.extend(self._display_tip_section(stats_tip, moyennes_tip, heures_col))
        
        # Afficher les statistiques 3x8 si disponibles
        if stats_3x8 is not None and moyennes_3x8 is not None:
            summary_lines.extend(self._display_3x8_section(stats_3x8, moyennes_3x8, heures_col))
        
        # Afficher tous les TOP à la fin
        summary_lines.extend(self._display_all_tops(top_employes, stats_tip, stats_3x8))
        
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
    
    def _display_general_stats(self, nb_employes, nb_equipes, moy_heures, moy_jours, moy_presence, moyennes_equipe, heures_col):
        """Affiche les statistiques générales."""
        lines = [
            "📈 STATISTIQUES GÉNÉRALES",
            f"• Nombre d'employés analysés : {nb_employes}",
            f"• Nombre d'équipes : {nb_equipes}",
            f"• Moyenne d'heures travaillées par employé : {moy_heures:.1f}h ({moy_jours:.1f} jours)",
            f"• Taux de présence moyen : {moy_presence:.1f}%"
        ]
        
        # Calculer la moyenne pondérée des heures travaillées des 4 agences d'astreinte
        if heures_col and not moyennes_equipe.empty:
            total_heures_agences = 0
            total_employes_agences = 0
            
            for _, equipe in moyennes_equipe.iterrows():
                nb_emp = equipe.get('Nb_Employés', 0)
                heures_moy = equipe.get(heures_col, 0)
                if nb_emp > 0 and heures_moy > 0:
                    total_heures_agences += heures_moy * nb_emp
                    total_employes_agences += nb_emp
            
            if total_employes_agences > 0:
                moyenne_ponderee_heures = total_heures_agences / total_employes_agences
                moyenne_ponderee_jours = moyenne_ponderee_heures / 8  # Conversion en jours (8h = 1 jour)
                
                lines.extend([
                    f"• Moyenne pondérée des 4 agences : {moyenne_ponderee_heures:.1f}h ({moyenne_ponderee_jours:.1f} jours)"
                ])
        
        lines.append("")
        
        for line in lines:
            self.log_manager.log_message(line)
        return lines
    
    def _display_best_team(self, best_team, heures_col):
        """Affiche la meilleure équipe."""
        if heures_col and best_team is not None:
            heures_moy = best_team[heures_col]
            jours_moy = heures_moy / 8  # Conversion en jours
            lines = [
                "🏢 MEILLEURE ÉQUIPE (par moyenne d'heures)",
                f"• {best_team['Équipe']} : {heures_moy:.1f}h ({jours_moy:.1f} jours) en moyenne"
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
        
        # Variables pour calculer la moyenne pondérée
        total_heures_ponderees = 0
        total_employes = 0
        
        # Variables pour les heures supplémentaires par agence
        agences_stats = {}
        
        for _, team in moyennes_equipe.iterrows():
            nb_emp = team.get('Nb_Employés', 'N/A')
            if heures_col:
                heures_moy = team[heures_col]
                jours_moy = heures_moy / 8  # Conversion en jours
                line = f"• {team['Équipe']} : {nb_emp} employés, {heures_moy:.1f}h moy. ({jours_moy:.1f} jours)"
                
                # Ajouter les informations d'arrêts maladie si disponibles
                if 'Moy_Nb_Périodes_Arrêts' in team:
                    line += f", {team['Moy_Nb_Périodes_Arrêts']:.1f} périodes d'arrêt"
                
                if 'Moy_Moy_Heures_Par_Arrêt_Maladie' in team:
                    line += f", {team['Moy_Moy_Heures_Par_Arrêt_Maladie']:.1f}h/arrêt"
                
                # Ajouter les heures supplémentaires si disponibles
                if 'Moy_Heures_Supp' in team:
                    line += f", {team['Moy_Heures_Supp']:.1f}h supp."
                
                lines.append(line)
                
                # Calcul pour la moyenne pondérée
                if isinstance(nb_emp, (int, float)) and nb_emp > 0:
                    total_heures_ponderees += heures_moy * nb_emp
                    total_employes += nb_emp
                    
                    # Collecte des statistiques par agence (premier mot du nom d'équipe)
                    agence = team['Équipe'].split()[0]
                    if agence not in agences_stats:
                        agences_stats[agence] = {
                            'total_heures_supp': 0,
                            'total_employes': 0,
                            'equipes': []
                        }
                    
                    heures_supp = team.get('Moy_Heures_Supp', 0)
                    agences_stats[agence]['total_heures_supp'] += heures_supp * nb_emp
                    agences_stats[agence]['total_employes'] += nb_emp
                    agences_stats[agence]['equipes'].append(team['Équipe'])
            else:
                lines.append(f"• {team['Équipe']} : {nb_emp} employés")
        
        # Ajouter la moyenne pondérée si possible
        if total_employes > 0:
            moyenne_ponderee_heures = total_heures_ponderees / total_employes
            moyenne_ponderee_jours = moyenne_ponderee_heures / 8
            lines.extend([
                "",
                f"📊 Moyenne pondérée des équipes : {moyenne_ponderee_heures:.1f}h ({moyenne_ponderee_jours:.1f} jours)"
            ])
            
            # Ajouter des statistiques globales sur les arrêts maladie par agence
            if 'Moy_Nb_Périodes_Arrêts' in moyennes_equipe.columns:
                moy_periodes = moyennes_equipe['Moy_Nb_Périodes_Arrêts'].mean()
                lines.append(f"📊 Moyenne des périodes d'arrêt par agence : {moy_periodes:.1f} périodes")
                
            if 'Moy_Moy_Heures_Par_Arrêt_Maladie' in moyennes_equipe.columns:
                moy_heures_arret = moyennes_equipe['Moy_Moy_Heures_Par_Arrêt_Maladie'].mean()
                lines.append(f"📊 Moyenne des heures par arrêt maladie par agence : {moy_heures_arret:.1f}h")
                
            # Ajouter la moyenne des heures supplémentaires si disponible
            if 'Moy_Heures_Supp' in moyennes_equipe.columns:
                moy_heures_supp = moyennes_equipe['Moy_Heures_Supp'].mean()
                lines.append(f"📊 Moyenne des heures supplémentaires par équipe : {moy_heures_supp:.1f}h")
        
            # Ajouter les statistiques par agence
            if agences_stats:
                lines.append("")
                lines.append("📊 HEURES SUPPLÉMENTAIRES PAR AGENCE")
                for agence, stats in agences_stats.items():
                    if stats['total_employes'] > 0:
                        moy_heures_supp_agence = stats['total_heures_supp'] / stats['total_employes']
                        lines.append(f"• {agence} : {moy_heures_supp_agence:.1f}h en moyenne ({stats['total_employes']} employés)")
        
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
            f"• Taux de présence moyen TIP : {stats_tip['Présence_%_365j'].mean():.1f}%"
        ]
        
        # Ajouter les statistiques d'arrêts maladie et heures supplémentaires si disponibles
        if 'Nb_Périodes_Arrêts' in stats_tip.columns:
            lines.append(f"• Moyenne périodes d'arrêt TIP : {stats_tip['Nb_Périodes_Arrêts'].mean():.1f} périodes")
        
        if 'Moy_Heures_Par_Arrêt_Maladie' in stats_tip.columns:
            lines.append(f"• Moyenne heures par arrêt maladie TIP : {stats_tip['Moy_Heures_Par_Arrêt_Maladie'].mean():.1f}h")
        
        # Ajouter les statistiques d'heures supplémentaires si disponibles
        if 'Heures_Supp' in stats_tip.columns:
            lines.append(f"• Moyenne heures supplémentaires TIP : {stats_tip['Heures_Supp'].mean():.1f}h")
        
        # Calculer la moyenne pondérée des heures travaillées des équipes TIP
        if heures_col and not moyennes_tip.empty:
            total_heures_tip = 0
            total_employes_tip = 0
            
            # Variables pour les heures supplémentaires par agence TIP
            agences_tip_stats = {}
            
            for _, equipe in moyennes_tip.iterrows():
                nb_emp = equipe.get('Nb_Employés', 0)
                heures_moy = equipe.get(heures_col, 0)
                if nb_emp > 0 and heures_moy > 0:
                    total_heures_tip += heures_moy * nb_emp
                    total_employes_tip += nb_emp
                
                # Collecte des statistiques par agence (premier mot du nom d'équipe)
                if nb_emp > 0:
                    agence = equipe['Équipe'].split()[0]
                    if agence not in agences_tip_stats:
                        agences_tip_stats[agence] = {
                            'total_heures_supp': 0,
                            'total_employes': 0
                        }
                    
                    heures_supp = equipe.get('Moy_Heures_Supp', 0)
                    agences_tip_stats[agence]['total_heures_supp'] += heures_supp * nb_emp
                    agences_tip_stats[agence]['total_employes'] += nb_emp
            
            if total_employes_tip > 0:
                moyenne_ponderee_heures_tip = total_heures_tip / total_employes_tip
                moyenne_ponderee_jours_tip = moyenne_ponderee_heures_tip / 8
                lines.extend([
                    "",
                    "🏢 MOYENNE DES ÉQUIPES TIP",
                    f"• Moyenne pondérée d'heures travaillées : {moyenne_ponderee_heures_tip:.1f}h ({moyenne_ponderee_jours_tip:.1f} jours)"
                ])
                
                # Ajouter la moyenne des heures supplémentaires si disponible
                if 'Moy_Heures_Supp' in moyennes_tip.columns:
                    moy_heures_supp_tip = moyennes_tip['Moy_Heures_Supp'].mean()
                    lines.append(f"• Moyenne des heures supplémentaires par équipe TIP : {moy_heures_supp_tip:.1f}h")
                
                # Ajouter les statistiques par agence TIP
                if agences_tip_stats:
                    lines.append("")
                    lines.append("📊 HEURES SUPPLÉMENTAIRES PAR AGENCE TIP")
                    for agence, stats in agences_tip_stats.items():
                        if stats['total_employes'] > 0:
                            moy_heures_supp_agence = stats['total_heures_supp'] / stats['total_employes']
                            lines.append(f"• {agence} : {moy_heures_supp_agence:.1f}h en moyenne ({stats['total_employes']} employés)")
        
        lines.extend([
            "",
            "📋 RÉPARTITION PAR ÉQUIPE TIP"
        ])
        
        # Variables pour calculer la moyenne pondérée TIP
        total_heures_ponderees_tip = 0
        total_employes_tip = 0
        
        # Répartition par équipe TIP
        for _, team in moyennes_tip.iterrows():
            nb_emp = team.get('Nb_Employés', 'N/A')
            if heures_col:
                heures_moy = team[heures_col]
                jours_moy = heures_moy / 8  # Conversion en jours
                line = f"• {team['Équipe']} : {nb_emp} employés, {heures_moy:.1f}h moy. ({jours_moy:.1f} jours)"
                
                # Ajouter les informations d'arrêts maladie si disponibles
                if 'Moy_Nb_Périodes_Arrêts' in team:
                    line += f", {team['Moy_Nb_Périodes_Arrêts']:.1f} périodes d'arrêt"
                
                if 'Moy_Moy_Heures_Par_Arrêt_Maladie' in team:
                    line += f", {team['Moy_Moy_Heures_Par_Arrêt_Maladie']:.1f}h/arrêt"
                
                # Ajouter les heures supplémentaires si disponibles
                if 'Moy_Heures_Supp' in team:
                    line += f", {team['Moy_Heures_Supp']:.1f}h supp."
                
                lines.append(line)
                
                # Calcul pour la moyenne pondérée TIP
                if isinstance(nb_emp, (int, float)) and nb_emp > 0:
                    total_heures_ponderees_tip += heures_moy * nb_emp
                    total_employes_tip += nb_emp
            else:
                lines.append(f"• {team['Équipe']} : {nb_emp} employés")
        
        # Ajouter la moyenne pondérée TIP si possible
        if total_employes_tip > 0:
            moyenne_ponderee_heures_tip = total_heures_ponderees_tip / total_employes_tip
            moyenne_ponderee_jours_tip = moyenne_ponderee_heures_tip / 8
            lines.append(f"📊 Moyenne pondérée des équipes TIP : {moyenne_ponderee_heures_tip:.1f}h ({moyenne_ponderee_jours_tip:.1f} jours)")
            
            # Ajouter des statistiques globales sur les arrêts maladie par agence TIP
            if 'Moy_Nb_Périodes_Arrêts' in moyennes_tip.columns:
                moy_periodes = moyennes_tip['Moy_Nb_Périodes_Arrêts'].mean()
                lines.append(f"📊 Moyenne des périodes d'arrêt par agence TIP : {moy_periodes:.1f} périodes")
                
            if 'Moy_Moy_Heures_Par_Arrêt_Maladie' in moyennes_tip.columns:
                moy_heures_arret = moyennes_tip['Moy_Moy_Heures_Par_Arrêt_Maladie'].mean()
                lines.append(f"📊 Moyenne des heures par arrêt maladie par agence TIP : {moy_heures_arret:.1f}h")
        
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
            f"• Moyenne postes de nuit par employé : {stats_3x8['Postes_Nuit'].mean():.1f}"
        ]
        
        # Ajouter les statistiques d'arrêts maladie et heures supplémentaires si disponibles
        if 'Nb_Périodes_Arrêts' in stats_3x8.columns:
            lines.append(f"• Moyenne périodes d'arrêt 3x8 : {stats_3x8['Nb_Périodes_Arrêts'].mean():.1f} périodes")
        
        if 'Moy_Heures_Par_Arrêt_Maladie' in stats_3x8.columns:
            lines.append(f"• Moyenne heures par arrêt maladie 3x8 : {stats_3x8['Moy_Heures_Par_Arrêt_Maladie'].mean():.1f}h")
        
        # Ajouter les statistiques d'heures supplémentaires si disponibles
        if 'Heures_Supp' in stats_3x8.columns:
            lines.append(f"• Moyenne heures supplémentaires 3x8 : {stats_3x8['Heures_Supp'].mean():.1f}h")
        
        if 'Total_Heures_Supp_Service_Continu' in stats_3x8.columns:
            lines.append(f"• Moyenne heures supp. service continu : {stats_3x8['Total_Heures_Supp_Service_Continu'].mean():.1f}h")
        
        lines.append("")
        lines.append("📋 RÉPARTITION PAR ÉQUIPE 3x8")
        
        # Variables pour calculer la moyenne pondérée 3x8
        total_jours_ponderees_3x8 = 0
        total_employes_3x8 = 0
        
        # Variables pour les heures supplémentaires par agence 3x8
        agences_3x8_stats = {}
        
        # Répartition par équipe 3x8
        for _, team in moyennes_3x8.iterrows():
            nb_emp = team.get('Nb_Employés', 'N/A')
            moy_jours = team.get('Moy_Jours_Travaillés', 0)
            moy_absents_partiels = team.get('Moy_Jours_Absents_Partiels', 0)
            
            # Calcul pour la moyenne pondérée 3x8
            if isinstance(nb_emp, (int, float)) and nb_emp > 0 and moy_jours > 0:
                total_jours_ponderees_3x8 += moy_jours * nb_emp
                total_employes_3x8 += nb_emp
            
            # Collecte des statistiques par agence (premier mot du nom d'équipe)
            if isinstance(nb_emp, (int, float)) and nb_emp > 0:
                agence = team['Équipe'].split()[0]
                if agence not in agences_3x8_stats:
                    agences_3x8_stats[agence] = {
                        'total_heures_supp': 0,
                        'total_employes': 0
                    }
                
                heures_supp = team.get('Moy_Heures_Supp', 0)
                agences_3x8_stats[agence]['total_heures_supp'] += heures_supp * nb_emp
                agences_3x8_stats[agence]['total_employes'] += nb_emp
            
            # Vérifier si nous avons les totaux ou les moyennes des postes
            if 'Total_Postes_Matin' in team:
                matin = team.get('Total_Postes_Matin', 0)
                apres_midi = team.get('Total_Postes_Apres_Midi', 0) 
                nuit = team.get('Total_Postes_Nuit', 0)
                line = (
                    f"• {team['Équipe']} : {nb_emp} employés, {moy_jours:.1f} jours travaillés, "
                    f"Absences: {moy_absents_partiels:.1f} partiels - "
                    f"Total postes: Matin: {matin}, Après-midi: {apres_midi}, Nuit: {nuit}"
                )
            else:
                matin = team.get('Moy_Postes_Matin', 0)
                apres_midi = team.get('Moy_Postes_Apres_Midi', 0) 
                nuit = team.get('Moy_Postes_Nuit', 0)
                line = (
                    f"• {team['Équipe']} : {nb_emp} employés, {moy_jours:.1f} jours travaillés, "
                    f"Absences: {moy_absents_partiels:.1f} partiels - "
                    f"Moyenne postes: Matin: {matin:.1f}, Après-midi: {apres_midi:.1f}, Nuit: {nuit:.1f}"
                )
            
            # Ajouter les informations d'arrêts maladie si disponibles
            if 'Moy_Nb_Périodes_Arrêts' in team:
                line += f", {team['Moy_Nb_Périodes_Arrêts']:.1f} périodes d'arrêt"
            
            if 'Moy_Moy_Heures_Par_Arrêt_Maladie' in team:
                line += f", {team['Moy_Moy_Heures_Par_Arrêt_Maladie']:.1f}h/arrêt"
            
            # Ajouter les heures supplémentaires si disponibles
            if 'Moy_Heures_Supp' in team:
                line += f", {team['Moy_Heures_Supp']:.1f}h supp."
            
            lines.append(line)
        
        # Ajouter la moyenne pondérée 3x8 si possible
        if total_employes_3x8 > 0:
            moyenne_ponderee_jours_3x8 = total_jours_ponderees_3x8 / total_employes_3x8
            lines.append(f"📊 Moyenne pondérée des équipes 3x8 : {moyenne_ponderee_jours_3x8:.1f} jours travaillés")
            
            # Ajouter des statistiques globales sur les arrêts maladie par agence 3x8
            if 'Moy_Nb_Périodes_Arrêts' in moyennes_3x8.columns:
                moy_periodes = moyennes_3x8['Moy_Nb_Périodes_Arrêts'].mean()
                lines.append(f"📊 Moyenne des périodes d'arrêt par agence 3x8 : {moy_periodes:.1f} périodes")
                
            if 'Moy_Moy_Heures_Par_Arrêt_Maladie' in moyennes_3x8.columns:
                moy_heures_arret = moyennes_3x8['Moy_Moy_Heures_Par_Arrêt_Maladie'].mean()
                lines.append(f"📊 Moyenne des heures par arrêt maladie par agence 3x8 : {moy_heures_arret:.1f}h")
            
            # Ajouter la moyenne des heures supplémentaires si disponible
            if 'Moy_Heures_Supp' in moyennes_3x8.columns:
                moy_heures_supp_3x8 = moyennes_3x8['Moy_Heures_Supp'].mean()
                lines.append(f"📊 Moyenne des heures supplémentaires par équipe 3x8 : {moy_heures_supp_3x8:.1f}h")
            
            # Ajouter les statistiques par agence 3x8
            if agences_3x8_stats:
                lines.append("")
                lines.append("📊 HEURES SUPPLÉMENTAIRES PAR AGENCE 3x8")
                for agence, stats in agences_3x8_stats.items():
                    if stats['total_employes'] > 0:
                        moy_heures_supp_agence = stats['total_heures_supp'] / stats['total_employes']
                        lines.append(f"• {agence} : {moy_heures_supp_agence:.1f}h en moyenne ({stats['total_employes']} employés)")
        
        lines.append("")
        
        for line in lines:
            self.log_manager.log_message(line)
        return lines
    
    def _display_all_tops(self, top_employes, stats_tip, stats_3x8):
        """Affiche tous les TOP à la fin."""
        lines = [
            "",
            "🏆 TOP 5 EMPLOYÉS ASTREINTE (par heures travaillées)"
        ]
        
        # TOP 5 employés astreinte
        for i, (_, emp) in enumerate(top_employes.iterrows(), 1):
            lines.append(f"{i}. {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Total_Heures_Travaillées']:.1f}h")
        
        # TOP 3 employés TIP si disponibles
        if stats_tip is not None and not stats_tip.empty:
            lines.extend([
                "",
                "🏆 TOP 3 EMPLOYÉS TIP (par heures travaillées)"
            ])
            top_employes_tip = stats_tip.nlargest(3, 'Total_Heures_Travaillées')
            for i, (_, emp) in enumerate(top_employes_tip.iterrows(), 1):
                lines.append(f"{i}. {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Total_Heures_Travaillées']:.1f}h")
        
        # TOP employés 3x8 si disponibles
        if stats_3x8 is not None and not stats_3x8.empty:
            lines.extend([
                "",
                "🏆 TOP EMPLOYÉS 3x8 (par jours travaillés)"
            ])
            top_employes_3x8 = stats_3x8.nlargest(min(3, len(stats_3x8)), 'Jours_Travaillés')
            for i, (_, emp) in enumerate(top_employes_3x8.iterrows(), 1):
                lines.append(
                    f"{i}. {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Jours_Travaillés']:.1f} jours travaillés, "
                    f"Absences: {emp['Jours_Absents_Partiels']:.1f} partiels - "
                    f"Postes: Matin: {emp['Postes_Matin']}, Après-midi: {emp['Postes_Apres_Midi']}, Nuit: {emp['Postes_Nuit']}"
                )
        
        lines.extend([
            "",
            "="*60
        ])
        
        for line in lines:
            self.log_manager.log_message(line)
        return lines 