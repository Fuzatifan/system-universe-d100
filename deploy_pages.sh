#!/bin/bash
# ==============================================================================
# Script de déploiement automatique pour GitHub Pages
# ==============================================================================
# Ce script permet de committer et de pousser les modifications locales vers
# la branche principale (main) pour déclencher le déploiement GitHub Pages.
# Il vérifie l'état du dépôt, demande un message de commit et pousse les changements.
# ==============================================================================

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher des messages
print_step() {
    echo -e "\n${BLUE}==>${NC} ${1}"
}

print_success() {
    echo -e "${GREEN}✓${NC} ${1}"
}

print_error() {
    echo -e "${RED}✗ Erreur :${NC} ${1}"
    exit 1
}

print_warning() {
    echo -e "${YELLOW}! Attention :${NC} ${1}"
}

# 1. Vérification de l'environnement
print_step "Vérification de l'environnement Git..."
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    print_error "Ce répertoire n'est pas un dépôt Git."
fi

BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "master" ]; then
    print_warning "Vous n'êtes pas sur la branche principale (actuelle : $BRANCH)."
    read -p "Voulez-vous continuer quand même ? (o/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Oo]$ ]]; then
        echo "Déploiement annulé."
        exit 0
    fi
fi

# 2. Vérification des modifications
print_step "Vérification des modifications..."
if [ -z "$(git status --porcelain)" ]; then
    print_warning "Aucune modification à committer. Le dépôt est déjà à jour."
    exit 0
fi

git status --short

# 3. Demande du message de commit
print_step "Préparation du commit..."
read -p "Entrez un message pour ce déploiement (ou appuyez sur Entrée pour le message par défaut) : " COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Déploiement du site web : mise à jour $(date +'%Y-%m-%d %H:%M')"
fi

# 4. Exécution
print_step "Ajout des fichiers et création du commit..."
git add -A || print_error "Échec lors de l'ajout des fichiers (git add)."
git commit -m "$COMMIT_MSG" || print_error "Échec lors de la création du commit."

print_step "Envoi vers GitHub (Push)..."
git push origin "$BRANCH" || print_error "Échec lors de l'envoi vers GitHub."

# 5. Conclusion
print_success "Modifications envoyées avec succès !"
echo -e "\nLe déploiement GitHub Pages devrait s'effectuer automatiquement."
echo -e "Il peut s'écouler 1 à 2 minutes avant que les changements ne soient visibles en ligne."

# Tenter de récupérer l'URL GitHub Pages
if command -v gh >/dev/null 2>&1; then
    REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
    URL=$(gh api repos/$REPO/pages --jq '.html_url' 2>/dev/null)
    if [ -n "$URL" ]; then
        echo -e "\n🌐 URL du site : ${GREEN}${URL}${NC}"
    fi
fi

echo ""
exit 0
