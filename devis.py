<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ASSAWIN</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<style>
:root {
    --bg-dark-main: #030712;
    --bg-card-glass: rgba(255,255,255,0.05);
    --border-glass: rgba(255,255,255,0.1);
    --gold-primary: #f59e0b;
    --gold-secondary: #d97706;
    --gold-light: #fbbf24;
    --text-primary: #f9fafb;
    --text-muted: #9ca3af;
    --accent-emerald: #10b981;
    --accent-red: #ef4444;
    --accent-orange: #f97316;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
    background: var(--bg-dark-main);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
}
.bg-watermark {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 140vw;
    max-width: 900px;
    opacity: 0.035;
    z-index: 0;
    pointer-events: none;
}
.page-content {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
}
.container { max-width: 800px; margin: 0 auto; width: 100%; }
.header { text-align: center; margin-bottom: 2rem; display: flex; flex-direction: column; align-items: center; }
.logo-mark { width: 64px; height: 64px; margin-bottom: 0.75rem; }
.header p { color: var(--text-muted); font-size: 1rem; margin: 0; }
.auth-card, .form-card {
    background: var(--bg-card-glass);
    border: 1px solid var(--border-glass);
    border-radius: 1rem;
    padding: 2rem;
    max-width: 400px;
    margin: 0 auto 1rem;
    backdrop-filter: blur(8px);
}
.form-card { max-width: 600px; margin-bottom: 1.5rem; }
.auth-card input, .form-card input, .form-card select {
    width: 100%;
    padding: 0.75rem;
    margin-bottom: 1rem;
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border-glass);
    border-radius: 0.5rem;
    color: var(--text-primary);
    font-size: 1rem;
}
.form-card label {
    font-size: 0.85rem;
    color: var(--text-muted);
    display: block;
    margin-bottom: 0.3rem;
}
.switch-link {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.9rem;
    max-width: 400px;
    margin: 0 auto 2rem;
}
.switch-link a { color: var(--gold-primary); cursor: pointer; text-decoration: underline; }
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}
.glass-card {
    background: var(--bg-card-glass);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border-glass);
    border-radius: 1rem;
    padding: 1.5rem;
}
.kpi-card { text-align: center; }
.kpi-card h3 {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.kpi-card .value { color: var(--gold-primary); font-size: 2rem; font-weight: bold; }
.section-title { color: var(--gold-primary); font-size: 1.2rem; margin-bottom: 1rem; margin-top: 2rem; max-width: 600px; width: 100%; }
.btn-gold {
    background: linear-gradient(135deg, var(--gold-secondary) 0%, var(--gold-primary) 50%, var(--gold-light) 100%);
    color: var(--bg-dark-main);
    border: none;
    border-radius: 0.5rem;
    padding: 0.85rem;
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
    width: 100%;
}
.btn-gold:active { transform: scale(0.98); }
.btn-secondary {
    background: transparent;
    color: var(--gold-primary);
    border: 1px solid var(--gold-primary);
    border-radius: 0.5rem;
    padding: 0.6rem;
    font-size: 0.9rem;
    cursor: pointer;
    width: 100%;
    margin-top: 0.5rem;
}
.btn-small {
    background: rgba(245,158,11,0.1);
    color: var(--gold-primary);
    border: 1px dashed var(--gold-primary);
    border-radius: 0.5rem;
    padding: 0.5rem;
    font-size: 0.85rem;
    cursor: pointer;
    width: 100%;
    margin-top: 0.5rem;
}
.btn-remove {
    background: transparent;
    color: var(--accent-red);
    border: none;
    cursor: pointer;
    font-size: 0.8rem;
    padding: 0.3rem 0;
}
.btn-pdf {
    background: var(--accent-emerald);
    color: #052e19;
    border: none;
    border-radius: 0.5rem;
    padding: 0.75rem;
    font-size: 0.95rem;
    font-weight: bold;
    cursor: pointer;
    width: 100%;
    margin-top: 0.75rem;
    display: none;
}
.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
#status, #auth-status, #proj-status, #devis-status { text-align: center; color: var(--text-muted); min-height: 1.5rem; margin-top: 0.5rem; }
#app, #register-section, #project-form, #devis-form { display: none; }
.ligne-block {
    border: 1px solid var(--border-glass);
    border-radius: 0.65rem;
    padding: 1rem;
    margin-bottom: 0.85rem;
    background: rgba(255,255,255,0.02);
}
.ligne-top-row { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 0.5rem; margin-bottom: 0.5rem; }
.ligne-top-row input { margin-bottom: 0; }
.mode-toggle { display: flex; gap: 0.4rem; margin: 0.6rem 0 0.75rem; }
.mode-btn {
    flex: 1;
    padding: 0.4rem;
    font-size: 0.78rem;
    border-radius: 0.4rem;
    border: 1px solid var(--border-glass);
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
}
.mode-btn.active {
    background: var(--gold-primary);
    color: var(--bg-dark-main);
    border-color: var(--gold-primary);
    font-weight: bold;
}
.slider-row { margin: 0.6rem 0; }
.slider-row label { display: flex; justify-content: space-between; }
.slider-row .marge-val { color: var(--gold-primary); font-weight: bold; }
.slider-row input[type=range] { width: 100%; accent-color: var(--gold-primary); margin: 0.4rem 0 0; }
.result-line { display: flex; justify-content: space-between; font-size: 0.85rem; padding: 0.25rem 0; color: var(--text-muted); }
.result-line.total { color: var(--gold-primary); font-weight: bold; font-size: 1rem; border-top: 1px solid var(--border-glass); margin-top: 0.4rem; padding-top: 0.5rem; }
.project-select { margin-bottom: 1rem; }

/* Liste des devis */
.devis-list { max-width: 600px; width: 100%; margin: 0 auto; }
.devis-card {
    background: var(--bg-card-glass);
    border: 1px solid var(--border-glass);
    border-radius: 0.75rem;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
}
.devis-header { display: flex; justify-content: space-between; align-items: baseline; }
.devis-titre { font-weight: bold; color: var(--text-primary); }
.devis-montant { color: var(--gold-primary); font-weight: bold; }
.devis-sous-titre { color: var(--text-muted); font-size: 0.85rem; margin-top: 0.2rem; }
.devis-statut-container { margin: 0.6rem 0; }
.badge-vert, .badge-orange {
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: bold;
}
.badge-vert { background: rgba(16,185,129,0.15); color: var(--accent-emerald); border: 1px solid var(--accent-emerald); }
.badge-orange { background: rgba(249,115,22,0.15); color: var(--accent-orange); border: 1px solid var(--accent-orange); }
.devis-actions { display: flex; gap: 0.5rem; margin-top: 0.6rem; }
.devis-actions button {
    flex: 1;
    padding: 0.5rem;
    font-size: 0.78rem;
    border-radius: 0.4rem;
    border: 1px solid var(--border-glass);
    background: transparent;
    color: var(--text-primary);
    cursor: pointer;
}
.btn-modifier { border-color: var(--gold-primary) !important; color: var(--gold-primary) !important; }
.btn-telecharger { border-color: var(--accent-emerald) !important; color: var(--accent-emerald) !important; }
.btn-supprimer { border-color: var(--accent-red) !important; color: var(--accent-red) !important; }
#devis-list-status { text-align: center; color: var(--text-muted); font-size: 0.85rem; margin: 0.5rem 0; }
</style>
</head>
<body>

<svg class="bg-watermark" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="100" cy="100" r="94" fill="none" stroke="#f59e0b" stroke-width="2"/>
  <path d="M100 40 L150 150 L128 150 L100 88 L72 150 L50 150 Z" fill="#f59e0b"/>
  <rect x="78" y="118" width="44" height="10" fill="#030712"/>
</svg>

<div class="page-content">
<div class="container">
    <div class="header">
        <svg class="logo-mark" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
          <circle cx="100" cy="100" r="94" fill="none" stroke="#f59e0b" stroke-width="6"/>
          <path d="M100 40 L150 150 L128 150 L100 88 L72 150 L50 150 Z" fill="#f59e0b"/>
          <rect x="78" y="118" width="44" height="10" fill="#030712"/>
        </svg>
        <p>Vue consolidée de votre activité</p>
    </div>

    <div class="auth-card" id="login-section">
        <input type="email" id="login-email" placeholder="Email" />
        <input type="password" id="login-password" placeholder="Mot de passe" />
        <button class="btn-gold" onclick="login()">Se connecter</button>
        <div id="status"></div>
    </div>
    <div class="switch-link" id="to-register">
        Pas encore de compte ? <a onclick="showRegister()">Créer un compte</a>
    </div>

    <div class="auth-card" id="register-section">
        <input type="text" id="reg-nom" placeholder="Nom complet" />
        <input type="email" id="reg-email" placeholder="Email" />
        <input type="password" id="reg-password" placeholder="Mot de passe" />
        <input type="text" id="reg-entreprise" placeholder="Entreprise (optionnel)" />
        <button class="btn-gold" onclick="register()">Créer mon compte</button>
        <div id="auth-status"></div>
    </div>
    <div class="switch-link" id="to-login" style="display:none">
        Déjà un compte ? <a onclick="showLogin()">Se connecter</a>
    </div>

    <div id="app">
        <div class="kpi-grid">
            <div class="glass-card kpi-card"><h3>CA total</h3><div class="value" id="ca">—</div></div>
            <div class="glass-card kpi-card"><h3>Marge brute</h3><div class="value" id="marge">—</div></div>
            <div class="glass-card kpi-card"><h3>Taux de marque</h3><div class="value" id="taux">—</div></div>
            <div class="glass-card kpi-card"><h3>Projets</h3><div class="value" id="projets">—</div></div>
        </div>
        <div class="section-title">Détail</div>
        <div class="glass-card" id="details"><p style="color:var(--text-muted)">Chargement...</p></div>
        <button class="btn-gold" onclick="loadDashboard()" style="margin-top:1.5rem">Actualiser</button>

        <div class="section-title">Actions</div>
        <button class="btn-gold" onclick="toggleProjectForm()">+ Nouveau projet</button>
        <button class="btn-secondary" onclick="toggleDevisForm()">+ Nouveau devis</button>

        <div class="form-card" id="project-form">
            <label>Nom du projet</label>
            <input type="text" id="proj-nom" placeholder="Ex: Rénovation Saint-Ouen" />
            <div class="row2">
                <div>
                    <label>Budget initial HT (€)</label>
                    <input type="number" id="proj-budget" value="0" />
                </div>
                <div>
                    <label>Marge cible (%)</label>
                    <input type="number" id="proj-marge" value="30" />
                </div>
            </div>
            <label>Description</label>
            <input type="text" id="proj-description" placeholder="Optionnel" />
            <button class="btn-gold" onclick="createProject()">Créer le projet</button>
            <div id="proj-status"></div>
        </div>

        <div class="form-card" id="devis-form">
            <label>Projet (client)</label>
            <select id="devis-projet" class="project-select"></select>
            <label>Titre du devis</label>
            <input type="text" id="devis-titre" placeholder="Ex: Rénovation complète" />
            <div class="row2">
                <div>
                    <label>Acompte (%)</label>
                    <input type="number" id="devis-acompte" value="30" />
                </div>
                <div>
                    <label>Marge cible globale (%)</label>
                    <input type="number" id="devis-marge" value="30" />
                </div>
            </div>

            <label style="margin-top:0.5rem">Interventions / lignes du devis</label>
            <div id="lignes-container"></div>
            <button class="btn-small" type="button" onclick="addLigne()">+ Ajouter une intervention</button>

            <button class="btn-gold" id="btn-submit-devis" onclick="createDevis()" style="margin-top:1rem">Créer le devis</button>
            <button class="btn-secondary" id="btn-cancel-edit" onclick="cancelEdit()" style="display:none">Annuler la modification</button>
            <button class="btn-pdf" id="btn-pdf" onclick="generatePDF()">Télécharger le PDF du devis</button>
            <div id="devis-status"></div>
        </div>

        <div class="section-title">Mes devis</div>
        <button class="btn-secondary" onclick="loadDevisList()" style="max-width:600px">Actualiser la liste</button>
        <div id="devis-list-status"></div>
        <div class="devis-list" id="devis-list"></div>
    </div>
</div>
</div>

<script>
const API_URL = "https://assawin-backend.onrender.com";
let token = null;
let cachedProjects = [];
let ligneCounter = 0;
let lastDevis = null;
let editingDevisId = null;

function showRegister() {
    document.getElementById('login-section').style.display = "none";
    document.getElementById('to-register').style.display = "none";
    document.getElementById('register-section').style.display = "block";
    document.getElementById('to-login').style.display = "block";
}

function showLogin() {
    document.getElementById('register-section').style.display = "none";
    document.getElementById('to-login').style.display = "none";
    document.getElementById('login-section').style.display = "block";
    document.getElementById('to-register').style.display = "block";
}

function toggleProjectForm() {
    const el = document.getElementById('project-form');
    el.style.display = el.style.display === "block" ? "none" : "block";
}

async function toggleDevisForm() {
    const el = document.getElementById('devis-form');
    const willShow = el.style.display !== "block";
    el.style.display = willShow ? "block" : "none";
    if (willShow) {
        await refreshProjectSelect();
        if (document.getElementById('lignes-container').children.length === 0) addLigne();
    }
}

function addLigne() {
    ligneCounter++;
    const id = ligneCounter;
    const container = document.getElementById('lignes-container');
    const block = document.createElement('div');
    block.className = 'ligne-block';
    block.id = 'ligne-' + id;
    block.dataset.mode = 'inverse';
    block.innerHTML = `
        <div class="ligne-top-row">
            <input type="text" placeholder="Désignation" data-field="designation" />
            <input type="text" placeholder="Unité" value="u" data-field="unite" />
            <input type="number" placeholder="Qté" value="1" data-field="quantite" oninput="recalc(${id})" />
        </div>

        <div class="mode-toggle">
            <button type="button" class="mode-btn active" data-mode="inverse" onclick="setMode(${id}, 'inverse')">Chiffrage inversé</button>
            <button type="button" class="mode-btn" data-mode="direct" onclick="setMode(${id}, 'direct')">Prix direct</button>
        </div>

        <div data-panel="inverse">
            <label>Déboursé sec unitaire (€) — ce que ça te coûte réellement</label>
            <input type="number" value="0" data-field="debourse_sec_unitaire" oninput="recalc(${id})" />
            <div class="slider-row">
                <label>Marge cible <span class="marge-val" data-out="marge-label">30%</span></label>
                <input type="range" min="0" max="80" value="30" data-field="marge_slider" oninput="recalc(${id})" />
            </div>
        </div>

        <div data-panel="direct" style="display:none">
            <label>Prix unitaire HT (€) — ce que le client paie</label>
            <input type="number" value="0" data-field="prix_manuel" oninput="recalc(${id})" />
            <label>Déboursé sec unitaire (€)</label>
            <input type="number" value="0" data-field="debourse_sec_unitaire_direct" oninput="recalc(${id})" />
        </div>

        <label style="margin-top:0.5rem">TVA (%)</label>
        <input type="number" value="20" data-field="taux_tva" oninput="recalc(${id})" />

        <div class="result-line"><span>Prix unitaire HT calculé</span><span data-out="prix-unitaire">0,00 €</span></div>
        <div class="result-line"><span>Marge unitaire</span><span data-out="marge-unitaire">0,00 €</span></div>
        <div class="result-line total"><span>Total ligne HT</span><span data-out="total-ligne">0,00 €</span></div>

        <button type="button" class="btn-remove" onclick="removeLigne(${id})">Retirer cette intervention</button>
    `;
    container.appendChild(block);
    recalc(id);
}

function setMode(id, mode) {
    const block = document.getElementById('ligne-' + id);
    block.querySelectorAll('.mode-btn').forEach(b => b.classList.toggle('active', b.dataset.mode === mode));
    block.querySelector('[data-panel="inverse"]').style.display = mode === 'inverse' ? 'block' : 'none';
    block.querySelector('[data-panel="direct"]').style.display = mode === 'direct' ? 'block' : 'none';
    block.dataset.mode = mode;
    recalc(id);
}

function recalc(id) {
    const block = document.getElementById('ligne-' + id);
    if (!block) return;
    const mode = block.dataset.mode || 'inverse';
    const get = (field) => parseFloat(block.querySelector(`[data-field="${field}"]`)?.value) || 0;
    const quantite = get('quantite') || 1;

    let prixUnitaire = 0;
    let debourseUnitaire = 0;

    if (mode === 'inverse') {
        debourseUnitaire = get('debourse_sec_unitaire');
        const margePct = get('marge_slider');
        block.querySelector('[data-out="marge-label"]').textContent = margePct + '%';
        prixUnitaire = margePct < 100 ? debourseUnitaire / (1 - margePct / 100) : debourseUnitaire;
    } else {
        prixUnitaire = get('prix_manuel');
        debourseUnitaire = get('debourse_sec_unitaire_direct');
    }

    const margeUnitaire = prixUnitaire - debourseUnitaire;
    const totalLigne = prixUnitaire * quantite;

    block.querySelector('[data-out="prix-unitaire"]').textContent = formatMoney(prixUnitaire);
    block.querySelector('[data-out="marge-unitaire"]').textContent = formatMoney(margeUnitaire);
    block.querySelector('[data-out="total-ligne"]').textContent = formatMoney(totalLigne);
}

function removeLigne(id) {
    const el = document.getElementById('ligne-' + id);
    if (el) el.remove();
}

function collectLignes() {
    const blocks = document.querySelectorAll('.ligne-block');
    const lignes = [];
    blocks.forEach(block => {
        const mode = block.dataset.mode || 'inverse';
        const get = (field) => block.querySelector(`[data-field="${field}"]`)?.value;
        const quantite = parseFloat(get('quantite')) || 1;
        const taux_tva = parseFloat(get('taux_tva')) || 20;
        let prix_unitaire_ht, debourse_sec_unitaire;

        if (mode === 'inverse') {
            debourse_sec_unitaire = parseFloat(get('debourse_sec_unitaire')) || 0;
            const margePct = parseFloat(get('marge_slider')) || 0;
            prix_unitaire_ht = margePct < 100 ? debourse_sec_unitaire / (1 - margePct / 100) : debourse_sec_unitaire;
        } else {
            prix_unitaire_ht = parseFloat(get('prix_manuel')) || 0;
            debourse_sec_unitaire = parseFloat(get('debourse_sec_unitaire_direct')) || 0;
        }

        lignes.push({
            designation: get('designation') || '(sans nom)',
            unite: get('unite'),
            quantite,
            prix_unitaire_ht: Math.round(prix_unitaire_ht * 100) / 100,
            debourse_sec_unitaire,
            taux_tva
        });
    });
    return lignes;
}

async function refreshProjectSelect() {
    try {
        const res = await fetch(API_URL + "/api/v1/projets/", {
            headers: { "Authorization": "Bearer " + token }
        });
        const data = await res.json();
        if (!res.ok) return;
        cachedProjects = data;
        const select = document.getElementById('devis-projet');
        select.innerHTML = data.map(p => "<option value='" + p.id_projet + "'>" + p.nom_projet + "</option>").join("");
    } catch (err) {}
}

async function register() {
    const nom = document.getElementById('reg-nom').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const entreprise = document.getElementById('reg-entreprise').value;
    const statusDiv = document.getElementById('auth-status');

    if (!nom || !email || !password) {
        statusDiv.textContent = "Nom, email et mot de passe obligatoires.";
        return;
    }

    statusDiv.textContent = "Création du compte... (le serveur peut mettre 30-50s à démarrer)";

    try {
        const res = await fetch(API_URL + "/api/v1/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nom, email, password, entreprise: entreprise || null })
        });
        const data = await res.json();

        if (!res.ok) {
            statusDiv.textContent = "Erreur : " + (data.detail || "inscription refusée");
            return;
        }

        statusDiv.textContent = "Compte créé ! Connexion en cours...";
        document.getElementById('login-email').value = email;
        document.getElementById('login-password').value = password;
        showLogin();
        await login();
    } catch (err) {
        statusDiv.textContent = "Erreur réseau : " + err.message;
    }
}

