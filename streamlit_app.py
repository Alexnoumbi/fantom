import streamlit as st
import pandas as pd

st.set_page_config(page_title="Appariement CSV", layout="wide")

st.title("🔍 Appariement Noms/Numéros entre fichiers CSV")

with st.expander("ℹ️ Instructions"):
    st.markdown("""
    1. **Fichier Source** : CSV contenant les colonnes `noms` et `numeros` (la référence complète)
    2. **Fichier Cible** : CSV contenant une colonne `numeros` à compléter avec les noms
    3. L'application fusionnera les données et affichera le résultat
    """)

# Upload des fichiers
col1, col2 = st.columns(2)
with col1:
    st.subheader("Fichier Source (noms + numeros)")
    source_file = st.file_uploader("Choisir le fichier source", type=["csv"], key="source")

with col2:
    st.subheader("Fichier Cible (numeros)")
    target_file = st.file_uploader("Choisir le fichier cible", type=["csv"], key="target")

# Paramètres optionnels
with st.sidebar:
    st.header("Options")
    source_noms_col = st.text_input("Nom colonne 'noms' dans source", "noms")
    source_num_col = st.text_input("Nom colonne 'numeros' dans source", "numeros")
    target_num_col = st.text_input("Nom colonne 'numeros' dans cible", "numeros")

def safe_strip_columns(df):
    """Supprime les espaces en début/fin dans les noms de colonnes."""
    df.columns = df.columns.str.strip()
    return df

def check_column(df, col_name, file_label):
    if col_name not in df.columns:
        st.error(f"Colonne '{col_name}' introuvable dans le fichier {file_label}. Colonnes trouvées : {list(df.columns)}")
        return False
    return True

def normalize_column(df, col_name):
    """Supprime les espaces et normalise en str pour la colonne de jointure."""
    if col_name in df.columns:
        df[col_name] = df[col_name].astype(str).str.strip()
    return df

if st.button("🔍 Effectuer l'appariement"):
    if not source_file or not target_file:
        st.error("Veuillez uploader les deux fichiers CSV.")
    else:
        try:
            # Lecture des fichiers
            df_source = pd.read_csv(source_file, dtype=str)
            df_target = pd.read_csv(target_file, dtype=str)

            # Nettoyage des noms de colonnes
            df_source = safe_strip_columns(df_source)
            df_target = safe_strip_columns(df_target)

            # Vérification des colonnes nécessaires
            valid_source_noms = check_column(df_source, source_noms_col, "source")
            valid_source_num = check_column(df_source, source_num_col, "source")
            valid_target_num = check_column(df_target, target_num_col, "cible")

            if valid_source_noms and valid_source_num and valid_target_num:
                # Nettoyage des colonnes de jointure (suppression espaces)
                df_source = normalize_column(df_source, source_num_col)
                df_target = normalize_column(df_target, target_num_col)

                # Fusion
                result = df_target.merge(
                    df_source[[source_num_col, source_noms_col]],
                    left_on=target_num_col,
                    right_on=source_num_col,
                    how='left'
                )

                st.success("Appariement réussi !")

                tab1, tab2 = st.tabs(["📊 Résultat", "📥 Télécharger"])

                with tab1:
                    st.dataframe(result, height=500)

                with tab2:
                    csv = result.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="💾 Télécharger le résultat",
                        data=csv,
                        file_name="resultat_appariement.csv",
                        mime="text/csv"
                    )

                # Statistiques
                matched = result[source_noms_col].notna().sum()
                total = len(result)
                percent = (matched / total * 100) if total != 0 else 0
                st.info(f"**Statistiques :** {matched}/{total} correspondances trouvées ({percent:.1f}%)")
        except pd.errors.ParserError:
            st.error("Erreur de lecture des fichiers CSV. Veuillez vérifier le format (séparateur, encodage, etc.).")
        except Exception as e:
            st.error(f"Une erreur est survenue : {str(e)}")