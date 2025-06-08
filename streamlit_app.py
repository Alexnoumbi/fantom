import streamlit as st
import pandas as pd

st.set_page_config(page_title="Appariement CSV", layout="wide")
st.title("🔍 Appariement Noms/Numéros entre fichiers CSV")

with st.expander("ℹ️ Instructions"):
    st.markdown("""
    1. **Fichier Source** : CSV contenant les colonnes `noms` et `numeros` (la référence complète)
    2. **Fichier Cible** : CSV contenant une colonne `numeros` à compléter avec les noms
    3. L'application fusionnera les données et affichera le résultat
    4. Les numéros sans correspondance seront disponibles dans un espace séparé.
    5. Vous pouvez également charger un fichier pour corriger les numéros qui n'ont pas un format commençant par `2376`
    6. Vous pouvez aussi supprimer les "6" ajoutés ou standardiser les numéros à 9 chiffres après "237"
    7. Une option permet de supprimer les doublons sur la colonne `numeros` pour chaque fichier.
    """)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Fichier Source (noms + numeros)")
    source_file = st.file_uploader("Choisir le fichier source", type=["csv"], key="source")
    remove_duplicates_source = st.checkbox("❎ Supprimer les doublons (source)", key="dup_source")
with col2:
    st.subheader("Fichier Cible (numeros)")
    target_file = st.file_uploader("Choisir le fichier cible", type=["csv"], key="target")
    remove_duplicates_target = st.checkbox("❎ Supprimer les doublons (cible)", key="dup_target")

include_missing = st.checkbox("📌 Garder les lignes originales avec la colonne 'noms' vide", value=False)

st.subheader("📦 Corriger les numéros mal formés")
correction_file = st.file_uploader("Charger un fichier à corriger (colonne 'numeros')", type=["csv"], key="correction")
remove_duplicates_correction = st.checkbox("❎ Supprimer les doublons (correction)", key="dup_correction")

st.subheader("🧹 Supprimer les '6' en trop après 237")
delete6_file = st.file_uploader("Charger un fichier pour supprimer le '6' après 237 (colonne 'numeros')", type=["csv"], key="delete6")
remove_duplicates_delete6 = st.checkbox("❎ Supprimer les doublons (delete6)", key="dup_delete6")

st.subheader("🔄 Standardiser les numéros (ajouter ou retirer le '6' après 237)")
standardize_file = st.file_uploader("Charger un fichier à standardiser (colonne 'numeros')", type=["csv"], key="standardize")

def correct_phone_numbers(file):
    df = pd.read_csv(file, dtype=str).fillna("")
    df.columns = df.columns.str.strip()
    if "numeros" not in df.columns:
        st.error("Le fichier doit contenir une colonne 'numeros'.")
        return

    if remove_duplicates_correction:
        df = df.drop_duplicates(subset=["numeros"])

    def format_number(num):
        num = num.strip()
        if not num.startswith("237"):
            return num

        rest = num[3:]

        if num.startswith("2376"):
            return num
        if len(rest) == 8 and rest.isdigit():
            return "2376" + rest
        return "2376" + rest

    df["numeros"] = df["numeros"].apply(format_number)
    df['numeros'] = df['numeros'].apply(lambda x: f'="{x}"')

    st.success("Numéros corrigés avec succès !")
    st.dataframe(df, height=300)
    corrected_csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("💾 Télécharger le fichier corrigé", corrected_csv, file_name="numeros_corriges.csv", mime="text/csv")

def remove_six_after_237(file):
    df = pd.read_csv(file, dtype=str).fillna("")
    df.columns = df.columns.str.strip()
    if "numeros" not in df.columns:
        st.error("Le fichier doit contenir une colonne 'numeros'.")
        return

    if remove_duplicates_delete6:
        df = df.drop_duplicates(subset=["numeros"])

    def remove_6(num):
        num = num.strip()
        if num.startswith("2376") and len(num) == 13:
            return "237" + num[4:]
        return num

    df["numeros"] = df["numeros"].apply(remove_6)
    df['numeros'] = df['numeros'].apply(lambda x: f'="{x}"')

    st.success("Suppression du '6' effectuée avec succès !")
    st.dataframe(df, height=300)
    cleaned_csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("💾 Télécharger le fichier nettoyé", cleaned_csv, file_name="numeros_nettoyes.csv", mime="text/csv")