async function login() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = "Connexion... (le serveur peut mettre 30-50s à démarrer)";

    try {
        const res = await fetch(API_URL + "/api/v1/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (!res.ok) {
            statusDiv.textContent = "Erreur : " + (data.detail || "connexion refusée");
            return;
        }

        token = data.access_token;
        document.getElementById('login-section').style.display = "none";
        document.getElementById('to-register').style.display = "none";
        document.getElementById('app').style.display = "block";
        loadDashboard();
        loadDevisList();
    } catch (err) {
        statusDiv.textContent = "Erreur réseau : " + err.message;
    }
}

async function loadDashboard() {
    try {
        const res = await fetch(API_URL + "/api/v1/dashboard/summary", {
            headers: { "Authorization": "Bearer " + token }
        });
        const data = await res.json();

        if (!res.ok) {
            document.getElementById('details').innerHTML = "<p>Erreur : " + (data.detail || res.status) + "</p>";
            return;
        }

        document.getElementById('ca').textContent = formatMoney(data.chiffre_affaires_total);
        document.getElementById('marge').textContent = formatMoney(data.marge_brute_eur);
        document.getElementById('taux').textContent = data.taux_marque_pct + " %";
        document.getElementById('projets').textContent = data.nombre_projets;

        document.getElementById('details').innerHTML =
            "<div style='display:flex;justify-content:space-between;padding:8px 0'><span>Chantiers en cours</span><span>" + data.chantiers_en_cours + "</span></div>" +
            "<div style='display:flex;justify-content:space-between;padding:8px 0'><span>Nombre de devis</span><span>" + data.nombre_devis + "</span></div>" +
            "<div style='display:flex;justify-content:space-between;padding:8px 0'><span>Coût total</span><span>" + formatMoney(data.cout_total) + "</span></div>";
    } catch (err) {
        document.getElementById('details').innerHTML = "<p>Erreur réseau : " + err.message + "</p>";
    }
}

