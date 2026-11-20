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

def taux_non_tranches(donnees, colonne):
    """Pour chaque valeur de `colonne` (chaque canal, chaque pays...), calcule la part
    de numéros non tranché en %. Renvoie un tableau à deux colonnes : `colonne` et "taux non tranche (%)"."""
    return (
        donnees.groupby(colonne)["statut"]
        .apply(lambda statuts: round((statuts == "non_tranche").mean() * 100, 1))
        .sort_values()
        .reset_index(name="taux non tranché (%)")
    )

df = charger_donnees()

# =============================================================================
# ÉTAPE 3 — Les filtres (à faire APRÈS les étapes 1 et 2)
# =============================================================================
st.sidebar.header("***Filtres***")

# Exemple déjà écrit : le filtre pays. Une liste vide veut dire « tous les pays ».
pays = st.sidebar.multiselect("*Pays déclaré*", sorted(df["pays_declare"].unique()))

# TODO FILTRE_CANAL (étape 3a) : sur le même modèle, un filtre « Canal de saisie » sur la colonne source_saisie.
canal = st.sidebar.multiselect("*Canal de saisie*", sorted(df["source_saisie"].unique()))

# TODO FILTRE_PERIODE (étape 3b) : un filtre « Période de saisie » avec st.sidebar.slider (voir le brief).
debut, fin = st.sidebar.slider(
"*Période de saisie*",
min_value=df["date_saisie"].min().date(),
max_value=df["date_saisie"].max().date(),
value=(df["date_saisie"].min().date(), df["date_saisie"].max().date()),
format="DD/MM/YYYY",
)

# `selection` contient les lignes qui passent les filtres. Toute la suite utilise
# `selection`, jamais `df` : c'est ce qui fait réagir la page aux filtres.
selection = df
if pays:
    selection = selection[selection["pays_declare"].isin(pays)]
# TODO APPLIQUER_FILTRES (étape 3c) : appliquer le filtre canal et le filtre période à `selection`.
#           Toujours `selection = selection[...]`, jamais `selection = df[...]`.
if canal:
    selection = selection[selection["source_saisie"].isin(canal)]
selection = selection[selection["date_saisie"].dt.date.between(debut, fin)]

# =============================================================================
# ÉTAPE 6 — Rendre la page lisible par tous (à faire APRÈS l'étape 5)
# =============================================================================
st.title("Qualité du référentiel TVA")
# TODO AIDE (étape 6a) : une phrase d'aide pour la directrice financière (st.write).
with st.expander("**🛟 Aide**"):
    st.write("Ce site permet de ressortir les codes TVA dont il faut surveiller la *validité* ou réclamer une *mise à jour*. (L'action à entreprendre est spécifiée dans l'onglet **`Numéros à traiter`** en colonne `Action`)")
    st.write("Les ***`Filtres`*** (à gauche) permettent de trier les résultats en fonction des pays et des canaux de saisie des codes TVA")

# TODO DATE_REGLE (étape 6b) : la date de la dernière vérification VIES et la règle pour les non tranchés (st.info).
derniere = df["date_verification"].max()
#st.info(f"Dernière vérification VIES : {derniere:%d/%m/%Y à %H:%M}. Règle : ...")

st.markdown(
    f"""
    <div style="background-color: rgba(28, 131, 225, 0.1); border-left: 4px solid #1c83e1; padding: 16px; border-radius: 6px; color: #1c83e1;">
        <strong>Dernière vérification VIES : {derniere:%d/%m/%Y à %H:%M}</strong>
        <details style="margin-top: 10px; cursor: pointer;">
            <summary><strong>ℹ️ Règle :</strong></summary>
            <div style="margin-top: 8px; cursor: default;">
                \n- **valide** : VIES a confirmé le numéro.
                \n- **invalide** : VIES a refusé le numéro, ou le numéro a été écarté avant l'envoi parce qu'il était absent ou mal formé.
                \n- **non_tranche** : VIES n'a pas pu répondre (service du pays indisponible, délai dépassé). Ce n'est ni valide ni invalide.
                \n- Un **doublon** reprend le statut de la première ligne qui porte le même numéro.
            </div>
        </details>
    </div>
    """,
    unsafe_allow_html=True,
)


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
col2.metric("Valides", valides, f"{valides / total:.1%} du total", delta_color="normal")
col3.metric("Invalides", invalides, f"{invalides / total:.1%} du total", delta_color="inverse")
col4.metric("Non tranchés", non_tranches, f"{non_tranches / total:.1%} du total", delta_color="off")


# =============================================================================
# BONUS 3 — Présentation en onglets
# =============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(["**Entonnoir**", \
                                        "**Provenance des erreurs**", \
                                        "**Temps de réponse VIES**", \
                                        "**Non tranchés**", \
                                        "**Numéros à traiter**"])

