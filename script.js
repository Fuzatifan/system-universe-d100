/**
 * System Universe d100 - Script principal
 * Améliorations : Séparation des responsabilités, test de compétence,
 * calcul de dégâts, gestion du thème sombre/clair, accessibilité renforcée.
 */

// ============================================================
// MODULE : Utilitaires d'accessibilité
// ============================================================
const Accessibilite = {
    /**
     * Annonce un message aux lecteurs d'écran via une région ARIA live.
     * @param {string} message - Le message à annoncer.
     * @param {string} politesse - 'polite' ou 'assertive'.
     */
    annoncer(message, politesse = 'polite') {
        const region = document.createElement('div');
        region.setAttribute('role', 'status');
        region.setAttribute('aria-live', politesse);
        region.setAttribute('aria-atomic', 'true');
        region.className = 'sr-only';
        region.textContent = message;
        document.body.appendChild(region);
        setTimeout(() => {
            if (document.body.contains(region)) {
                document.body.removeChild(region);
            }
        }, 2000);
    },

    /**
     * Synthèse vocale si disponible dans le navigateur.
     * @param {string} texte - Le texte à lire.
     */
    parler(texte) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(texte);
            utterance.lang = 'fr-FR';
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    }
};

// ============================================================
// MODULE : Gestion du thème (sombre / clair)
// ============================================================
const Theme = {
    CLE_STOCKAGE: 'su-d100-theme',

    init() {
        const themeSauvegarde = localStorage.getItem(this.CLE_STOCKAGE);
        if (themeSauvegarde) {
            document.documentElement.setAttribute('data-theme', themeSauvegarde);
        }
        this._mettreAJourBouton();
    },

    basculer() {
        const themeActuel = document.documentElement.getAttribute('data-theme');
        const nouveauTheme = (themeActuel === 'light') ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', nouveauTheme);
        localStorage.setItem(this.CLE_STOCKAGE, nouveauTheme);
        this._mettreAJourBouton();
        const label = (nouveauTheme === 'light') ? 'Mode clair activé' : 'Mode sombre activé';
        Accessibilite.annoncer(label);
    },

    _mettreAJourBouton() {
        const btn = document.getElementById('themeToggle');
        if (!btn) return;
        const themeActuel = document.documentElement.getAttribute('data-theme');
        const estClair = (themeActuel === 'light');
        btn.textContent = estClair ? '🌙 Mode sombre' : '☀️ Mode clair';
        btn.setAttribute('aria-label', estClair ? 'Passer en mode sombre' : 'Passer en mode clair');
    }
};

// ============================================================
// MODULE : Historique des lancers
// ============================================================
const Historique = {
    MAX_ENTREES: 10,
    _liste: document.getElementById('historyList'),

    ajouter(texte) {
        if (!this._liste) return;
        const maintenant = new Date();
        const heure = maintenant.toLocaleTimeString('fr-FR');
        const item = document.createElement('li');
        item.textContent = `${heure} — ${texte}`;
        this._liste.insertBefore(item, this._liste.firstChild);
        if (this._liste.children.length > this.MAX_ENTREES) {
            this._liste.removeChild(this._liste.lastChild);
        }
    }
};

// ============================================================
// MODULE : Mécanique de jeu d100
// ============================================================
const Mecanique = {
    /**
     * Lance un dé à 100 faces.
     * @returns {number} Un entier entre 1 et 100.
     */
    lancerD100() {
        return Math.floor(Math.random() * 100) + 1;
    },

    /**
     * Évalue le résultat d'un test de compétence.
     * @param {number} resultat - Le résultat du dé.
     * @param {number} seuil - La valeur cible (compétence + modificateur).
     * @returns {{statut: string, classe: string, message: string}}
     */
    evaluerTest(resultat, seuil) {
        if (resultat <= 5) {
            return {
                statut: 'RÉUSSITE CRITIQUE !',
                classe: 'critical-success',
                message: `Dé : ${resultat} / Seuil : ${seuil} — RÉUSSITE CRITIQUE ! (01-05)`
            };
        } else if (resultat >= 96) {
            return {
                statut: 'ÉCHEC CRITIQUE.',
                classe: 'critical-failure',
                message: `Dé : ${resultat} / Seuil : ${seuil} — ÉCHEC CRITIQUE. (96-00)`
            };
        } else if (resultat <= seuil) {
            return {
                statut: 'RÉUSSITE !',
                classe: 'success',
                message: `Dé : ${resultat} / Seuil : ${seuil} — RÉUSSITE !`
            };
        } else {
            return {
                statut: 'ÉCHEC.',
                classe: 'failure',
                message: `Dé : ${resultat} / Seuil : ${seuil} — ÉCHEC.`
            };
        }
    },

    /**
     * Calcule les dégâts selon le type d'arme.
     * @param {string} typeArme - 'legere', 'moyenne', 'lourde', 'tres-lourde'.
     * @returns {{nom: string, resultat: number, degats: number, message: string}}
     */
    calculerDegats(typeArme) {
        const armes = {
            'legere':      { nom: 'Légère',      diviseur: 10 },
            'moyenne':     { nom: 'Moyenne',     diviseur: 5  },
            'lourde':      { nom: 'Lourde',      diviseur: 3  },
            'tres-lourde': { nom: 'Très lourde', diviseur: 2  }
        };
        const arme = armes[typeArme];
        if (!arme) return null;
        const resultat = this.lancerD100();
        const degats = Math.floor(resultat / arme.diviseur);
        return {
            nom: arme.nom,
            resultat,
            degats,
            message: `Arme ${arme.nom.toLowerCase()} : Dé ${resultat} ÷ ${arme.diviseur} = ${degats} dégâts`
        };
    }
};