def standardize_phone_numbers(file):
    df = pd.read_csv(file, dtype=str).fillna("")
    df.columns = df.columns.str.strip()
    if "numeros" not in df.columns:
        st.error("Le fichier doit contenir une colonne 'numeros'.")
        return

    def clean_num(num):
        num = str(num).strip()
        if num.startswith('="') and num.endswith('"'):
            num = num[2:-1]
        elif num.startswith('"') and num.endswith('"'):
            num = num[1:-1]
        return num

    def standardize(num):
        num = clean_num(num)
        if num.startswith("2376"):
            # Retirer le '6' après '237'
            return "237" + num[4:]
        elif num.startswith("237"):
            # Ajouter un '6' après '237' si ce n'est pas déjà le cas
            if len(num) == 12 and num[3] != "6":
                return "2376" + num[3:]
        return num

    df["numeros"] = df["numeros"].apply(standardize)
    df['numeros'] = df['numeros'].apply(lambda x: f'="{x}"')

    st.success("Numéros standardisés avec succès !")
    st.dataframe(df, height=300)
    standardized_csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "💾 Télécharger le fichier standardisé", 
        standardized_csv, 
        file_name="numeros_standardises.csv", 
        mime="text/csv"
    )

def clean_and_merge(source_file, target_file):
    df_source = pd.read_csv(source_file, dtype=str).fillna("")
    df_target = pd.read_csv(target_file, dtype=str).fillna("")
    df_source.columns = df_source.columns.str.strip()
    df_target.columns = df_target.columns.str.strip()

    if remove_duplicates_source:
        df_source = df_source.drop_duplicates(subset=["numeros"])
    if remove_duplicates_target:
        df_target = df_target.drop_duplicates(subset=["numeros"])

    if not all(col in df_source.columns for col in ["noms", "numeros"]):
        st.error(f"Le fichier source doit contenir les colonnes 'noms' et 'numeros'. Colonnes trouvées : {list(df_source.columns)}")
        return None, None
    if "numeros" not in df_target.columns:
        st.error(f"Le fichier cible doit contenir la colonne 'numeros'. Colonnes trouvées : {list(df_target.columns)}")
        return None, None

    df_source['numeros'] = df_source['numeros'].astype(str).str.strip()
    df_source['noms'] = df_source['noms'].astype(str).str.strip()
    df_target['numeros'] = df_target['numeros'].astype(str).str.strip()

    result = df_target.merge(df_source, on="numeros", how="left")
    result = result[["numeros", "noms"] if "noms" in result.columns else ["numeros"]]

    result = result.fillna("")
    result['numeros'] = result['numeros'].apply(lambda x: f'="{x}"')

    missing = result[result["noms"] == ""]
    matched = result if include_missing else result[result["noms"] != ""]

    return matched, missing

if st.button("🔍 Effectuer l'appariement"):
    if not source_file or not target_file:
        st.error("Veuillez uploader les deux fichiers CSV.")
    else:
        try:
            matched, missing = clean_and_merge(source_file, target_file)
            if matched is not None:
                st.success("Appariement terminé !")

                tab1, tab2 = st.tabs(["✅ Numéros avec noms", "❌ Numéros sans noms"])

                with tab1:
                    st.dataframe(matched, height=500)
                    csv = matched.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="💾 Télécharger les numéros avec noms",
                        data=csv,
                        file_name="numeros_avec_noms.csv",
                        mime="text/csv"
                    )
                    st.info(f"**Statistiques :** {len(matched)} lignes exportées")

                with tab2:
                    if missing is not None and not missing.empty:
                        st.dataframe(missing[["numeros"]], height=300)
                        missing_csv = missing[["numeros"]].to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="💾 Télécharger les numéros sans noms",
                            data=missing_csv,
                            file_name="numeros_sans_noms.csv",
                            mime="text/csv"
                        )
                    else:
                        st.success("Tous les numéros ont un nom associé !")
        except Exception as e:
            st.error(f"Une erreur est survenue : {str(e)}")

if correction_file:
    correct_phone_numbers(correction_file)

if delete6_file:
    remove_six_after_237(delete6_file)

if standardize_file:
    standardize_phone_numbers(standardize_file)

st.subheader("➕ Ajouter le '6' après 237")
add6_file = st.file_uploader("Charger un fichier pour ajouter le '6' après 237 (colonne 'numeros')", type=["csv"], key="add6")
