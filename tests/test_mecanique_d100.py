#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour le Lanceur de Dés Accessible - System Universe d100
Exécution : pytest tests/test_mecanique_d100.py -v
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Ajouter le répertoire parent au path pour importer le module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lanceur_des_accessible import MecaniqueD100, Historique


# ============================================================
# Tests : MecaniqueD100.lancer_d100
# ============================================================
class TestLancerD100:
    """Tests pour la fonction de lancer de dé."""

    def test_resultat_dans_plage(self):
        """Le résultat doit toujours être entre 1 et 100."""
        for _ in range(1000):
            resultat = MecaniqueD100.lancer_d100()
            assert 1 <= resultat <= 100, f"Résultat hors plage : {resultat}"

    def test_type_entier(self):
        """Le résultat doit être un entier."""
        resultat = MecaniqueD100.lancer_d100()
        assert isinstance(resultat, int)

    def test_distribution_non_constante(self):
        """Vérification basique que le dé n'est pas biaisé (pas toujours le même résultat)."""
        resultats = {MecaniqueD100.lancer_d100() for _ in range(200)}
        assert len(resultats) > 50, "Le dé semble biaisé (trop peu de valeurs distinctes)"


# ============================================================
# Tests : MecaniqueD100.evaluer_test
# ============================================================
class TestEvaluerTest:
    """Tests pour l'évaluation des tests de compétence."""

    def test_reussite_critique_01(self):
        """Un résultat de 1 est toujours une réussite critique."""
        eval = MecaniqueD100.evaluer_test(1, 50)
        assert eval['reussite'] is True
        assert eval['critique'] is True
        assert 'RÉUSSITE CRITIQUE' in eval['statut']

    def test_reussite_critique_05(self):
        """Un résultat de 5 est toujours une réussite critique."""
        eval = MecaniqueD100.evaluer_test(5, 50)
        assert eval['reussite'] is True
        assert eval['critique'] is True

    def test_echec_critique_96(self):
        """Un résultat de 96 est toujours un échec critique."""
        eval = MecaniqueD100.evaluer_test(96, 100)
        assert eval['reussite'] is False
        assert eval['critique'] is True
        assert 'ÉCHEC CRITIQUE' in eval['statut']

    def test_echec_critique_100(self):
        """Un résultat de 100 est toujours un échec critique."""
        eval = MecaniqueD100.evaluer_test(100, 100)
        assert eval['reussite'] is False
        assert eval['critique'] is True

    def test_reussite_normale(self):
        """Un résultat inférieur ou égal au seuil (hors critique) est une réussite."""
        eval = MecaniqueD100.evaluer_test(40, 50)
        assert eval['reussite'] is True
        assert eval['critique'] is False
        assert 'RÉUSSITE' in eval['statut']

    def test_echec_normal(self):
        """Un résultat supérieur au seuil (hors critique) est un échec."""
        eval = MecaniqueD100.evaluer_test(60, 50)
        assert eval['reussite'] is False
        assert eval['critique'] is False
        assert 'ÉCHEC' in eval['statut']

    def test_reussite_sur_seuil_exact(self):
        """Un résultat égal au seuil est une réussite."""
        eval = MecaniqueD100.evaluer_test(50, 50)
        assert eval['reussite'] is True

    def test_message_contient_resultat_et_seuil(self):
        """Le message doit contenir le résultat et le seuil."""
        eval = MecaniqueD100.evaluer_test(42, 65)
        assert '42' in eval['message']
        assert '65' in eval['message']

    def test_reussite_critique_prime_sur_seuil(self):
        """Un résultat de 3 est critique même si le seuil est très bas (ex: 2)."""
        eval = MecaniqueD100.evaluer_test(3, 2)
        assert eval['reussite'] is True
        assert eval['critique'] is True

    def test_echec_critique_prime_sur_reussite(self):
        """Un résultat de 98 est critique même avec un seuil de 100."""
        eval = MecaniqueD100.evaluer_test(98, 100)
        assert eval['reussite'] is False
        assert eval['critique'] is True


