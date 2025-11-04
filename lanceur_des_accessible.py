#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanceur de Dés Accessible - System Universe d100
Version UTF-8 corrigée pour éviter les problèmes d'encodage

Spécialement conçu pour l'accessibilité aux personnes aveugles et malvoyantes
Compatible avec les lecteurs d'écran (NVDA, JAWS, Narrateur Windows)
Interface 100% clavier avec synthèse vocale française
"""

import random
import sys
import os
import time
from datetime import datetime

# Configuration de l'encodage
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration de la synthèse vocale
SYNTHESE_DISPONIBLE = True
engine = None

try:
    import pyttsx3
    engine = pyttsx3.init()
    
    # Configuration de la synthèse vocale
    engine.setProperty('rate', 150)  # Vitesse de parole
    
    # Recherche d'une voix française
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break
    
except ImportError:
    SYNTHESE_DISPONIBLE = False
    print("⚠ pyttsx3 non installé - Mode texte uniquement")
except Exception as e:
    SYNTHESE_DISPONIBLE = False
    print(f"⚠ Erreur synthèse vocale: {e}")

# Historique des lancers
historique = []

def parler(texte):
    """Synthèse vocale si disponible, sinon affichage texte"""
    print(texte)
    if SYNTHESE_DISPONIBLE and engine:
        try:
            engine.say(texte)
            engine.runAndWait()
        except Exception as e:
            print(f"⚠ Erreur synthèse: {e}")

def lancer_d100():
    """Lance un dé à 100 faces"""
    return random.randint(1, 100)

def ajouter_historique(action, resultat, details=""):
    """Ajoute une entrée à l'historique"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    historique.append({
        'heure': timestamp,
        'action': action,
        'resultat': resultat,
        'details': details
    })
    
    # Limite l'historique à 50 entrées
    if len(historique) > 50:
        historique.pop(0)

def lancer_simple():
    """Lance un d100 simple"""
    resultat = lancer_d100()
    message = f"Dé 100: {resultat}"
    parler(message)
    ajouter_historique("Lancer simple", resultat)
    return resultat

def lancer_avec_modificateur():
    """Lance un d100 avec modificateur"""
    try:
        modificateur = int(input("Modificateur (+/-): "))
        resultat = lancer_d100()
        total = resultat + modificateur
        
        if modificateur >= 0:
            message = f"Dé 100: {resultat} plus {modificateur} égale {total}"
        else:
            message = f"Dé 100: {resultat} moins {abs(modificateur)} égale {total}"
        
        parler(message)
        ajouter_historique("Lancer avec modificateur", resultat, f"Mod: {modificateur:+d}, Total: {total}")
        return total
        
    except ValueError:
        parler("Erreur: Veuillez entrer un nombre valide")
        return None

def test_competence():
    """Effectue un test de compétence d100"""
    try:
        print("\n=== TEST DE COMPÉTENCE ===")
        
        # Saisie de la valeur de compétence
        competence = int(input("Valeur de compétence (0-100): "))
        if competence < 0 or competence > 100:
            parler("Erreur: La compétence doit être entre 0 et 100")
            return
        
        # Saisie du modificateur optionnel
        mod_input = input("Modificateur de difficulté (+/-) [Entrée pour 0]: ").strip()
        modificateur = int(mod_input) if mod_input else 0
        
        # Calcul du seuil final
        seuil = competence + modificateur
        
        # Lancer du dé
        resultat = lancer_d100()
        
        # Détermination du résultat
        if resultat <= 5:
            statut = "RÉUSSITE CRITIQUE !"
            message = f"Test: Dé {resultat} contre {seuil}. {statut}"
        elif resultat <= seuil:
            statut = "RÉUSSITE !"
            message = f"Test: Dé {resultat} contre {seuil}. {statut}"
        elif resultat >= 96:
            statut = "ÉCHEC CRITIQUE."
            message = f"Test: Dé {resultat} contre {seuil}. {statut}"
        else:
            statut = "ÉCHEC."
            message = f"Test: Dé {resultat} contre {seuil}. {statut}"
        
        parler(message)
        ajouter_historique("Test de compétence", resultat, f"Seuil: {seuil}, {statut}")
        
    except ValueError:
        parler("Erreur: Veuillez entrer des nombres valides")

def calcul_degats():
    """Calcule les dégâts selon le type d'arme"""
    print("\n=== CALCUL DE DÉGÂTS ===")
    print("Types d'armes:")
    print("1 - Légère (couteau, matraque)")
    print("2 - Moyenne (épée, pistolet)")
    print("3 - Lourde (hache 2 mains, fusil)")
    print("4 - Très lourde (lance-roquettes)")
    
    try:
        choix = input("Type d'arme (1-4): ").strip()
        
        types_armes = {
            '1': ('Légère', 10),
            '2': ('Moyenne', 5),
            '3': ('Lourde', 3),
            '4': ('Très lourde', 2)
        }
        
        if choix not in types_armes:
            parler("Erreur: Choisissez un type d'arme valide (1-4)")
            return
        
        nom_arme, diviseur = types_armes[choix]
        resultat = lancer_d100()
        degats = resultat // diviseur
        
        message = f"Arme {nom_arme.lower()}: Dé {resultat} divisé par {diviseur} égale {degats} dégâts"
        parler(message)
        ajouter_historique("Calcul dégâts", resultat, f"{nom_arme}: {degats} dégâts")
        
    except ValueError:
        parler("Erreur: Veuillez entrer un choix valide")

