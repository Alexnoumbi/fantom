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

if st.button("🔍 Effectuer l'appariement"):
    if not source_file or not target_file:
        st.error("Veuillez uploader les deux fichiers CSV")
    else:
        try:
            # Lecture des fichiers
            df_source = pd.read_csv(source_file)
            df_target = pd.read_csv(target_file)
            
            # Vérification des colonnes
            if source_noms_col not in df_source.columns:
                st.error(f"Colonne '{source_noms_col}' introuvable dans le fichier source")
            
            elif source_num_col not in df_source.columns:
                st.error(f"Colonne '{source_num_col}' introuvable dans le fichier source")
            
            elif target_num_col not in df_target.columns:
                st.error(f"Colonne '{target_num_col}' introuvable dans le fichier cible")
            
            else:
                # Fusion des données
                result = df_target.merge(
                    df_source[[source_num_col, source_noms_col]],
                    left_on=target_num_col,
                    right_on=source_num_col,
                    how='left'
                )
                
                # Affichage
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
                st.info(f"**Statistiques :** {matched}/{total} correspondances trouvées ({matched/total:.1%})")
        
        except Exception as e:
            st.error(f"Une erreur est survenue: {str(e)}")