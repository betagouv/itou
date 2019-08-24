"""
Result for a call to `api_insee.siret('12000015300011').get()`.
"""

API_INSEE_SIRET_RESULT_MOCK = {
    "header": {"statut": 200, "message": "ok"},
    "etablissement": {
        "siren": "120000153",
        "nic": "00011",
        "siret": "12000015300011",
        "statutDiffusionEtablissement": "O",
        "dateCreationEtablissement": "1997-06-11",
        "trancheEffectifsEtablissement": "32",
        "anneeEffectifsEtablissement": "2017",
        "activitePrincipaleRegistreMetiersEtablissement": None,
        "dateDernierTraitementEtablissement": "2019-06-24T13:06:52",
        "etablissementSiege": True,
        "nombrePeriodesEtablissement": 3,
        "uniteLegale": {
            "etatAdministratifUniteLegale": "A",
            "statutDiffusionUniteLegale": "O",
            "dateCreationUniteLegale": "1997-06-11",
            "categorieJuridiqueUniteLegale": "7120",
            "denominationUniteLegale": "DELEGATION GENERALE A L'EMPLOI ET A LA FORMATION PROFESSIONNELLE",
            "sigleUniteLegale": "DGEFP",
            "denominationUsuelle1UniteLegale": None,
            "denominationUsuelle2UniteLegale": None,
            "denominationUsuelle3UniteLegale": None,
            "sexeUniteLegale": None,
            "nomUniteLegale": None,
            "nomUsageUniteLegale": None,
            "prenom1UniteLegale": None,
            "prenom2UniteLegale": None,
            "prenom3UniteLegale": None,
            "prenom4UniteLegale": None,
            "prenomUsuelUniteLegale": None,
            "pseudonymeUniteLegale": None,
            "activitePrincipaleUniteLegale": "84.13Z",
            "nomenclatureActivitePrincipaleUniteLegale": "NAFRev2",
            "identifiantAssociationUniteLegale": None,
            "economieSocialeSolidaireUniteLegale": "N",
            "caractereEmployeurUniteLegale": "N",
            "trancheEffectifsUniteLegale": "32",
            "anneeEffectifsUniteLegale": "2017",
            "nicSiegeUniteLegale": "00011",
            "dateDernierTraitementUniteLegale": "2019-06-24T13:06:52",
            "categorieEntreprise": "PME",
            "anneeCategorieEntreprise": "2016",
        },
        "adresseEtablissement": {
            "complementAdresseEtablissement": "10-18",
            "numeroVoieEtablissement": "10",
            "indiceRepetitionEtablissement": None,
            "typeVoieEtablissement": "PL",
            "libelleVoieEtablissement": "5 MARTYRS LYCEE BUFFON",
            "codePostalEtablissement": "75015",
            "libelleCommuneEtablissement": "PARIS 15",
            "libelleCommuneEtrangerEtablissement": None,
            "distributionSpecialeEtablissement": None,
            "codeCommuneEtablissement": "75115",
            "codeCedexEtablissement": None,
            "libelleCedexEtablissement": None,
            "codePaysEtrangerEtablissement": None,
            "libellePaysEtrangerEtablissement": None,
        },
        "adresse2Etablissement": {
            "complementAdresse2Etablissement": None,
            "numeroVoie2Etablissement": None,
            "indiceRepetition2Etablissement": None,
            "typeVoie2Etablissement": None,
            "libelleVoie2Etablissement": None,
            "codePostal2Etablissement": None,
            "libelleCommune2Etablissement": None,
            "libelleCommuneEtranger2Etablissement": None,
            "distributionSpeciale2Etablissement": None,
            "codeCommune2Etablissement": None,
            "codeCedex2Etablissement": None,
            "libelleCedex2Etablissement": None,
            "codePaysEtranger2Etablissement": None,
            "libellePaysEtranger2Etablissement": None,
        },
        "periodesEtablissement": [
            {
                "dateFin": None,
                "dateDebut": "2008-01-01",
                "etatAdministratifEtablissement": "A",
                "changementEtatAdministratifEtablissement": False,
                "enseigne1Etablissement": None,
                "enseigne2Etablissement": None,
                "enseigne3Etablissement": None,
                "changementEnseigneEtablissement": False,
                "denominationUsuelleEtablissement": None,
                "changementDenominationUsuelleEtablissement": False,
                "activitePrincipaleEtablissement": "84.13Z",
                "nomenclatureActivitePrincipaleEtablissement": "NAFRev2",
                "changementActivitePrincipaleEtablissement": True,
                "caractereEmployeurEtablissement": "N",
                "changementCaractereEmployeurEtablissement": False,
            },
            {
                "dateFin": "2007-12-31",
                "dateDebut": "1997-12-25",
                "etatAdministratifEtablissement": "A",
                "changementEtatAdministratifEtablissement": False,
                "enseigne1Etablissement": None,
                "enseigne2Etablissement": None,
                "enseigne3Etablissement": None,
                "changementEnseigneEtablissement": False,
                "denominationUsuelleEtablissement": None,
                "changementDenominationUsuelleEtablissement": False,
                "activitePrincipaleEtablissement": "75.1E",
                "nomenclatureActivitePrincipaleEtablissement": "NAF1993",
                "changementActivitePrincipaleEtablissement": True,
                "caractereEmployeurEtablissement": "N",
                "changementCaractereEmployeurEtablissement": False,
            },
            {
                "dateFin": "1997-12-24",
                "dateDebut": "1997-06-11",
                "etatAdministratifEtablissement": "A",
                "changementEtatAdministratifEtablissement": False,
                "enseigne1Etablissement": None,
                "enseigne2Etablissement": None,
                "enseigne3Etablissement": None,
                "changementEnseigneEtablissement": False,
                "denominationUsuelleEtablissement": None,
                "changementDenominationUsuelleEtablissement": False,
                "activitePrincipaleEtablissement": None,
                "nomenclatureActivitePrincipaleEtablissement": None,
                "changementActivitePrincipaleEtablissement": False,
                "caractereEmployeurEtablissement": "N",
                "changementCaractereEmployeurEtablissement": False,
            },
        ],
    },
}
