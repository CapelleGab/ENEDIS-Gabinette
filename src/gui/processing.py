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
        # Initialiser le StructuredLogger pour les statistiques par DR
        from src.utils.structured_logger import StructuredLogger
        self.structured_logger = StructuredLogger(log_manager)

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

            # Statistiques par DR pour ASTREINTE
            if "UM (Lib)" in stats_final.columns:
                # Vérifier que la colonne contient des valeurs
                dr_values = stats_final["UM (Lib)"].dropna().unique()
                if len(dr_values) > 0:
                    self.log_manager.log_message(f"✅ {len(dr_values)} Directions Régionales trouvées: {', '.join(dr_values[:3])}...")
                    self.structured_logger.log_dr_stats(stats_final, "ASTREINTE")
                else:
                    self.log_manager.log_message("⚠️ Colonne 'UM (Lib)' trouvée mais vide")

            self.log_manager.log_message("✅ Traitement terminé avec succès !")
            self.on_success(stats_final, moyennes_equipe, stats_final_tip, moyennes_equipe_tip, stats_final_3x8, moyennes_equipe_3x8, arrets_maladie_tous)

        except Exception as e:
            error_msg = f"❌ Erreur lors du traitement :\n{str(e)}"
            self.on_error(error_msg)


class SummaryDisplayer:
    """Gestionnaire de l'affichage des résumés."""

    def __init__(self, log_manager):
        self.log_manager = log_manager
        from src.utils.structured_logger import StructuredLogger
        self.structured_logger = StructuredLogger(log_manager)

    def display_summary(self, stats_final, moyennes_equipe, csv_file_path, stats_tip=None, moyennes_tip=None, stats_3x8=None, moyennes_3x8=None):
        """Affiche le résumé de l'analyse dans le journal d'exécution et retourne le contenu."""
        if stats_final is None or moyennes_equipe is None:
            return None

        # Réinitialiser le logger
        self.structured_logger.clear()

        # En-tête
        self._display_header()

        # Générer les statistiques pour chaque catégorie
        if stats_final is not None:
            self.structured_logger.log_employee_stats(stats_final, "ASTREINTE")

            # Statistiques par équipe pour ASTREINTE
            if moyennes_equipe is not None:
                for _, team in moyennes_equipe.iterrows():
                    heures_col = self._find_hours_column(moyennes_equipe)
                    if heures_col:
                        heures_moy = team[heures_col]
                        self.structured_logger.log(
                            f"Équipe {team['Équipe']}: {team.get('Nb_Employés', 0)} employés, {heures_moy:.1f}h",
                            "Employés", "ASTREINTE"
                        )

            # Statistiques par DR pour ASTREINTE
            if "UM (Lib)" in stats_final.columns:
                # Vérifier que la colonne contient des valeurs
                dr_values = stats_final["UM (Lib)"].dropna().unique()
                if len(dr_values) > 0:
                    self.log_manager.log_message(f"✅ {len(dr_values)} Directions Régionales trouvées: {', '.join(dr_values[:3])}...")
                    self.structured_logger.log_dr_stats(stats_final, "ASTREINTE")
                else:
                    self.log_manager.log_message("⚠️ Colonne 'UM (Lib)' trouvée mais vide")

        if stats_tip is not None:
            self.structured_logger.log_employee_stats(stats_tip, "TIP")

            # Statistiques par équipe pour TIP
            if moyennes_tip is not None:
                for _, team in moyennes_tip.iterrows():
                    heures_col = self._find_hours_column(moyennes_tip)
                    if heures_col:
                        heures_moy = team[heures_col]
                        self.structured_logger.log(
                            f"Équipe {team['Équipe']}: {team.get('Nb_Employés', 0)} employés, {heures_moy:.1f}h",
                            "Employés", "TIP"
                        )

            # Statistiques par DR pour TIP
            if "UM (Lib)" in stats_tip.columns:
                self.structured_logger.log_dr_stats(stats_tip, "TIP")

        if stats_3x8 is not None:
            self.structured_logger.log_employee_stats(stats_3x8, "3x8")

            # Statistiques par équipe pour 3x8
            if moyennes_3x8 is not None:
                for _, team in moyennes_3x8.iterrows():
                    moy_jours = team.get('Moy_Jours_Travaillés', 0)
                    self.structured_logger.log(
                        f"Équipe {team['Équipe']}: {team.get('Nb_Employés', 0)} employés, {moy_jours:.1f} jours",
                        "Employés", "3x8"
                    )

            # Statistiques par DR pour 3x8
            if "UM (Lib)" in stats_3x8.columns:
                self.structured_logger.log_dr_stats(stats_3x8, "3x8")

        # Génération des statistiques par agence
        dfs_to_check = [df for df in [stats_final, stats_tip, stats_3x8] if df is not None and not df.empty]
        for df in dfs_to_check:
            if "FSDUM (Lib)" in df.columns:
                pass  # La méthode log_agency_stats a été supprimée

        # Génération des statistiques globales
        self._add_global_stats(stats_final, stats_tip, stats_3x8)

        # Afficher les meilleurs employés
        self._add_top_employees(stats_final, stats_tip, stats_3x8)

        # Formater et afficher le résumé
        summary_content = self.structured_logger.format_summary()

        # Afficher le résumé dans le log manager
        self.log_manager.log_message("\n" + summary_content)

        return summary_content

    def _find_hours_column(self, moyennes_equipe):
        """Trouve la colonne des heures travaillées."""
        for col in moyennes_equipe.columns:
            if 'Heures_Travaillées' in col or 'heures' in col.lower():
                return col
        return None

    def _display_header(self):
        """Affiche l'en-tête du résumé."""
        header_msg = "📊 RÉSUMÉ DE L'ANALYSE DES STATISTIQUES PMT"
        self.structured_logger.log(header_msg, "Global")

    def _add_global_stats(self, stats_final, stats_tip, stats_3x8):
        """Ajoute les statistiques globales"""
        total_employes = 0
        total_heures = 0

        # Compter le total des employés
        if stats_final is not None:
            nb_employes = len(stats_final)
            total_employes += nb_employes
            if 'Total_Heures_Travaillées' in stats_final.columns:
                total_heures += stats_final['Total_Heures_Travaillées'].sum()

        if stats_tip is not None:
            nb_employes_tip = len(stats_tip)
            total_employes += nb_employes_tip
            if 'Total_Heures_Travaillées' in stats_tip.columns:
                total_heures += stats_tip['Total_Heures_Travaillées'].sum()

        if stats_3x8 is not None:
            nb_employes_3x8 = len(stats_3x8)
            total_employes += nb_employes_3x8
            # Pour 3x8, les heures sont calculées différemment si disponibles
            if 'Total_Heures_Travaillées' in stats_3x8.columns:
                total_heures += stats_3x8['Total_Heures_Travaillées'].sum()

        self.structured_logger.log(f"Total employés toutes catégories: {total_employes}", "Global")
        self.structured_logger.log(f"Total heures travaillées: {total_heures:.1f}h", "Global")

    def _add_top_employees(self, stats_final, stats_tip, stats_3x8):
        """Ajoute les meilleurs employés de chaque catégorie"""
        # TOP employés astreinte
        if stats_final is not None and not stats_final.empty:
            top_employes = stats_final.nlargest(5, 'Total_Heures_Travaillées')
            for i, (_, emp) in enumerate(top_employes.iterrows(), 1):
                self.structured_logger.log(
                    f"TOP {i}: {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Total_Heures_Travaillées']:.1f}h",
                    "Employés", "ASTREINTE"
                )

        # TOP employés TIP
        if stats_tip is not None and not stats_tip.empty:
            top_employes_tip = stats_tip.nlargest(3, 'Total_Heures_Travaillées')
            for i, (_, emp) in enumerate(top_employes_tip.iterrows(), 1):
                self.structured_logger.log(
                    f"TOP {i}: {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Total_Heures_Travaillées']:.1f}h",
                    "Employés", "TIP"
                )

        # TOP employés 3x8
        if stats_3x8 is not None and not stats_3x8.empty:
            top_employes_3x8 = stats_3x8.nlargest(min(3, len(stats_3x8)), 'Jours_Travaillés')
            for i, (_, emp) in enumerate(top_employes_3x8.iterrows(), 1):
                self.structured_logger.log(
                    f"TOP {i}: {emp['Prénom']} {emp['Nom']} ({emp['Équipe']}) : {emp['Jours_Travaillés']:.1f} jours",
                    "Employés", "3x8"
                )
