/**
 * Gestion de session + profil - LIMA Maintenance
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

    // ---------- Modal Profil ----------
    async ouvrirModaleProfil() {
        const user = API.getUser();
        let profil = {};

        try {
            profil = await API.get('/profil/me');
        } catch (err) {
            profil = user;
        }

        const initiales = (profil.nom || '?').split(' ').map(p => p[0]).join('').substring(0, 2).toUpperCase();

        const html = `
            <div class="modal-backdrop" id="profil-backdrop">
                <div class="modal-box modal-box-lg" style="position:relative;max-width:480px;text-align:left">
                    <button class="modal-close" onclick="document.getElementById('profil-backdrop').remove()">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                    </button>

                    <h2 class="modal-title" style="margin-bottom:24px;display:flex;align-items:center;gap:10px">
                        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1a237e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                        Mon profil
                    </h2>

                    <div style="display:flex;align-items:center;gap:14px;padding:16px;background:#f8fafc;border-radius:12px;margin-bottom:24px">
                        <div style="width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#1a237e,#3949ab);color:white;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:16px;flex-shrink:0">
                            ${initiales}
                        </div>
                        <div>
                            <p style="font-size:15px;font-weight:600;color:#1e293b;margin:0">${profil.nom || '-'}</p>
                            <p style="font-size:12px;color:#64748b;margin:2px 0 0 0">${profil.email || '-'}</p>
                            <p style="font-size:11px;color:#94a3b8;margin:2px 0 0 0">
                                ${profil.role === 'technicien' ? 'Technicien' : 'Employé'}
                            </p>
                        </div>
                    </div>

                    <h3 style="font-size:13px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.05em;margin:0 0 12px 0">
                        Changer le mot de passe
                    </h3>

                    <div style="margin-bottom:12px">
                        <label class="label">Ancien mot de passe *</label>
                        <input type="password" id="profil-ancien" class="input" autocomplete="current-password">
                    </div>
                    <div style="margin-bottom:12px">
                        <label class="label">Nouveau mot de passe *</label>
                        <input type="password" id="profil-nouveau" class="input" placeholder="Min. 6 caractères" autocomplete="new-password">
                    </div>
                    <div style="margin-bottom:20px">
                        <label class="label">Confirmer le nouveau mot de passe *</label>
                        <input type="password" id="profil-confirm" class="input" autocomplete="new-password">
                    </div>

                    <div style="display:flex;gap:12px;justify-content:flex-end;padding-top:16px;border-top:1px solid #e2e8f0">
                        <button class="btn btn-secondary" onclick="document.getElementById('profil-backdrop').remove()">Annuler</button>
                        <button class="btn btn-primary" onclick="Auth.changerMotDePasse()">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
                            Enregistrer
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Supprimer une éventuelle modale existante
        const existing = document.getElementById('profil-container');
        if (existing) existing.remove();

        const div = document.createElement('div');
        div.id = 'profil-container';
        div.innerHTML = html;
        document.body.appendChild(div);

        document.getElementById('profil-backdrop').addEventListener('click', (e) => {
            if (e.target.id === 'profil-backdrop') div.remove();
        });

        // Focus sur le premier champ
        setTimeout(() => document.getElementById('profil-ancien')?.focus(), 100);
    },

    async changerMotDePasse() {
        const ancien = document.getElementById('profil-ancien').value;
        const nouveau = document.getElementById('profil-nouveau').value;
        const confirm = document.getElementById('profil-confirm').value;

        if (!ancien) return Modal.alert('Ancien mot de passe requis', 'warning');
        if (!nouveau || nouveau.length < 6) return Modal.alert('Le nouveau mot de passe doit faire au moins 6 caractères', 'warning');
        if (nouveau !== confirm) return Modal.alert('Les mots de passe ne correspondent pas', 'warning');
        if (ancien === nouveau) return Modal.alert('Le nouveau mot de passe doit être différent', 'warning');

        const btn = event.target;
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = 'Enregistrement...';

        try {
            await API.put('/profil/changer-mot-de-passe', {
                ancien_mot_de_passe: ancien,
                nouveau_mot_de_passe: nouveau,
            });

            Toast.show('Mot de passe modifié avec succès', 'success');
            document.getElementById('profil-container').remove();
        } catch (err) {
            Modal.alert(err.message, 'danger');
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    },
};

window.Auth = Auth;