def afficher_historique():
    """Affiche l'historique des lancers"""
    if not historique:
        parler("Aucun lancer dans l'historique")
        return
    
    print("\n=== HISTORIQUE DES LANCERS ===")
    parler("Historique des lancers")
    
    # Affiche les 10 derniers lancers
    derniers = historique[-10:]
    for i, entree in enumerate(derniers, 1):
        ligne = f"{i}. {entree['heure']} - {entree['action']}: {entree['resultat']}"
        if entree['details']:
            ligne += f" ({entree['details']})"
        print(ligne)
    
    if len(historique) > 10:
        parler(f"Affichage des 10 derniers lancers sur {len(historique)} total")
    else:
        parler(f"{len(historique)} lancers au total")

def afficher_aide():
    """Affiche l'aide et les raccourcis"""
    aide_texte = """
=== AIDE - LANCEUR DE DÉS ACCESSIBLE ===

RACCOURCIS CLAVIER:
• Espace : Lancer d100 rapide
• T : Test de compétence
• D : Calcul de dégâts
• H : Historique des lancers
• A : Afficher cette aide
• Q ou Échap : Quitter

NAVIGATION:
• Utilisez les chiffres pour les menus
• Entrée pour valider
• Échap pour revenir au menu principal

ACCESSIBILITÉ:
• Interface 100% clavier
• Synthèse vocale française
• Compatible lecteurs d'écran
• Messages clairs et détaillés

SYSTEM UNIVERSE d100:
• Tous les tests: 1d100 ≤ Compétence + Modificateurs
• Réussite critique: 01-05
• Échec critique: 96-00
• Modificateurs: -40% (Héroïque) à +30% (Très Facile)
"""
    print(aide_texte)
    parler("Aide affichée. Consultez l'écran pour les détails complets.")

def menu_principal():
    """Affiche le menu principal et gère les choix"""
    while True:
        print("\n" + "=" * 50)
        print("LANCEUR DE DÉS ACCESSIBLE - SYSTEM UNIVERSE d100")
        print("=" * 50)
        print("\nMENU PRINCIPAL:")
        print("1 - Lancer un d100 simple")
        print("2 - Lancer d100 avec modificateur")
        print("3 - Test de compétence")
        print("4 - Calcul de dégâts")
        print("5 - Historique des lancers")
        print("6 - Aide et raccourcis")
        print("0 - Quitter")
        print("\nRaccourcis: [Espace]=d100, [T]=test, [D]=dégâts, [H]=historique, [Q]=quitter")
        
        try:
            choix = input("\nVotre choix: ").strip().lower()
            
            if choix == '1' or choix == ' ':
                lancer_simple()
            elif choix == '2':
                lancer_avec_modificateur()
            elif choix == '3' or choix == 't':
                test_competence()
            elif choix == '4' or choix == 'd':
                calcul_degats()
            elif choix == '5' or choix == 'h':
                afficher_historique()
            elif choix == '6' or choix == 'a':
                afficher_aide()
            elif choix == '0' or choix == 'q' or choix == '\x1b':  # \x1b = Échap
                parler("Au revoir ! Merci d'avoir utilisé le lanceur de dés accessible.")
                break
            else:
                parler("Choix invalide. Utilisez les chiffres 0-6 ou les raccourcis.")
                
        except KeyboardInterrupt:
            print("\n")
            parler("Au revoir ! Merci d'avoir utilisé le lanceur de dés accessible.")
            break
        except Exception as e:
            parler(f"Erreur inattendue: {e}")

def verifier_environnement():
    """Vérifie l'environnement et affiche les informations de démarrage"""
    print("Vérification de l'environnement...")
    
    # Vérification de l'encodage
    print(f"Encodage système: {sys.stdout.encoding}")
    
    # Vérification de la synthèse vocale
    if SYNTHESE_DISPONIBLE:
        print("✓ Synthèse vocale disponible")
    else:
        print("⚠ Synthèse vocale non disponible - Mode texte uniquement")
    
    # Test des caractères français
    test_chars = "àáâäèéêëìíîïòóôöùúûüç"
    print(f"Test caractères français: {test_chars}")
    
    return True

def main():
    """Fonction principale"""
    # Configuration de l'encodage pour Windows
    if os.name == 'nt':  # Windows
        os.system('chcp 65001 > nul 2>&1')  # UTF-8
    
    # Vérification de l'environnement
    if not verifier_environnement():
        return
    
    # Message de bienvenue
    print("\n" + "=" * 60)
    print("LANCEUR DE DÉS ACCESSIBLE")
    print("System Universe d100")
    print("Version UTF-8 - Spécialement conçu pour l'accessibilité")
    print("=" * 60)
    
    message_bienvenue = "Bienvenue dans le lanceur de dés accessible pour System Universe d100"
    parler(message_bienvenue)
    
    # Information sur l'accessibilité
    if SYNTHESE_DISPONIBLE:
        parler("Synthèse vocale française activée")
    else:
        parler("Mode texte activé. Installez pyttsx3 pour la synthèse vocale")
    
    parler("Interface 100% clavier. Appuyez sur 6 pour l'aide complète")
    
    # Lancement du menu principal
    try:
        menu_principal()
    except Exception as e:
        print(f"\nErreur fatale: {e}")
        parler("Erreur fatale. Consultez la console pour plus de détails.")
    finally:
        # Nettoyage
        if engine:
            try:
                engine.stop()
            except:
                pass

if __name__ == "__main__":
    main()
