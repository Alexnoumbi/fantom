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
    """)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Fichier Source (noms + numeros)")
    source_file = st.file_uploader("Choisir le fichier source", type=["csv"], key="source")
with col2:
    st.subheader("Fichier Cible (numeros)")
    target_file = st.file_uploader("Choisir le fichier cible", type=["csv"], key="target")

def clean_and_merge(source_file, target_file):
    df_source = pd.read_csv(source_file, dtype=str)
    df_target = pd.read_csv(target_file, dtype=str)
    df_source.columns = df_source.columns.str.strip()
    df_target.columns = df_target.columns.str.strip()

    # Sécurité sur les noms de colonnes
    if not all(col in df_source.columns for col in ["noms", "numeros"]):
        st.error(f"Le fichier source doit contenir les colonnes 'noms' et 'numeros'. Colonnes trouvées : {list(df_source.columns)}")
        return None, None
    if "numeros" not in df_target.columns:
        st.error(f"Le fichier cible doit contenir la colonne 'numeros'. Colonnes trouvées : {list(df_target.columns)}")
        return None, None

    # Nettoyage et préparation
    df_source['numeros'] = df_source['numeros'].astype(str).str.strip()
    df_source['noms'] = df_source['noms'].astype(str).str.strip()
    df_target['numeros'] = df_target['numeros'].astype(str).str.strip()

    # Appariement
    result = df_target.merge(df_source, on="numeros", how="left")

    # Colonnes finales : conserver l'ordre cible puis noms
    result = result[["numeros", "noms"] if "noms" in result.columns else ["numeros"]]

    # Numéros sans noms associés
    missing = result[result["noms"].isna()]

    return result, missing

if st.button("🔍 Effectuer l'appariement"):
    if not source_file or not target_file:
        st.error("Veuillez uploader les deux fichiers CSV.")
    else:
        try:
            result, missing = clean_and_merge(source_file, target_file)
            if result is not None:
                st.success("Appariement terminé !")

                tab1, tab2 = st.tabs(["📊 Résultat complet", "📥 Numéros sans noms"])

                with tab1:
                    st.dataframe(result, height=500)
                    csv = result.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="💾 Télécharger le résultat complet",
                        data=csv,
                        file_name="resultat_appariement.csv",
                        mime="text/csv"
                    )
                    matched = result["noms"].notna().sum()
                    total = len(result)
                    percent = (matched / total * 100) if total else 0
                    st.info(f"**Statistiques :** {matched}/{total} correspondances trouvées ({percent:.1f}%)")

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

# Nouveau bloc : affichage direct après upload
if source_file and target_file:
    try:
        result, missing = clean_and_merge(source_file, target_file)
        if result is not None:
            with st.expander("💾 Télécharger les contacts avec noms"):
                with_names = result[result["noms"].notna()]
                st.dataframe(with_names, height=300)
                csv_with_names = with_names.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Télécharger les contacts avec noms",
                    data=csv_with_names,
                    file_name="contacts_avec_noms.csv",
                    mime="text/csv"
                )
            # Bloc pour les numéros sans noms uniquement
            only_missing = result[result["noms"].isna()][["numeros"]]
            with st.expander("💾 Télécharger les numéros sans noms"):
                if missing is not None and not missing.empty:
                    st.dataframe(missing[["numeros"]], height=200)
                    missing_csv = missing[["numeros"]].to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="Télécharger les numéros sans noms",
                        data=missing_csv,
                        file_name="numeros_sans_noms.csv",
                        mime="text/csv"
                    )
                else:
                    st.success("Tous les numéros ont un nom associé !")
    except Exception as e:
        st.error(f"Erreur lors du traitement : {str(e)}")