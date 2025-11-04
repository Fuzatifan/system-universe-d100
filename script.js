// Navigation entre les onglets
document.addEventListener('DOMContentLoaded', function() {
    const navButtons = document.querySelectorAll('.nav-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            
            // Désactiver tous les boutons et onglets
            navButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(tab => tab.classList.remove('active'));
            
            // Activer le bouton et l'onglet sélectionnés
            this.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            
            // Annoncer le changement pour les lecteurs d'écran
            announceForScreenReader(`Onglet ${this.textContent} activé`);
        });
    });
    
    // Lanceur de dés
    const launchButton = document.getElementById('launchDice');
    const resultDiv = document.getElementById('diceResult');
    const historyList = document.getElementById('historyList');
    
    if (launchButton) {
        launchButton.addEventListener('click', function() {
            // Lancer le dé (1-100)
            const result = Math.floor(Math.random() * 100) + 1;
            
            // Afficher le résultat avec animation
            resultDiv.textContent = result;
            resultDiv.style.animation = 'none';
            setTimeout(() => {
                resultDiv.style.animation = 'pulse 0.5s ease';
            }, 10);
            
            // Ajouter à l'historique
            const now = new Date();
            const timeString = now.toLocaleTimeString('fr-FR');
            const historyItem = document.createElement('li');
            historyItem.textContent = `${timeString} - Résultat : ${result}`;
            historyList.insertBefore(historyItem, historyList.firstChild);
            
            // Limiter l'historique à 10 entrées
            if (historyList.children.length > 10) {
                historyList.removeChild(historyList.lastChild);
            }
            
            // Annoncer le résultat pour les lecteurs d'écran
            announceForScreenReader(`Dé 100 lancé. Résultat : ${result}`);
            
            // Synthèse vocale si disponible
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(`Résultat : ${result}`);
                utterance.lang = 'fr-FR';
                utterance.rate = 1.0;
                utterance.pitch = 1.0;
                window.speechSynthesis.speak(utterance);
            }
        });
        
        // Support clavier pour le lanceur de dés
        launchButton.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    }
    
    // Navigation clavier globale
    document.addEventListener('keydown', function(e) {
        // Raccourcis clavier pour la navigation
        if (e.altKey) {
            switch(e.key) {
                case '1':
                    e.preventDefault();
                    document.querySelector('[data-tab="accueil"]').click();
                    break;
                case '2':
                    e.preventDefault();
                    document.querySelector('[data-tab="lanceur"]').click();
                    break;
                case '3':
                    e.preventDefault();
                    document.querySelector('[data-tab="campagne"]').click();
                    break;
                case '4':
                    e.preventDefault();
                    document.querySelector('[data-tab="telechargements"]').click();
                    break;
            }
        }
        
        // Espace pour lancer le dé si on est sur l'onglet lanceur
        if (e.key === ' ' && document.getElementById('lanceur').classList.contains('active')) {
            const activeElement = document.activeElement;
            if (activeElement.tagName !== 'BUTTON' && activeElement.tagName !== 'A') {
                e.preventDefault();
                launchButton.click();
            }
        }
    });
    
    // Fonction pour annoncer aux lecteurs d'écran
    function announceForScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.style.position = 'absolute';
        announcement.style.left = '-10000px';
        announcement.style.width = '1px';
        announcement.style.height = '1px';
        announcement.style.overflow = 'hidden';
        announcement.textContent = message;
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
    
    // Animation de pulsation pour le résultat du dé
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
    `;
    document.head.appendChild(style);
    
    // Annoncer les raccourcis clavier au chargement
    console.log('Raccourcis clavier disponibles :');
    console.log('Alt+1 : Accueil');
    console.log('Alt+2 : Lanceur de Dés');
    console.log('Alt+3 : Campagne');
    console.log('Alt+4 : Téléchargements');
    console.log('Espace : Lancer le dé (sur l\'onglet Lanceur de Dés)');
});

