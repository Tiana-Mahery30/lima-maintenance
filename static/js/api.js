/**
 * API Wrapper - LIMA Maintenance
 * Gère automatiquement le JWT, le refresh et les erreurs.
 */

const API_BASE = window.location.origin;

const API = {
    // ---------- Gestion du token ----------
    getToken() {
        return localStorage.getItem('lima_token');
    },

    setToken(token) {
        localStorage.setItem('lima_token', token);
    },

    clearToken() {
        localStorage.removeItem('lima_token');
        localStorage.removeItem('lima_user');
    },

    getUser() {
        const u = localStorage.getItem('lima_user');
        return u ? JSON.parse(u) : null;
    },

    setUser(user) {
        localStorage.setItem('lima_user', JSON.stringify(user));
    },

    isAuthenticated() {
        return !!this.getToken();
    },

    // ---------- Requête générique ----------
    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const headers = options.headers || {};

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // Si ce n'est pas du FormData, on met du JSON par défaut
        if (!(options.body instanceof FormData) && options.body && typeof options.body === 'object') {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(options.body);
        }

        const config = {
            ...options,
            headers,
        };

        try {
            const response = await fetch(url, config);

            // Token expiré ou invalide
            if (response.status === 401) {
                this.clearToken();
                if (!window.location.pathname.includes('login')) {
                    window.location.href = '/login';
                }
                throw new Error('Session expirée');
            }

            if (!response.ok) {
                let errorMsg = `Erreur ${response.status}`;
                try {
                    const err = await response.json();
                    errorMsg = err.detail || errorMsg;
                } catch (e) { /* ignore */ }
                throw new Error(errorMsg);
            }

            // Si c'est un blob (PDF, CSV)
            const contentType = response.headers.get('content-type');
            if (contentType && (contentType.includes('application/pdf') || contentType.includes('text/csv'))) {
                return await response.blob();
            }

            // Si pas de contenu
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // ---------- Raccourcis ----------
    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    post(endpoint, data) {
        return this.request(endpoint, { method: 'POST', body: data });
    },

    put(endpoint, data) {
        return this.request(endpoint, { method: 'PUT', body: data });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    // ---------- Upload ----------
    async upload(endpoint, formData) {
        return this.request(endpoint, {
            method: 'POST',
            body: formData,
        });
    },

    // ---------- Login ----------
    async login(email, motDePasse) {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', motDePasse);

        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Erreur de connexion');
        }

        const data = await response.json();
        this.setToken(data.access_token);
        this.setUser({
            id: data.utilisateur_id,
            nom: data.nom,
            role: data.role,
        });
        return data;
    },

    logout() {
        this.clearToken();
        window.location.href = '/login';
    },

    // ---------- Téléchargement de fichier ----------
    async download(endpoint, filename) {
        const blob = await this.get(endpoint);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    },
};

window.API = API;
