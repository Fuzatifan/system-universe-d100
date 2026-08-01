#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanceur de Dés Accessible - System Universe d100
Version 2.0 - Architecture orientée objet avec persistance JSON

Spécialement conçu pour l'accessibilité aux personnes aveugles et malvoyantes.
Compatible avec les lecteurs d'écran (NVDA, JAWS, Narrateur Windows).
Interface 100% clavier avec synthèse vocale française.

Installation :
    pip install -r requirements.txt

Utilisation :
    python lanceur_des_accessible.py
"""

import random
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# ============================================================
# Configuration de l'encodage (Windows)
# ============================================================
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


# ============================================================
# Classe : SynthèseVocale
# ============================================================
class SyntheseVocale:
    """Gère la synthèse vocale avec détection gracieuse de l'absence de pyttsx3."""

    def __init__(self):
        self.disponible = False
        self._engine = None
        self._initialiser()

    def _initialiser(self):
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', 150)
            voices = self._engine.getProperty('voices')
            for voice in voices:
                if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                    self._engine.setProperty('voice', voice.id)
                    break
            self.disponible = True
        except ImportError:
            print("⚠ pyttsx3 non installé — Mode texte uniquement")
            print("  Installez-le avec : pip install pyttsx3")
        except Exception as e:
            print(f"⚠ Erreur synthèse vocale : {e}")

    def parler(self, texte: str):
        """Lit le texte à voix haute si la synthèse est disponible."""
        if self.disponible and self._engine:
            try:
                self._engine.say(texte)
                self._engine.runAndWait()
            except Exception as e:
                print(f"⚠ Erreur synthèse : {e}")

    def arreter(self):
        """Arrête proprement le moteur de synthèse vocale."""
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass


# ============================================================
# Classe : Historique
# ============================================================
class Historique:
    """Gère l'historique des lancers avec persistance JSON."""

    MAX_ENTREES = 50
    FICHIER_HISTORIQUE = Path.home() / ".su_d100_historique.json"

    def __init__(self):
        self._entrees: list = []
        self._charger()

    def _charger(self):
        """Charge l'historique depuis le fichier JSON."""
        if self.FICHIER_HISTORIQUE.exists():
            try:
                with open(self.FICHIER_HISTORIQUE, 'r', encoding='utf-8') as f:
                    self._entrees = json.load(f)
                    self._entrees = self._entrees[-self.MAX_ENTREES:]
            except (json.JSONDecodeError, IOError):
                self._entrees = []

    def _sauvegarder(self):
        """Sauvegarde l'historique dans le fichier JSON."""
        try:
            with open(self.FICHIER_HISTORIQUE, 'w', encoding='utf-8') as f:
                json.dump(self._entrees, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"⚠ Impossible de sauvegarder l'historique : {e}")

    def ajouter(self, action: str, resultat: int, details: str = ""):
        """Ajoute une entrée à l'historique et la sauvegarde."""
        entree = {
            'heure': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'action': action,
            'resultat': resultat,
            'details': details
        }
        self._entrees.append(entree)
        if len(self._entrees) > self.MAX_ENTREES:
            self._entrees.pop(0)
        self._sauvegarder()

    def obtenir_derniers(self, n: int = 10) -> list:
        """Retourne les n derniers lancers."""
        return self._entrees[-n:]

    def nombre_total(self) -> int:
        """Retourne le nombre total d'entrées."""
        return len(self._entrees)

    def vider(self):
        """Vide l'historique en mémoire et sur disque."""
        self._entrees = []
        self._sauvegarder()


