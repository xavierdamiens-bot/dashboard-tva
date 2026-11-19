"""Tableau de bord TVA — Meridian Distribution.

Lancement :  streamlit run app.py
La page se met à jour toute seule chaque fois que vous enregistrez ce fichier.

Complétez les TODO dans l'ordre des étapes du brief. Chaque TODO porte un nom
(par exemple « CHIFFRES ») que l'étape du brief vous indique.
ATTENTION : ils ne sont pas dans l'ordre du fichier (les étapes 3 et 6 sont en haut).
Cherchez-les avec Ctrl+F (Cmd+F sur Mac).
Ne passez à l'étape suivante que quand la vérification de l'étape en cours est bonne.
"""

import pandas as pd
import plotly.express as px  # noqa: F401 — servira aux étapes 2 et 4, ne pas supprimer
import streamlit as st

st.set_page_config(page_title="Référentiel TVA", layout="wide")


# Déjà écrit pour vous. @st.cache_data évite de relire le fichier à chaque clic.
@st.cache_data
def charger_donnees():
    df = pd.read_csv(
        "data/resultats_vies.csv", parse_dates=["date_saisie", "date_verification"]
    )
    df["etape_rejet"] = df["etape_rejet"].fillna("envoyé à VIES")
    return df


# Déjà écrit pour vous : sert à l'étape 4.
def taux_invalides(donnees, colonne):
    """Pour chaque valeur de `colonne` (chaque canal, chaque pays...), calcule la part
    de numéros invalides en %. Renvoie un tableau à deux colonnes : `colonne` et "taux d'erreur (%)"."""
    return (
        donnees.groupby(colonne)["statut"]
        .apply(lambda statuts: round((statuts == "invalide").mean() * 100, 1))
        .sort_values()
        .reset_index(name="taux d'erreur (%)")
    )


df = charger_donnees()

# =============================================================================
# ÉTAPE 3 — Les filtres (à faire APRÈS les étapes 1 et 2)
# =============================================================================
st.sidebar.header("Filtres")

# Exemple déjà écrit : le filtre pays. Une liste vide veut dire « tous les pays ».
pays = st.sidebar.multiselect("Pays déclaré", sorted(df["pays_declare"].unique()))

# TODO FILTRE_CANAL (étape 3a) : sur le même modèle, un filtre « Canal de saisie » sur la colonne source_saisie.

# TODO FILTRE_PERIODE (étape 3b) : un filtre « Période de saisie » avec st.sidebar.slider (voir le brief).

# `selection` contient les lignes qui passent les filtres. Toute la suite utilise
# `selection`, jamais `df` : c'est ce qui fait réagir la page aux filtres.
selection = df
if pays:
    selection = selection[selection["pays_declare"].isin(pays)]
# TODO APPLIQUER_FILTRES (étape 3c) : appliquer le filtre canal et le filtre période à `selection`.
#           Toujours `selection = selection[...]`, jamais `selection = df[...]`.

# =============================================================================
# ÉTAPE 6 — Rendre la page lisible par tous (à faire APRÈS l'étape 5)
# =============================================================================
st.title("Qualité du référentiel TVA")
# TODO AIDE (étape 6a) : une phrase d'aide pour la directrice financière (st.write).
# TODO DATE_REGLE (étape 6b) : la date de la dernière vérification VIES et la règle pour les non tranchés (st.info).

# =============================================================================
# ÉTAPE 1 — Les quatre chiffres clés
# =============================================================================
total = len(selection)
valides = (selection["statut"] == "valide").sum()
invalides = (selection["statut"] == "invalide").sum()
non_tranches = (selection["statut"] == "non_tranche").sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Numéros", total)
# TODO CHIFFRES (étape 1) : dans col2, col3 et col4, le nombre de valides, d'invalides et de non tranchés,
#          chacun avec son pourcentage du total.
col2.metric("Valides", valides, f"{valides / total:.1%} du total", delta_color="off")
col3.metric("Invalides", invalides, f"{invalides / total:.1%} du total", delta_color="off")
col4.metric("Non tranchés", non_tranches, f"{non_tranches / total:.1%} du total", delta_color="off")

# =============================================================================
# ÉTAPE 2 — L'entonnoir
# =============================================================================
st.subheader("Combien de numéros ont pu être envoyés à VIES ?")
# TODO ENTONNOIR (étape 2) : compter, étape par étape, les numéros qui restent après le retrait des absents,
#          des doublons, puis des numéros mal formés, et les afficher avec px.funnel.
absents = (selection["etape_rejet"] == "absent").sum()
doublons = (selection["etape_rejet"] == "doublon").sum()
structure = (selection["etape_rejet"] == "structure").sum()
entonnoir = pd.DataFrame({
"étape": ["Référentiel", "Sans les absents", "Sans les doublons", "Envoyés à VIES"],
"numéros": [total,
total - absents,
total - absents - doublons,
total - absents - doublons - structure],
})
fig = px.funnel(entonnoir, x="numéros", y="étape",
title="Du référentiel aux numéros envoyés à VIES")
st.plotly_chart(fig)

# =============================================================================
# ÉTAPE 4 — D'où viennent les erreurs ?
# =============================================================================
st.subheader("D'où viennent les erreurs ?")
# TODO GRAPHIQUES (étape 4) : avec taux_invalides(selection, "source_saisie"), puis "pays_declare",
#          deux graphiques en barres horizontales avec la valeur écrite sur chaque barre,
#          puis une phrase (st.caption) qui explique quel canal sort du lot.

# =============================================================================
# ÉTAPE 5 — Les numéros à traiter
# =============================================================================
st.subheader("Numéros à traiter")
# TODO A_TRAITER (étape 5) : la liste des invalides et des non tranchés, avec une colonne « action »,
#          et un bouton pour la télécharger.

# Déjà écrit : les données brutes, cachées par défaut.
with st.expander("Voir toutes les données"):
    st.dataframe(selection, hide_index=True)