// ============================================================
// MODULE : Navigation par onglets
// ============================================================
const Navigation = {
    init() {
        const boutons = document.querySelectorAll('.nav-button');
        const onglets = document.querySelectorAll('.tab-content');

        boutons.forEach(bouton => {
            bouton.addEventListener('click', () => {
                const nomOnglet = bouton.getAttribute('data-tab');

                boutons.forEach(b => {
                    b.classList.remove('active');
                    b.setAttribute('aria-selected', 'false');
                });
                onglets.forEach(o => o.classList.remove('active'));

                bouton.classList.add('active');
                bouton.setAttribute('aria-selected', 'true');
                const ongletCible = document.getElementById(nomOnglet);
                if (ongletCible) ongletCible.classList.add('active');

                Accessibilite.annoncer(`Onglet "${bouton.textContent}" activé`);
            });
        });

        // Raccourcis Alt+1..4 pour la navigation
        document.addEventListener('keydown', (e) => {
            if (e.altKey && e.key >= '1' && e.key <= '4') {
                e.preventDefault();
                const index = parseInt(e.key, 10) - 1;
                if (boutons[index]) boutons[index].click();
            }
        });
    }
};

// ============================================================
// MODULE : Lanceur de dés (onglet Lanceur)
// ============================================================
const LanceurDes = {
    init() {
        const btnLancer = document.getElementById('launchDice');
        const divResultat = document.getElementById('diceResult');

        if (!btnLancer || !divResultat) return;

        btnLancer.addEventListener('click', () => {
            const resultat = Mecanique.lancerD100();
            divResultat.textContent = resultat;
            divResultat.style.animation = 'none';
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    divResultat.style.animation = 'pulse 0.5s ease';
                });
            });

            const message = `Dé 100 lancé. Résultat : ${resultat}`;
            Historique.ajouter(`d100 → ${resultat}`);
            Accessibilite.annoncer(message, 'assertive');
            Accessibilite.parler(`Résultat : ${resultat}`);
        });

        // Espace pour lancer le dé quand l'onglet lanceur est actif
        document.addEventListener('keydown', (e) => {
            if (e.key === ' ' && document.getElementById('lanceur')?.classList.contains('active')) {
                const actif = document.activeElement;
                if (actif.tagName !== 'BUTTON' && actif.tagName !== 'A' && actif.tagName !== 'INPUT') {
                    e.preventDefault();
                    btnLancer.click();
                }
            }
        });
    }
};

// ============================================================
// MODULE : Test de compétence (onglet Lanceur)
// ============================================================
const TestCompetence = {
    init() {
        const form = document.getElementById('formTestCompetence');
        const resultatBox = document.getElementById('testCompetenceResult');
        if (!form || !resultatBox) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const competence = parseInt(document.getElementById('inputCompetence').value, 10);
            const modificateur = parseInt(document.getElementById('inputModificateur').value, 10) || 0;

            if (isNaN(competence) || competence < 0 || competence > 100) {
                resultatBox.textContent = 'Veuillez entrer une compétence entre 0 et 100.';
                resultatBox.className = 'test-result-box failure';
                Accessibilite.annoncer('Erreur : compétence invalide.', 'assertive');
                return;
            }

            const seuil = Math.max(0, Math.min(100, competence + modificateur));
            const resultat = Mecanique.lancerD100();
            const evaluation = Mecanique.evaluerTest(resultat, seuil);

            resultatBox.textContent = evaluation.message;
            resultatBox.className = `test-result-box ${evaluation.classe}`;

            Historique.ajouter(`Test (seuil ${seuil}) → ${resultat} — ${evaluation.statut}`);
            Accessibilite.annoncer(evaluation.message, 'assertive');
            Accessibilite.parler(evaluation.message);
        });
    }
};

// ============================================================
// MODULE : Calcul de dégâts (onglet Lanceur)
// ============================================================
const CalculDegats = {
    init() {
        const form = document.getElementById('formDegats');
        const resultatBox = document.getElementById('degatsResult');
        if (!form || !resultatBox) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const typeArme = document.getElementById('selectArme').value;
            const calcul = Mecanique.calculerDegats(typeArme);

            if (!calcul) {
                resultatBox.textContent = 'Veuillez sélectionner un type d\'arme.';
                resultatBox.className = 'test-result-box failure';
                return;
            }

            resultatBox.textContent = calcul.message;
            resultatBox.className = 'test-result-box success';

            Historique.ajouter(`Dégâts ${calcul.nom} → ${calcul.degats} dégâts`);
            Accessibilite.annoncer(calcul.message, 'assertive');
            Accessibilite.parler(calcul.message);
        });
    }
};

// ============================================================
// INITIALISATION PRINCIPALE
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    // Thème
    Theme.init();
    const btnTheme = document.getElementById('themeToggle');
    if (btnTheme) {
        btnTheme.addEventListener('click', () => Theme.basculer());
    }

    // Navigation
    Navigation.init();

    // Lanceur de dés
    LanceurDes.init();

    // Test de compétence
    TestCompetence.init();

    // Calcul de dégâts
    CalculDegats.init();

    // Log des raccourcis pour les développeurs
    console.info('System Universe d100 — Raccourcis clavier :');
    console.info('Alt+1 : Accueil | Alt+2 : Lanceur | Alt+3 : Campagne | Alt+4 : Téléchargements');
    console.info('Espace : Lancer le dé (sur l\'onglet Lanceur)');
});