async function createProject() {
    const nom_projet = document.getElementById('proj-nom').value;
    const budget_initial_ht = parseFloat(document.getElementById('proj-budget').value) || 0;
    const marge_cible_pct = parseFloat(document.getElementById('proj-marge').value) || 30;
    const description = document.getElementById('proj-description').value;
    const statusDiv = document.getElementById('proj-status');

    if (!nom_projet) {
        statusDiv.textContent = "Le nom du projet est obligatoire.";
        return;
    }

    statusDiv.textContent = "Création en cours...";

    try {
        const res = await fetch(API_URL + "/api/v1/projets/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
            body: JSON.stringify({
                nom_projet, budget_initial_ht, marge_cible_pct,
                statut: "EN_COURS", description: description || null
            })
        });
        const data = await res.json();

        if (!res.ok) {
            statusDiv.textContent = "Erreur : " + (data.detail || res.status);
            return;
        }

        statusDiv.textContent = "Projet créé !";
        document.getElementById('proj-nom').value = "";
        document.getElementById('proj-description').value = "";
        loadDashboard();
    } catch (err) {
        statusDiv.textContent = "Erreur réseau : " + err.message;
    }
}

function resetDevisFormState() {
    editingDevisId = null;
    document.getElementById('btn-submit-devis').textContent = "Créer le devis";
    document.getElementById('btn-cancel-edit').style.display = "none";
}

