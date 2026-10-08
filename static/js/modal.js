/**
 * Système de modales modernes - LIMA Maintenance
 * Remplace alert() et confirm() par de belles modales.
 *
 * Usage :
 *   await Modal.alert('Message');
 *   await Modal.alert('Message', 'success');
 *   const ok = await Modal.confirm('Voulez-vous continuer ?');
 *   const value = await Modal.prompt('Votre nom');
 */

const Modal = {
    /**
     * Crée l'overlay et la box.
     */
    _create(html) {
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop';
        backdrop.innerHTML = html;
        document.body.appendChild(backdrop);

        // Fermer au clic sur le backdrop
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) {
                this._resolveCurrent(null);
            }
        });

        return backdrop;
    },

    _resolveCurrent(value) {
        if (this._currentResolve) {
            this._currentResolve(value);
            this._currentResolve = null;
        }
        if (this._currentBackdrop && this._currentBackdrop.parentNode) {
            this._currentBackdrop.remove();
        }
        this._currentBackdrop = null;
    },

    /**
     * Modal d'alerte simple.
     */
    alert(message, type = 'info', title = null) {
        return new Promise((resolve) => {
            this._currentResolve = resolve;

            const icons = {
                info: { svg: '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>', cls: 'modal-icon-info' },
                success: { svg: '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>', cls: 'modal-icon-success' },
                warning: { svg: '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>', cls: 'modal-icon-warning' },
                danger: { svg: '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>', cls: 'modal-icon-danger' },
            };

            const icon = icons[type] || icons.info;
            const defaultTitles = {
                info: 'Information',
                success: 'Succès',
                warning: 'Attention',
                danger: 'Erreur',
            };

            const html = `
                <div class="modal-box" style="position:relative">
                    <button class="modal-close" onclick="Modal._resolveCurrent(null)">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                    </button>
                    <div class="modal-icon ${icon.cls}">${icon.svg}</div>
                    <h2 class="modal-title">${title || defaultTitles[type]}</h2>
                    <p class="modal-message">${message}</p>
                    <div class="modal-actions">
                        <button class="btn btn-primary" onclick="Modal._resolveCurrent(true)">OK</button>
                    </div>
                </div>
            `;

            this._currentBackdrop = this._create(html);
        });
    },

    /**
     * Modal de confirmation.
     */
    confirm(message, options = {}) {
        return new Promise((resolve) => {
            this._currentResolve = resolve;

            const title = options.title || 'Confirmation';
            const confirmText = options.confirmText || 'Confirmer';
            const cancelText = options.cancelText || 'Annuler';
            const type = options.type || 'warning';

            const icons = {
                info: { svg: '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>', cls: 'modal-icon-info' },
                warning: { svg: '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>', cls: 'modal-icon-warning' },
                danger: { svg: '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>', cls: 'modal-icon-danger' },
            };

            const icon = icons[type] || icons.warning;
            const btnClass = type === 'danger' ? 'btn-danger' : 'btn-primary';

            const html = `
                <div class="modal-box" style="position:relative">
                    <button class="modal-close" onclick="Modal._resolveCurrent(false)">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                    </button>
                    <div class="modal-icon ${icon.cls}">${icon.svg}</div>
                    <h2 class="modal-title">${title}</h2>
                    <p class="modal-message">${message}</p>
                    <div class="modal-actions">
                        <button class="btn btn-secondary" onclick="Modal._resolveCurrent(false)">${cancelText}</button>
                        <button class="btn ${btnClass}" onclick="Modal._resolveCurrent(true)">${confirmText}</button>
                    </div>
                </div>
            `;

            this._currentBackdrop = this._create(html);
        });
    },

    /**
     * Modal de saisie (prompt).
     */
    prompt(message, options = {}) {
        return new Promise((resolve) => {
            this._currentResolve = resolve;

            const title = options.title || 'Saisie';
            const placeholder = options.placeholder || '';
            const defaultValue = options.defaultValue || '';
            const confirmText = options.confirmText || 'Valider';

            const html = `
                <div class="modal-box modal-box-lg" style="position:relative">
                    <button class="modal-close" onclick="Modal._resolveCurrent(null)">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                    </button>
                    <h2 class="modal-title" style="text-align:left">${title}</h2>
                    <p class="modal-message" style="text-align:left">${message}</p>
                    <input type="text" class="input" id="modal-prompt-input" placeholder="${placeholder}" value="${defaultValue}" style="margin-bottom:24px" autofocus>
                    <div class="modal-actions">
                        <button class="btn btn-secondary" onclick="Modal._resolveCurrent(null)">Annuler</button>
                        <button class="btn btn-primary" id="modal-prompt-ok">${confirmText}</button>
                    </div>
                </div>
            `;

            this._currentBackdrop = this._create(html);

            const input = document.getElementById('modal-prompt-input');
            const okBtn = document.getElementById('modal-prompt-ok');

            setTimeout(() => input.focus(), 100);

            const submit = () => this._resolveCurrent(input.value);
            okBtn.onclick = submit;
            input.onkeydown = (e) => {
                if (e.key === 'Enter') submit();
                if (e.key === 'Escape') this._resolveCurrent(null);
            };
        });
    },
};

window.Modal = Modal;
