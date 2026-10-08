/**
 * WebSocket client + Toasts - LIMA Maintenance
 */

const WS = {
    socket: null,
    reconnectDelay: 3000,
    reconnectAttempts: 0,
    maxReconnectAttempts: 10,

    connect() {
        const token = API.getToken();
        if (!token) return;

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${protocol}//${window.location.host}/notifications/ws?token=${token}`;

        try {
            this.socket = new WebSocket(url);

            this.socket.onopen = () => {
                console.log('WS: Connecté');
                this.reconnectAttempts = 0;
            };

            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (e) {
                    console.error('WS: Message invalide', event.data);
                }
            };

            this.socket.onclose = (event) => {
                if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    setTimeout(() => this.connect(), this.reconnectDelay);
                }
            };

            this.socket.onerror = (error) => {
                console.error('WS: Erreur', error);
            };
        } catch (e) {
            console.error('WS: Impossible de se connecter', e);
        }
    },

    handleMessage(data) {
        switch (data.type) {
            case 'notification':
                Toast.show(data.message, 'info');
                this.updateBadge();
                break;
            case 'nouvelle_intervention':
                Toast.show(data.message, 'warning');
                this.updateBadge();
                if (window.location.pathname.includes('signalements') ||
                    window.location.pathname.includes('dashboard')) {
                    if (typeof chargerInterventions === 'function') {
                        chargerInterventions();
                    }
                }
                break;
            case 'intervention_annulee':
                Toast.show(data.message, 'warning');
                if (window.location.pathname.includes('signalements') ||
                    window.location.pathname.includes('dashboard')) {
                    if (typeof chargerInterventions === 'function') {
                        chargerInterventions();
                    } else if (typeof charger === 'function') {
                        charger();
                    }
                }
                break;
            case 'nouveau_commentaire':
                Toast.show(`${data.auteur} : ${data.contenu}`, 'info');
                if (typeof chargerCommentaires === 'function' && data.intervention_id) {
                    chargerCommentaires(data.intervention_id);
                }
                break;
        }
    },

    async updateBadge() {
        try {
            const res = await API.get('/notifications/non-lues/count');
            const badge = document.getElementById('notif-badge');
            if (badge) {
                if (res.count > 0) {
                    badge.textContent = res.count;
                    badge.style.display = 'flex';
                } else {
                    badge.style.display = 'none';
                }
            }
        } catch (e) { /* silencieux */ }
    },

    disconnect() {
        if (this.socket) {
            this.socket.close(1000, 'Déconnexion volontaire');
        }
    },
};

// ---------- Toasts (notifications discrètes) ----------
const Toast = {
    show(message, type = 'info', duration = 5000) {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icons = {
            info: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
            success: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
            warning: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
            danger: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>',
        };

        toast.innerHTML = `
            <div style="flex-shrink:0">${icons[type] || icons.info}</div>
            <div style="flex:1;font-size:13px;line-height:1.4">${message}</div>
            <button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;color:#94a3b8;padding:0">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },
};

window.WS = WS;
window.Toast = Toast;