function cancelEdit() {
    resetDevisFormState();
    document.getElementById('devis-titre').value = "";
    document.getElementById('lignes-container').innerHTML = "";
    addLigne();
    document.getElementById('devis-status').textContent = "";
}

async function createDevis() {
    const projetSelect = document.getElementById('devis-projet');
    const id_projet = projetSelect.value;
    const nomProjet = projetSelect.options[projetSelect.selectedIndex] ? projetSelect.options[projetSelect.selectedIndex].text : '';
    const titre = document.getElementById('devis-titre').value;
    const acompte_pct = parseFloat(document.getElementById('devis-acompte').value) || 30;
    const marge_cible_pct = parseFloat(document.getElementById('devis-marge').value) || 30;
    const lignes = collectLignes();
    const statusDiv = document.getElementById('devis-status');
    const btnPdf = document.getElementById('btn-pdf');

    if (!id_projet || !titre) {
        statusDiv.textContent = "Projet et titre obligatoires.";
        return;
    }
    if (lignes.length === 0 || !lignes.some(l => l.designation && l.designation !== '(sans nom)')) {
        statusDiv.textContent = "Ajoute au moins une intervention avec une désignation.";
        return;
    }

    statusDiv.textContent = editingDevisId ? "Mise à jour en cours..." : "Création en cours...";
    btnPdf.style.display = "none";

    const payload = {
        titre, acompte_pct, id_projet, marge_cible_pct,
        fournisseur_non_verifie: false,
        lots: [{ nom_lot: "Lot principal", lignes }]
    };

    try {
        const url = editingDevisId ? API_URL + "/api/v1/devis/" + editingDevisId : API_URL + "/api/v1/devis/";
        const method = editingDevisId ? "PUT" : "POST";
        const res = await fetch(url, {
            method,
            headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (!res.ok) {
            statusDiv.textContent = "Erreur : " + (data.detail || res.status);
            return;
        }

        statusDiv.textContent = (editingDevisId ? "Devis mis à jour ! " : "Devis créé ! ") + "Marge : " + formatMoney(data.marge_brute_eur) + " (" + data.taux_marque_pct + "%)";

        lastDevis = { ...data, titre, nomProjet, acompte_pct, lignes };
        btnPdf.style.display = "block";

        resetDevisFormState();
        document.getElementById('devis-titre').value = "";
        document.getElementById('lignes-container').innerHTML = "";
        addLigne();
        loadDashboard();
        loadDevisList();
    } catch (err) {
        statusDiv.textContent = "Erreur réseau : " + err.message;
    }
}

async function loadDevisList() {
    const statusDiv = document.getElementById('devis-list-status');
    const listDiv = document.getElementById('devis-list');
    statusDiv.textContent = "Chargement...";
    try {
        const res = await fetch(API_URL + "/api/v1/devis/", {
            headers: { "Authorization": "Bearer " + token }
        });
        const data = await res.json();
        if (!res.ok) {
            statusDiv.textContent = "Erreur : " + (data.detail || res.status);
            return;
        }
        statusDiv.textContent = "";
        afficherGestionDevis(data);
    } catch (err) {
        statusDiv.textContent = "Erreur réseau : " + err.message;
    }
}

function afficherGestionDevis(devisList) {
    const container = document.getElementById('devis-list');
    container.innerHTML = '';

    if (devisList.length === 0) {
        container.innerHTML = "<p style='color:var(--text-muted); text-align:center;'>Aucun devis pour l'instant.</p>";
        return;
    }

    devisList.forEach(devis => {
        const card = document.createElement('div');
        card.className = 'devis-card';

        const statutHtml = devis.can_send
            ? '<span class="badge-vert">Vérifié - Prêt à imprimer</span>'
            : '<span class="badge-orange">À vérifier / En cours</span>';

        card.innerHTML = `
            <div class="devis-header">
                <span class="devis-titre">${devis.reference || 'Sans titre'}</span>
                <span class="devis-montant">${formatMoney(devis.total_ttc)} TTC</span>
            </div>
            <div class="devis-sous-titre">Marge : ${formatMoney(devis.marge_brute_eur)} — Taux de marque : ${devis.taux_marque_pct}%</div>
            <div class="devis-statut-container">${statutHtml}</div>
            <div class="devis-actions">
                <button class="btn-modifier" onclick="chargerDevisPourModification('${devis.id_devis}', ${devis.total_ht}, ${devis.cout_total})">Modifier</button>
                <button class="btn-telecharger" onclick="telechargerPdfResume('${devis.id_devis}')">PDF</button>
                <button class="btn-supprimer" onclick="supprimerDevis('${devis.id_devis}')">Supprimer</button>
            </div>
        `;
        container.appendChild(card);

        card.dataset.devis = JSON.stringify(devis);
    });

    window._devisCache = devisList;
}

function chargerDevisPourModification(id_devis) {
    const devis = (window._devisCache || []).find(d => d.id_devis === id_devis);
    if (!devis) return;

    editingDevisId = id_devis;
    document.getElementById('btn-submit-devis').textContent = "Enregistrer les modifications";
    document.getElementById('btn-cancel-edit').style.display = "block";

    document.getElementById('devis-form').style.display = "block";
    document.getElementById('devis-titre').value = devis.reference || '';

    document.getElementById('lignes-container').innerHTML = "";
    addLigne();
    setMode(ligneCounter, 'direct');
    const block = document.getElementById('ligne-' + ligneCounter);
    block.querySelector('[data-field="designation"]').value = devis.reference || 'Ligne existante';
    block.querySelector('[data-field="quantite"]').value = 1;
    block.querySelector('[data-field="prix_manuel"]').value = devis.total_ht;
    block.querySelector('[data-field="debourse_sec_unitaire_direct"]').value = devis.cout_total;
    recalc(ligneCounter);

    document.getElementById('devis-status').textContent = "Modification : ajuste les lignes puis enregistre.";
    window.scrollTo({ top: document.getElementById('devis-form').offsetTop - 20, behavior: 'smooth' });
}

async function supprimerDevis(id_devis) {
    if (!confirm("Supprimer ce devis ? Cette action est irréversible.")) return;
    try {
        const res = await fetch(API_URL + "/api/v1/devis/" + id_devis, {
            method: "DELETE",
            headers: { "Authorization": "Bearer " + token }
        });
        if (!res.ok) {
            const data = await res.json();
            alert("Erreur : " + (data.detail || res.status));
            return;
        }
        loadDevisList();
        loadDashboard();
    } catch (err) {
        alert("Erreur réseau : " + err.message);
    }
}

function telechargerPdfResume(id_devis) {
    const devis = (window._devisCache || []).find(d => d.id_devis === id_devis);
    if (!devis) return;

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const gold = [245, 158, 11];
    const dark = [30, 30, 30];
    const muted = [120, 120, 120];

    doc.setFillColor(...gold);
    doc.rect(0, 0, 210, 24, 'F');
    doc.setFontSize(18);
    doc.setTextColor(255, 255, 255);
    doc.text("ASSAWIN PRO", 14, 16);
    doc.setFontSize(10);
    doc.text("DEVIS - RESUME", 155, 16);

    let y = 40;
    doc.setTextColor(...dark);
    doc.setFontSize(15);
    doc.text(devis.reference || "Devis", 14, y);
    y += 12;

    const lines = [
        ["Total HT", devis.total_ht, false],
        ["TVA", devis.total_tva, false],
        ["Total TTC", devis.total_ttc, true],
        ["Marge brute", devis.marge_brute_eur, false],
        ["Taux de marque", devis.taux_marque_pct + " %", false],
        ["Acompte", devis.acompte_montant, false],
    ];

    lines.forEach(([label, val, isBold]) => {
        doc.setFontSize(isBold ? 12 : 10);
        doc.setTextColor(isBold ? gold[0] : dark[0], isBold ? gold[1] : dark[1], isBold ? gold[2] : dark[2]);
        doc.text(String(label), 14, y);
        doc.text(typeof val === 'number' ? formatMoney(val) : String(val), 140, y);
        y += 8;
    });

    y += 15;
    doc.setFontSize(8);
    doc.setTextColor(...muted);
    doc.text("Résumé généré via ASSAWIN PRO. Pour le détail des lignes, consulte le PDF généré à la création du devis.", 14, y);

    doc.save((devis.reference || "devis") + "-resume.pdf");
}

function formatMoney(val) {
    const num = parseFloat(val) || 0;
    return num.toFixed(2).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' €';
}

function generatePDF() {
    if (!lastDevis) return;
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const gold = [245, 158, 11];
    const dark = [30, 30, 30];
    const muted = [120, 120, 120];

    doc.setFillColor(...gold);
    doc.rect(0, 0, 210, 24, 'F');
    doc.setFontSize(18);
    doc.setTextColor(255, 255, 255);
    doc.text("ASSAWIN PRO", 14, 16);
    doc.setFontSize(10);
    doc.text("DEVIS", 175, 16);

    let y = 36;
    doc.setTextColor(...dark);
    doc.setFontSize(15);
    doc.text(lastDevis.titre, 14, y);

    y += 10;
    doc.setFillColor(245, 245, 247);
    doc.roundedRect(14, y, 182, 22, 2, 2, 'F');
    doc.setFontSize(9);
    doc.setTextColor(...muted);
    doc.text("Client / Projet :", 18, y + 7);
    doc.text("Référence :", 18, y + 14);
    doc.text("Date :", 130, y + 7);

    doc.setTextColor(...dark);
    doc.text(lastDevis.nomProjet, 48, y + 7);
    doc.text(String(lastDevis.reference || "N/A"), 40, y + 14);
    doc.text(new Date().toLocaleDateString('fr-FR'), 145, y + 7);

    y += 32;

    doc.setFillColor(30, 30, 30);
    doc.rect(14, y, 182, 8, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(9);
    doc.text("Désignation", 18, y + 5.5);
    doc.text("Qté", 110, y + 5.5);
    doc.text("Unité", 126, y + 5.5);
    doc.text("Prix U. HT", 148, y + 5.5);
    doc.text("Total HT", 174, y + 5.5);
    y += 8;

    lastDevis.lignes.forEach((l) => {
        const totalLigne = l.prix_unitaire_ht * l.quantite;
        doc.setFontSize(9);
        doc.setTextColor(...dark);
        doc.text(String(l.designation).substring(0, 42), 18, y + 6);
        doc.text(String(l.quantite), 110, y + 6);
        doc.text(String(l.unite), 126, y + 6);
        doc.text(formatMoney(l.prix_unitaire_ht), 148, y + 6);
        doc.text(formatMoney(totalLigne), 174, y + 6);
        y += 9;
        doc.setDrawColor(230, 230, 230);
        doc.line(14, y, 196, y);
    });

    y += 10;

    const totalsX = 120;
    const valuesX = 174;
    const totals = [
        ["Total HT", lastDevis.total_ht, false],
        ["TVA", lastDevis.total_tva, false],
        ["Total TTC", lastDevis.total_ttc, true],
        ["Acompte (" + lastDevis.acompte_pct + "%)", lastDevis.acompte_montant, false]
    ];

    totals.forEach(([label, val, isBold]) => {
        doc.setFontSize(isBold ? 11 : 9);
        doc.setTextColor(isBold ? gold[0] : dark[0], isBold ? gold[1] : dark[1], isBold ? gold[2] : dark[2]);
        doc.text(label, totalsX, y);
        doc.text(formatMoney(val), valuesX, y);
        y += 7;
    });

    y += 15;
    doc.setFontSize(8);
    doc.setTextColor(...muted);
    doc.text("Devis généré via ASSAWIN PRO — Document sous réserve d'acceptation. Validité 30 jours.", 14, y);

    doc.save((lastDevis.reference || "devis") + ".pdf");
}
</script>
</body>
</html>