# ============================================================
# Classe : MecaniqueD100
# ============================================================
class MecaniqueD100:
    """Contient toutes les mécaniques de jeu du système d100."""

    MODIFICATEURS = {
        '-40': ('Héroïque', -40),
        '-20': ('Difficile', -20),
        '-10': ('Légèrement Difficile', -10),
        '0':   ('Normal', 0),
        '+10': ('Facile', +10),
        '+20': ('Assez Facile', +20),
        '+30': ('Très Facile', +30),
    }

    ARMES = {
        '1': ('Légère (couteau, matraque)', 10),
        '2': ('Moyenne (épée, pistolet)', 5),
        '3': ('Lourde (hache 2 mains, fusil)', 3),
        '4': ('Très lourde (lance-roquettes)', 2),
    }

    @staticmethod
    def lancer_d100() -> int:
        """Lance un dé à 100 faces. Retourne un entier entre 1 et 100."""
        return random.randint(1, 100)

    @staticmethod
    def evaluer_test(resultat: int, seuil: int) -> dict:
        """
        Évalue le résultat d'un test de compétence.

        Args:
            resultat: Le résultat du dé (1-100).
            seuil: La valeur cible (compétence + modificateur).

        Returns:
            Un dictionnaire avec 'statut', 'reussite', 'critique', 'message'.
        """
        if resultat <= 5:
            return {
                'statut': 'RÉUSSITE CRITIQUE !',
                'reussite': True,
                'critique': True,
                'message': f"Dé : {resultat} | Seuil : {seuil} → RÉUSSITE CRITIQUE ! (01-05)"
            }
        elif resultat >= 96:
            return {
                'statut': 'ÉCHEC CRITIQUE.',
                'reussite': False,
                'critique': True,
                'message': f"Dé : {resultat} | Seuil : {seuil} → ÉCHEC CRITIQUE. (96-00)"
            }
        elif resultat <= seuil:
            return {
                'statut': 'RÉUSSITE !',
                'reussite': True,
                'critique': False,
                'message': f"Dé : {resultat} | Seuil : {seuil} → RÉUSSITE !"
            }
        else:
            return {
                'statut': 'ÉCHEC.',
                'reussite': False,
                'critique': False,
                'message': f"Dé : {resultat} | Seuil : {seuil} → ÉCHEC."
            }

    @staticmethod
    def calculer_degats(type_arme: str, resultat: int) -> dict:
        """
        Calcule les dégâts selon le type d'arme.

        Args:
            type_arme: Clé du dictionnaire ARMES ('1', '2', '3', '4').
            resultat: Le résultat du dé.

        Returns:
            Un dictionnaire avec 'nom', 'resultat', 'diviseur', 'degats', 'message'.
        """
        armes = MecaniqueD100.ARMES
        if type_arme not in armes:
            return None
        nom, diviseur = armes[type_arme]
        degats = resultat // diviseur
        return {
            'nom': nom,
            'resultat': resultat,
            'diviseur': diviseur,
            'degats': degats,
            'message': f"Arme {nom.split('(')[0].strip().lower()} : Dé {resultat} ÷ {diviseur} = {degats} dégâts"
        }


