/**
 * Gestion de session - LIMA Maintenance
 */

const Auth = {
    async check(requiredRole = null) {
        if (!API.isAuthenticated()) {
            window.location.href = '/login';
            return null;
        }

        const user = API.getUser();
        if (!user) {
            API.clearToken();
            window.location.href = '/login';
            return null;
        }

        if (requiredRole && user.role !== requiredRole) {
            if (user.role === 'technicien') {
                window.location.href = '/technicien/dashboard';
            } else {
                window.location.href = '/employe/dashboard';
            }
            return null;
        }

        return user;
    },

    redirectToDashboard() {
        const user = API.getUser();
        if (!user) {
            window.location.href = '/login';
            return;
        }
        if (user.role === 'technicien') {
            window.location.href = '/technicien/dashboard';
        } else {
            window.location.href = '/employe/dashboard';
        }
    },

    afficherUtilisateur() {
        const user = API.getUser();
        if (!user) return;

        document.querySelectorAll('[data-user-nom]').forEach(el => el.textContent = user.nom);
        document.querySelectorAll('[data-user-role]').forEach(el => {
            el.textContent = user.role === 'technicien' ? 'Technicien' : 'Employé';
        });
    },

    async logout() {
        const ok = await Modal.confirm(
            'Voulez-vous vraiment vous déconnecter ?',
            {
                title: 'Déconnexion',
                confirmText: 'Se déconnecter',
                cancelText: 'Rester connecté',
                type: 'warning',
            }
        );
        if (ok) {
            WS.disconnect();
            API.logout();
        }
    },
};

window.Auth = Auth;
