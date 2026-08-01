# System Universe d100 - Jeu de Rôle Accessible

Bienvenue dans le dépôt officiel de **System Universe d100**, un jeu de rôle post-apocalyptique conçu dès le départ pour être **100% accessible aux personnes aveugles et malvoyantes**.

Ce dépôt centralise l'ensemble de l'écosystème du jeu : les règles, la campagne, les outils numériques et les fictions audio associées.

## 🌍 L'Univers

L'humanité doit s'adapter à un monde transformé par le "Système" - une force mystérieuse qui a réécrit les lois de la réalité, introduisant des concepts de niveaux, de compétences et de magie dans notre monde moderne. Les joueurs incarnent des "Résonants", des humains capables d'influencer le Système lui-même.

## 🎲 Le Système d100

Un système de jeu fluide et unifié :
- **Résolution unique :** Lancez 1d100. Si le résultat est inférieur ou égal à votre (Compétence + Modificateurs), c'est une réussite.
- **Accessibilité :** Aucun calcul complexe en cours de partie, pas de brouettes de dés différents.
- **Outils fournis :** Un lanceur de dés accessible (Python) et une version web sont inclus.

## 📂 Contenu du dépôt

### Documents de Jeu (PDF et TXT accessibles)
- `System_Universe_JDR_Manuel_d100_UTF8.pdf` / `manuel_accessible.txt` : Le livre de base complet.
- `Campagne_System_Universe_d100_Les_Echos_du_Systeme.pdf` : Une campagne épique en 6 actes (niveaux 1 à 10).
- `Scenario_Prise_en_Main_System_Universe.pdf` / `scenario_prise_en_main_accessible.txt` : Une aventure d'initiation de 2-3h.
- Fiches de personnages, Aides de jeu MJ et Fiches de factions.

### Outils Numériques
- **Site Web Vitrine :** Interface HTML/CSS/JS accessible avec lanceur de dés intégré.
- **Lanceur de Dés Python :** `lanceur_des_accessible.py` (Interface 100% clavier avec synthèse vocale).

### Fictions et Dramatiques Audio
- `medievil-audio-drama/` : Scripts et audios d'adaptation de MediEvil.
- `primal-hunter-dramatique-audio/` : Scripts et audios basés sur Primal Hunter.
- `Battle_Zone_L_Evasion_du_Systeme.md` : Roman LitRPG dans l'univers.
- `Zazie_dans_le_Metro_Script_Dramatique.md` : Adaptation en dramatique audio.

## 🚀 Installation des outils

### Lanceur de dés Python
Le lanceur de dés utilise la synthèse vocale pour annoncer les résultats.

1. Assurez-vous d'avoir Python 3.8+ installé.
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancez le script :
   ```bash
   python lanceur_des_accessible.py
   ```

### Site Web
Le site est un site statique (HTML/CSS/JS). Vous pouvez simplement ouvrir le fichier `index.html` dans votre navigateur ou le déployer sur n'importe quel hébergement statique (comme GitHub Pages).

## ♿ Engagement Accessibilité

Ce projet suit une approche *Accessibility-First* :
- Tous les documents PDF sont accompagnés de leur équivalent `.txt` pur pour une compatibilité parfaite avec les lecteurs d'écran (NVDA, JAWS).
- Les interfaces web respectent les standards WCAG (navigation clavier, attributs ARIA, contrastes).
- Les outils logiciels intègrent nativement la synthèse vocale.

## 🤝 Contribution

Les contributions pour améliorer les règles, étendre l'univers ou parfaire l'accessibilité sont les bienvenues. N'hésitez pas à ouvrir une *Issue* ou proposer une *Pull Request*.

---
*Créé par Yohann Poulain (Fuzatifan) - 2025/2026*
