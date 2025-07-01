import pandas as pd
from datetime import datetime
import os

# === 1. Chemin vers le fichier Excel ===
file_path = "EMP-Project/Data/statistic_4100_6_16_2025.xlsx"  # adapte si le nom change

# === 2. Charger et nettoyer les données ===
def load_and_clean_data(filepath):
    df = pd.read_excel(filepath)
    df_clean = df.iloc[1:].copy()  # Supprimer la 1ère ligne
    df_clean.reset_index(drop=True, inplace=True)
    return df_clean

# === 3. Détection des valeurs manquantes ===
def detect_missing_values(df):
    # On garde uniquement les colonnes contenant des dates (par ex. "06/06/2025")
    date_columns = [col for col in df.columns if "/" in col]
    missing_mask = df[date_columns].isna()
    rows_with_missing = df[missing_mask.any(axis=1)].copy()
    return rows_with_missing

# === 4. Génération du rapport CSV ===
def save_report(df_anomalies):
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.today().strftime("%Y-%m-%d")
    output_path = os.path.join(output_dir, f"rapport_anomalies_{today}.csv")
    df_anomalies.to_csv(output_path, index=False)
    print(f"✅ Rapport généré ici : {output_path}")

# === 5. Exécution complète ===
def main():
    print("📊 Analyse en cours...")

    # Étape 1 : Chargement
    try:
        df = load_and_clean_data(file_path)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé : {file_path}")
        return

    # Étape 2 : Détection des valeurs manquantes
    df_anomalies = detect_missing_values(df)

    # Étape 3 : Rapport
    if not df_anomalies.empty:
        print(f"⚠️ Valeurs manquantes détectées : {len(df_anomalies)} lignes concernées")
        save_report(df_anomalies)
    else:
        print("✅ Aucune valeur manquante détectée.")

if __name__ == "__main__":
    main()