# ============================================================
# Classe : LanceurDes (Interface utilisateur)
# ============================================================
class LanceurDes:
    """
    Interface utilisateur en ligne de commande pour le lanceur de dés.
    Orchestre les classes SyntheseVocale, Historique et MecaniqueD100.
    """

    def __init__(self):
        self.voix = SyntheseVocale()
        self.historique = Historique()
        self.mecanique = MecaniqueD100()

    def afficher_et_parler(self, texte: str):
        """Affiche le texte et le lit vocalement."""
        print(texte)
        self.voix.parler(texte)

    def lancer_simple(self):
        """Lance un d100 simple."""
        resultat = self.mecanique.lancer_d100()
        message = f"Dé 100 : {resultat}"
        self.afficher_et_parler(message)
        self.historique.ajouter("Lancer simple", resultat)

    def lancer_avec_modificateur(self):
        """Lance un d100 avec un modificateur numérique."""
        try:
            modificateur = int(input("Modificateur (+/-) : "))
            resultat = self.mecanique.lancer_d100()
            total = resultat + modificateur
            signe = "plus" if modificateur >= 0 else "moins"
            message = f"Dé 100 : {resultat} {signe} {abs(modificateur)} = {total}"
            self.afficher_et_parler(message)
            self.historique.ajouter(
                "Lancer avec modificateur", resultat,
                f"Mod: {modificateur:+d}, Total: {total}"
            )
        except ValueError:
            self.afficher_et_parler("Erreur : Veuillez entrer un nombre valide.")

    def test_competence(self):
        """Effectue un test de compétence d100."""
        try:
            print("\n=== TEST DE COMPÉTENCE ===")
            competence = int(input("Valeur de compétence (0-100) : "))
            if not (0 <= competence <= 100):
                self.afficher_et_parler("Erreur : La compétence doit être entre 0 et 100.")
                return

            print("\nModificateurs disponibles :")
            for cle, (nom, val) in self.mecanique.MODIFICATEURS.items():
                print(f"  {cle:>4} : {nom}")
            mod_input = input("Modificateur de difficulté [Entrée pour 0] : ").strip()
            modificateur = int(mod_input) if mod_input else 0

            seuil = max(0, min(100, competence + modificateur))
            resultat = self.mecanique.lancer_d100()
            evaluation = self.mecanique.evaluer_test(resultat, seuil)

            self.afficher_et_parler(evaluation['message'])
            self.historique.ajouter(
                "Test de compétence", resultat,
                f"Seuil: {seuil}, {evaluation['statut']}"
            )
        except ValueError:
            self.afficher_et_parler("Erreur : Veuillez entrer des nombres valides.")

    def calcul_degats(self):
        """Calcule les dégâts selon le type d'arme."""
        print("\n=== CALCUL DE DÉGÂTS ===")
        print("Types d'armes :")
        for cle, (nom, div) in self.mecanique.ARMES.items():
            print(f"  {cle} - {nom} (÷{div})")
        try:
            choix = input("Type d'arme (1-4) : ").strip()
            resultat = self.mecanique.lancer_d100()
            calcul = self.mecanique.calculer_degats(choix, resultat)
            if not calcul:
                self.afficher_et_parler("Erreur : Choisissez un type d'arme valide (1-4).")
                return
            self.afficher_et_parler(calcul['message'])
            self.historique.ajouter(
                "Calcul dégâts", resultat,
                f"{calcul['nom'].split('(')[0].strip()}: {calcul['degats']} dégâts"
            )
        except ValueError:
            self.afficher_et_parler("Erreur : Veuillez entrer un choix valide.")

    def afficher_historique(self):
        """Affiche l'historique des lancers."""
        if self.historique.nombre_total() == 0:
            self.afficher_et_parler("Aucun lancer dans l'historique.")
            return

        print("\n=== HISTORIQUE DES LANCERS ===")
        derniers = self.historique.obtenir_derniers(10)
        for i, entree in enumerate(reversed(derniers), 1):
            ligne = f"{i}. {entree['heure']} — {entree['action']} : {entree['resultat']}"
            if entree.get('details'):
                ligne += f" ({entree['details']})"
            print(ligne)

        total = self.historique.nombre_total()
        message = f"Affichage des {len(derniers)} derniers lancers sur {total} au total."
        self.voix.parler(message)
        print(f"\n(Historique sauvegardé dans : {Historique.FICHIER_HISTORIQUE})")

    def afficher_aide(self):
        """Affiche l'aide et les raccourcis."""
        aide = """
=== AIDE - LANCEUR DE DÉS ACCESSIBLE ===

RACCOURCIS CLAVIER :
  Espace : Lancer d100 rapide
  T      : Test de compétence
  D      : Calcul de dégâts
  H      : Historique des lancers
  A      : Afficher cette aide
  Q / Échap : Quitter

NAVIGATION :
  Utilisez les chiffres pour les menus
  Entrée pour valider
  Échap pour revenir au menu principal

ACCESSIBILITÉ :
  Interface 100% clavier
  Synthèse vocale française (pyttsx3)
  Compatible lecteurs d'écran (NVDA, JAWS, Narrateur)
  Historique persistant entre les sessions (~/.su_d100_historique.json)

SYSTÈME UNIVERSE d100 :
  Tous les tests : 1d100 ≤ Compétence + Modificateurs
  Réussite critique : 01-05
  Échec critique   : 96-00
  Modificateurs    : -40 (Héroïque) à +30 (Très Facile)
"""
        print(aide)
        self.voix.parler("Aide affichée. Consultez l'écran pour les détails complets.")

    def menu_principal(self):
        """Affiche le menu principal et gère les choix."""
        while True:
            print("\n" + "=" * 55)
            print("  LANCEUR DE DÉS ACCESSIBLE — SYSTEM UNIVERSE d100")
            print("=" * 55)
            print("\n  MENU PRINCIPAL :")
            print("  1 — Lancer un d100 simple")
            print("  2 — Lancer d100 avec modificateur")
            print("  3 — Test de compétence")
            print("  4 — Calcul de dégâts")
            print("  5 — Historique des lancers")
            print("  6 — Aide et raccourcis")
            print("  0 — Quitter")
            print("\n  Raccourcis : [Espace]=d100, [T]=test, [D]=dégâts, [H]=historique, [Q]=quitter")

            try:
                choix = input("\n  Votre choix : ").strip().lower()

                if choix in ('1', ' '):
                    self.lancer_simple()
                elif choix == '2':
                    self.lancer_avec_modificateur()
                elif choix in ('3', 't'):
                    self.test_competence()
                elif choix in ('4', 'd'):
                    self.calcul_degats()
                elif choix in ('5', 'h'):
                    self.afficher_historique()
                elif choix in ('6', 'a'):
                    self.afficher_aide()
                elif choix in ('0', 'q', '\x1b'):
                    self.afficher_et_parler("Au revoir ! Merci d'avoir utilisé le lanceur de dés accessible.")
                    break
                else:
                    self.afficher_et_parler("Choix invalide. Utilisez les chiffres 0-6 ou les raccourcis.")

            except KeyboardInterrupt:
                print()
                self.afficher_et_parler("Au revoir ! Merci d'avoir utilisé le lanceur de dés accessible.")
                break
            except Exception as e:
                self.afficher_et_parler(f"Erreur inattendue : {e}")

    def verifier_environnement(self) -> bool:
        """Vérifie l'environnement et affiche les informations de démarrage."""
        print("Vérification de l'environnement...")
        print(f"  Python : {sys.version.split()[0]}")
        print(f"  Encodage : {sys.stdout.encoding}")
        print(f"  Synthèse vocale : {'✓ Disponible' if self.voix.disponible else '⚠ Non disponible (mode texte)'}")
        print(f"  Historique : {self.historique.nombre_total()} lancer(s) sauvegardé(s)")
        return True

    def demarrer(self):
        """Point d'entrée principal de l'application."""
        if os.name == 'nt':
            os.system('chcp 65001 > nul 2>&1')

        self.verifier_environnement()

        print("\n" + "=" * 60)
        print("  LANCEUR DE DÉS ACCESSIBLE")
        print("  System Universe d100 — Version 2.0")
        print("  Interface 100% clavier avec synthèse vocale")
        print("=" * 60)

        bienvenue = "Bienvenue dans le lanceur de dés accessible pour System Universe d100"
        self.afficher_et_parler(bienvenue)

        if self.voix.disponible:
            self.voix.parler("Synthèse vocale française activée.")
        else:
            print("  Mode texte activé. Installez pyttsx3 pour la synthèse vocale.")

        self.voix.parler("Interface 100% clavier. Appuyez sur 6 pour l'aide complète.")

        try:
            self.menu_principal()
        except Exception as e:
            print(f"\nErreur fatale : {e}")
            self.voix.parler("Erreur fatale. Consultez la console pour plus de détails.")
        finally:
            self.voix.arreter()


# ============================================================
# Point d'entrée
# ============================================================
if __name__ == "__main__":
    lanceur = LanceurDes()
    lanceur.demarrer()