# =============================================================================
# ÉTAPE 2 — L'entonnoir
# =============================================================================
with tab1:
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
with tab2:
    st.subheader("D'où viennent les erreurs ?")
# TODO GRAPHIQUES (étape 4) : avec taux_invalides(selection, "source_saisie"), puis "pays_declare",
#          deux graphiques en barres horizontales avec la valeur écrite sur chaque barre,
#          puis une phrase (st.caption) qui explique quel canal sort du lot.
    taux_canal = taux_invalides(selection, "source_saisie")
    taux_pays = taux_invalides(selection, "pays_declare")
    #st.dataframe(taux)
    fig1 = px.bar(taux_canal, x="taux d'erreur (%)", y="source_saisie", orientation="h",
    text="taux d'erreur (%)", title="Part de numéros invalides par canal de saisie",
    color_discrete_sequence=["#f09090"])

    fig2 = px.bar(taux_pays, x="taux d'erreur (%)", y="pays_declare", orientation="h",
    text="taux d'erreur (%)", title="Part de numéros invalides par pays déclaré",
    color_discrete_sequence=["#f09090"])

    st.plotly_chart(fig1)
    if not canal or "reprise_erp" in canal:
        #selection = selection[selection["source_saisie"].isin(canal)]
        st.caption("**NB :** Données **`reprise_erp`** récupéré de l'ancien logiciel de gestion de l'entreprise lors de son remplacement.")
        st.caption("-> Des erreurs ont pu se se glisser dans les données lors du transfert.")
        st.caption("-> De plus la gestion des erreurs était potentiellement différente sur l'ancien ERP.")
    st.plotly_chart(fig2)

# =============================================================================
# BONUS 1 — Temps de réponse VIES
# =============================================================================
with tab3:
# Un graphique des temps de réponse VIES (temps_reponse_ms) avec la médiane.
    st.subheader("Temps de réponse VIES")

    fig = px.box(
    selection, x="pays_declare", y="temps_reponse_ms", title="Distribution et Médiane du temps de réponse VIES",
    color_discrete_sequence=["#f0dd90"]
    )

    st.plotly_chart(fig)

# =============================================================================
# BONUS 2 — Non tranchés par pays
# =============================================================================
with tab4:
# Un graphique du nombre de non tranchés par pays : un pays ressort-il ?
    st.subheader("Répartition des cas non tranchés")

    taux_ntr_canal = taux_non_tranches(selection, "source_saisie")
    taux_ntr_pays = taux_non_tranches(selection, "pays_declare")

    fig3 = px.bar(taux_ntr_canal, x="taux non tranché (%)", y="source_saisie", orientation="h",
    text="taux non tranché (%)", title="Part de numéros non tranche par pays déclaré",
    color_discrete_sequence=["#717171"])
   
    fig4 = px.bar(taux_ntr_pays, x="taux non tranché (%)", y="pays_declare", orientation="h",
    text="taux non tranché (%)", title="Part de numéros non tranche par pays déclaré",
    color_discrete_sequence=["#717171"])
   
    st.plotly_chart(fig3)
    st.plotly_chart(fig4)

# =============================================================================
# ÉTAPE 5 — Les numéros à traiter
# =============================================================================
with tab5:
    st.subheader("Numéros à traiter")
# TODO A_TRAITER (étape 5) : la liste des invalides et des non tranchés, avec une colonne « action »,
#          et un bouton pour la télécharger.
    # 1. Garder les lignes dont le statut n'est pas "valide" (!= veut dire « différent de »)
    a_traiter = selection[selection["statut"] != "valide"].copy()

    # 2. Ajouter une colonne "action" : .map remplace chaque statut par le texte associé
    a_traiter["action"] = a_traiter["statut"].map({
    "invalide": "Demander un nouveau numéro au client",
    "non_tranche": "Revérifier sur VIES avant la prochaine facture",
    })

    # 3. Afficher le nombre et le tableau, avec les colonnes utiles pour la comptabilité
    colonnes = ["raison_sociale", "numero_saisi", "pays_declare", "statut", "motif", "action"]
    st.write(f"{len(a_traiter)} numéros demandent une action.")
    st.dataframe(a_traiter[colonnes], hide_index=True)

    # Préparation du nom du fichier selon le filtre
    nom_fic = "numeros_a_traiter"
    if pays:
        nom_fic += f"_{"_".join(pays)}"
    if canal:
        nom_fic += f"_{"_".join(canal)}"
    nom_fic += f"_{debut}_{fin}.csv"

    # 4. Le bouton de téléchargement
    st.download_button(
    "Télécharger la liste",
    a_traiter[colonnes].to_csv(index=False, sep=";").encode("utf-8-sig"),
    file_name=nom_fic,
    )

    # Déjà écrit : les données brutes, cachées par défaut.
    with st.expander("Voir toutes les données"):
        st.dataframe(selection, hide_index=True)