# ============================================================
# Tests : MecaniqueD100.calculer_degats
# ============================================================
class TestCalculerDegats:
    """Tests pour le calcul de dégâts."""

    def test_arme_legere(self):
        """Arme légère : dégâts = résultat // 10."""
        calcul = MecaniqueD100.calculer_degats('1', 75)
        assert calcul is not None
        assert calcul['degats'] == 7
        assert calcul['diviseur'] == 10

    def test_arme_moyenne(self):
        """Arme moyenne : dégâts = résultat // 5."""
        calcul = MecaniqueD100.calculer_degats('2', 50)
        assert calcul is not None
        assert calcul['degats'] == 10
        assert calcul['diviseur'] == 5

    def test_arme_lourde(self):
        """Arme lourde : dégâts = résultat // 3."""
        calcul = MecaniqueD100.calculer_degats('3', 90)
        assert calcul is not None
        assert calcul['degats'] == 30
        assert calcul['diviseur'] == 3

    def test_arme_tres_lourde(self):
        """Arme très lourde : dégâts = résultat // 2."""
        calcul = MecaniqueD100.calculer_degats('4', 80)
        assert calcul is not None
        assert calcul['degats'] == 40
        assert calcul['diviseur'] == 2

    def test_arme_invalide(self):
        """Un type d'arme invalide retourne None."""
        calcul = MecaniqueD100.calculer_degats('9', 50)
        assert calcul is None

    def test_degats_minimum_un(self):
        """Un résultat de 1 avec une arme légère donne 0 dégâts (division entière)."""
        calcul = MecaniqueD100.calculer_degats('1', 1)
        assert calcul is not None
        assert calcul['degats'] == 0

    def test_message_contient_degats(self):
        """Le message doit mentionner les dégâts calculés."""
        calcul = MecaniqueD100.calculer_degats('2', 50)
        assert '10' in calcul['message']


# ============================================================
# Tests : Historique
# ============================================================
class TestHistorique:
    """Tests pour la gestion de l'historique avec persistance JSON."""

    def _creer_historique_temp(self):
        """Crée un historique avec un fichier temporaire pour les tests."""
        hist = Historique.__new__(Historique)
        hist._entrees = []
        # Utiliser un fichier temporaire pour ne pas polluer le vrai historique
        hist.FICHIER_HISTORIQUE = Path(tempfile.mktemp(suffix='.json'))
        return hist

    def test_ajouter_entree(self):
        """L'ajout d'une entrée augmente le compteur."""
        hist = self._creer_historique_temp()
        assert hist.nombre_total() == 0
        hist.ajouter("Test", 42, "Détails")
        assert hist.nombre_total() == 1

    def test_obtenir_derniers(self):
        """obtenir_derniers retourne les N dernières entrées."""
        hist = self._creer_historique_temp()
        for i in range(15):
            hist.ajouter("Lancer", i)
        derniers = hist.obtenir_derniers(5)
        assert len(derniers) == 5
        assert derniers[-1]['resultat'] == 14

    def test_limite_max_entrees(self):
        """L'historique ne dépasse pas MAX_ENTREES entrées."""
        hist = self._creer_historique_temp()
        for i in range(60):
            hist.ajouter("Lancer", i)
        assert hist.nombre_total() == Historique.MAX_ENTREES

    def test_persistance_json(self):
        """L'historique est correctement sauvegardé et rechargé depuis JSON."""
        hist = self._creer_historique_temp()
        hist.ajouter("Test persistance", 77, "Détail test")
        fichier = hist.FICHIER_HISTORIQUE

        # Créer un nouvel objet Historique lisant le même fichier
        hist2 = Historique.__new__(Historique)
        hist2._entrees = []
        hist2.FICHIER_HISTORIQUE = fichier
        hist2._charger()

        assert hist2.nombre_total() == 1
        assert hist2.obtenir_derniers(1)[0]['resultat'] == 77

        # Nettoyage
        if fichier.exists():
            fichier.unlink()

    def test_vider_historique(self):
        """La méthode vider() supprime toutes les entrées."""
        hist = self._creer_historique_temp()
        for i in range(5):
            hist.ajouter("Lancer", i)
        assert hist.nombre_total() == 5
        hist.vider()
        assert hist.nombre_total() == 0

        # Nettoyage
        if hist.FICHIER_HISTORIQUE.exists():
            hist.FICHIER_HISTORIQUE.unlink()
