import pandas as pd
import numpy as np

from openpyxl import load_workbook
from openpyxl import Workbook


annee = '2024'
nom_fichier = f'Planning_journalier_{annee}.xlsx'

df_originel = pd.read_excel(nom_fichier)

#Liste des codes équipes à conserver
#codes_equipes = ['PV IT ASTREINTE','PV B ASTREINTE','PV G ASTREINTE','PV PE ASTREINTE','PF G SERVICE CONTINU','PF PE TERRAIN','PV B TERRAIN','PF IT TERRAIN']
codes_equipes = ['PV IT ASTREINTE','PV B ASTREINTE','PV G ASTREINTE','PV PE ASTREINTE']
#Liste des jours à enlever
jours_semaine = ['Samedi','Dimanche']
#Liste des codes absences à ne pas conserver
codes_absence = ['C','PL','RJ']

#Avoir un identifiant unique pour nom/prénom/équipe afin de distinguer les salariés qui auraient muté dans l'année d'une équipe à l'autre
df_originel['Gentile'] = df_originel['Nom'] +  ' ' + df_originel['Prénom'] + ' ' +df_originel['Equipe (Lib.)']

#Filtre sur les différents critères que l'on souhaite garder ou enlever
df_equipe = df_originel[df_originel['Equipe (Lib.)'].isin(codes_equipes)]
df_ferie = df_equipe[df_equipe['Jour férié']!='X']
df_astreinte = df_ferie[df_ferie['Astreinte']!='I']
df_weekend = df_astreinte[~df_astreinte['Désignation jour'].isin(jours_semaine)]
df_absence = df_weekend[~df_weekend['Code'].isin(codes_absence)]

#On réappelle df pour plus de simplicite
df = df_absence

# Convertir les colonnes 'Debut_absence' et 'Fin_absence' en datetime
date_format = "%H:%M:%S"
df['Heure début'] = pd.to_datetime(df['Heure début'], format = date_format,errors='coerce')
df['Heure fin'] = pd.to_datetime(df['Heure fin'], format =date_format,errors='coerce')


# Fonction pour obtenir le code horaire qui a réellement correspondu à la journée de l'agent
def get_horaire(row):
    if row['HE'] !=' ': #Horaire Effectué
        return row['HE']
    elif row['HTM'] !=' ': #Horaire Théorique Modifié
        return row['HTM']
    else:
        return row['HT'] #Horaire Théorique

# Appliquer la fonction pour obtenir le code horaire
df['Horaire'] = df.apply(get_horaire, axis=1)

#Pas utilisé pour l'instant
# Fonction pour calculer les heures d'absence entre 7h30 et 16h15
def calc_absence_heures(row):
    if pd.isna(row['Heure début']) or pd.isna(row['Heure fin']):
        return 0  # Si aucune absence n'est renseignée, on retourne 0 heures
    
    # Plages horaires de référence
    debut_plage = pd.to_datetime('07:30:00',format =date_format)
    fin_plage = pd.to_datetime('16:15:00',format =date_format)

    # Récupérer les heures d'absence réelles
    debut_absence = max(row['Heure début'], debut_plage)
    fin_absence = min(row['Heure fin'], fin_plage)
    
    # Vérifier si l'absence se situe dans la plage horaire valide
    if debut_absence >= fin_absence:
        return 0  # Si les heures sont invalides, on retourne 0 heures

    # Calcul des heures d'absence
    return (fin_absence - debut_absence).total_seconds() / 3600  # Conversion en heures

# Appliquer la fonction pour calculer les heures d'absence
#df['Heures_absence'] = df.apply(calc_absence_heures, axis=1)

# Regrouper par 'Groupe', 'Agent', et 'Date'
result = df.groupby(['Equipe (Lib.)', 'Gentile', 'Jour']).agg(
    Horaire=('Horaire', 'first'),
    Heures_absence=('Valeur', 'sum'),
    Codes = ('Code', list)
).reset_index()

#Enregistrer dans le fichier PMT_annee, la première feuille ne sert pas à grand chose pour l'instant
result.to_excel(f'PMT_{annee}.xlsx', index=False)

result = df.groupby(['Equipe (Lib.)', 'Gentile', 'Jour','Code']).agg(
    Horaire=('Horaire', 'first'),
    Heures_absence=('Valeur', 'sum')
).reset_index()

#Compter le nombre de jour de présence de l'agent dans l'équipe pour faire une projection sur une année complète / peut-être plutôt prendre en compte le df_originel avec les samedi/dimanche/jours_fériés
count_jours = df_equipe.groupby('Gentile')['Jour'].nunique().reset_index()
count_jours = count_jours.rename(columns={'Jour': 'Nb_Jours_distincts'})

#On garde les jour pour lesquels l'horaire a été J (journée complète travaillée) et où l'on a eu 0 heures d'absence (le code D est celui des heures supp aussi on garde ces journées là)
#Il faudra faire une modif pour incorporer les jours de B (7h30-11h30) et les jours de J avec une absence partielle en comptant leurs heures exactes
filtered_df = result[(result['Horaire'] == 'J') & ((result['Heures_absence'] == 0) | (result['Code'] == 'D'))]
result_2 = filtered_df.groupby(['Gentile','Equipe (Lib.)'])['Jour'].nunique().reset_index()

result_3 = pd.merge(count_jours, result_2, on='Gentile', how='inner')

#Ecriture dans le fichier PMT de l'année, pour l'instant il y a une erreur si la feuille est déjà existante, je n'ai pas géré ça
with pd.ExcelWriter(f'PMT_{annee}.xlsx', engine='openpyxl', mode='a') as writer:
    result_3.to_excel(writer, sheet_name='Indiv', index=False)
