# Le fichier `resultats_vies.csv`

Les résultats de la campagne de vérification VIES du 3 novembre 2026, sur les 10 000 lignes du
référentiel clients (le même référentiel que celui des J1-J2). Une ligne par ligne du référentiel.

| Colonne | Contenu |
|---|---|
| `id` | numéro de la ligne dans le référentiel (1 à 10 000) |
| `raison_sociale` | nom du client |
| `numero_saisi` | le numéro tel qu'il a été saisi |
| `numero_normalise` | le numéro nettoyé (majuscules, sans espaces ni tirets) |
| `pays` | code pays lu au début du numéro, vide s'il ne correspond à aucun des dix pays couverts |
| `pays_declare` | pays saisi dans le CRM (on y trouve aussi des codes faux : `ZZ`, `QQ`, `XX`, et le Royaume-Uni `GB`/`UK`, qui n'est plus dans l'UE) |
| `source_saisie` | canal d'origine du client (voir ci-dessous) |
| `date_saisie` | date d'entrée du client dans le référentiel |
| `etape_rejet` | vide si le numéro a été envoyé à VIES ; sinon `absent`, `doublon` ou `structure` |
| `motif` | explication du rejet, en français |
| `statut` | `valide`, `invalide` ou `non_tranche` |
| `erreur_vies` | pour un non tranché, la raison donnée par VIES (`TIMEOUT`, `MS_UNAVAILABLE`, `MS_MAX_CONCURRENT_REQ`) |
| `date_verification` | date et heure de la réponse VIES, vide si le numéro n'a pas été envoyé |
| `temps_reponse_ms` | temps de réponse de VIES en millisecondes, vide si le numéro n'a pas été envoyé |

## Les canaux de saisie

- `crm` : saisi par un commercial dans le logiciel de suivi des clients ;
- `import_fournisseur` : importé depuis des fichiers envoyés par des fournisseurs ;
- `saisie_manuelle` : tapé à la main au comptoir ;
- `portail_client` : saisi par le client lui-même sur le site web ;
- `reprise_erp` : récupéré de l'ancien logiciel de gestion de l'entreprise (un « ERP ») lors de son remplacement. Ce sont souvent les clients les plus anciens.

## Ce que veulent dire les statuts

- **valide** : VIES a confirmé le numéro.
- **invalide** : VIES a refusé le numéro, ou le numéro a été écarté avant l'envoi parce qu'il était absent ou mal formé.
- **non_tranche** : VIES n'a pas pu répondre (service du pays indisponible, délai dépassé). Ce n'est ni valide ni invalide.
- Un **doublon** reprend le statut de la première ligne qui porte le même numéro.

## Les chiffres que votre application doit retrouver (sans filtre)

| | Numéros | Part |
|---|---:|---:|
| Total | 10 000 | 100 % |
| Valides | 5 149 | 51,5 % |
| Invalides | 4 638 | 46,4 % |
| Non tranchés | 213 | 2,1 % |

Entonnoir : 10 000 numéros → 9 778 après retrait des absents → 9 302 après retrait des doublons
→ **5 802 envoyés à VIES** après retrait des numéros mal formés.
