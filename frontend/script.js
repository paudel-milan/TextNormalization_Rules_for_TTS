/**
 * Frontend JavaScript for Hybrid Text Normalization
 * Supports Manual Mode (existing) and Auto Detect Mode (ML + Rules)
 */

// Configuration
const API_BASE_URL = 'http://localhost:5003/api';

// ──────────────────────────────────────────────────────────────
//  DOM Elements
// ──────────────────────────────────────────────────────────────
const normalizeBtn = document.getElementById('normalize-btn');
const inputText = document.getElementById('input-text');
const languageSelect = document.getElementById('language');

// Manual mode elements
const outputSection = document.getElementById('output-section');
const normalizedTextEl = document.getElementById('normalized-text');
const ssmlOutputEl = document.getElementById('ssml-output');
const dfaInfoEl = document.getElementById('dfa-info');
const copySsmlBtn = document.getElementById('copy-ssml-btn');

// Auto detect mode elements
const autoDetectSection = document.getElementById('auto-detect-section');
const autoNormalizedTextEl = document.getElementById('auto-normalized-text');
const autoSsmlOutputEl = document.getElementById('auto-ssml-output');
const tokenTableBody = document.getElementById('token-table-body');
const pipelineSummaryEl = document.getElementById('pipeline-summary');

// Mode elements
const categoriesSection = document.getElementById('categories-section');
const modelStatusEl = document.getElementById('model-status');
const modelStatusTextEl = document.getElementById('model-status-text');
const btnTrain = document.getElementById('btn-train');

// Error
const errorSection = document.getElementById('error-section');
const errorMessageEl = document.getElementById('error-message');

// ──────────────────────────────────────────────────────────────
//  State
// ──────────────────────────────────────────────────────────────
let currentMode = 'manual'; // 'manual' or 'auto'

// ──────────────────────────────────────────────────────────────
//  Mode Toggle Logic
// ──────────────────────────────────────────────────────────────
document.querySelectorAll('input[name="mode"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        currentMode = e.target.value;
        updateModeUI();
    });
});

function updateModeUI() {
    if (currentMode === 'auto') {
        categoriesSection.classList.add('hidden');
        modelStatusEl.style.display = 'flex';
        checkModelStatus();
    } else {
        categoriesSection.classList.remove('hidden');
        modelStatusEl.style.display = 'none';
    }

    // Hide both output sections when switching modes
    outputSection.style.display = 'none';
    autoDetectSection.style.display = 'none';
    hideError();
}

// ──────────────────────────────────────────────────────────────
//  Model Status
// ──────────────────────────────────────────────────────────────
async function checkModelStatus() {
    const language = languageSelect.value;
    try {
        const response = await fetch(`${API_BASE_URL}/model-status?language=${language}`);
        const data = await response.json();

        if (data.success && data.model_status[language]) {
            const status = data.model_status[language];
            if (status.has_model) {
                modelStatusEl.className = 'model-status loaded';
                modelStatusTextEl.textContent = `ML Model: Loaded (${status.available_models.join(', ')})`;
                btnTrain.textContent = 'Retrain';
            } else {
                modelStatusEl.className = 'model-status not-loaded';
                modelStatusTextEl.textContent = 'ML Model: Not trained — Rule-only mode active';
                btnTrain.textContent = 'Train Model';
            }
        }
    } catch (error) {
        modelStatusEl.className = 'model-status not-loaded';
        modelStatusTextEl.textContent = 'ML Model: Backend not reachable';
    }
}

// Re-check model status when language changes
languageSelect.addEventListener('change', () => {
    if (currentMode === 'auto') {
        checkModelStatus();
    }
});

// ──────────────────────────────────────────────────────────────
//  Train Model
// ──────────────────────────────────────────────────────────────
async function trainModel() {
    const language = languageSelect.value;
    btnTrain.disabled = true;
    btnTrain.textContent = 'Training...';

    try {
        const response = await fetch(`${API_BASE_URL}/train`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ language: language }),
        });

        const data = await response.json();

        if (data.success) {
            modelStatusEl.className = 'model-status loaded';
            modelStatusTextEl.textContent =
                `ML Model: Trained ✓ (Accuracy: ${(data.accuracy * 100).toFixed(1)}%)`;
            btnTrain.textContent = 'Retrain';
        } else {
            showError(`Training failed: ${data.error}`);
        }
    } catch (error) {
        showError(`Training error: ${error.message}`);
    } finally {
        btnTrain.disabled = false;
    }
}

// ──────────────────────────────────────────────────────────────
//  Category Helpers
// ──────────────────────────────────────────────────────────────
function getSelectedCategories() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][id^="category-"]');
    const categories = [];
    checkboxes.forEach(cb => {
        if (cb.checked) categories.push(cb.value);
    });
    return categories;
}

// ──────────────────────────────────────────────────────────────
//  Error Display
// ──────────────────────────────────────────────────────────────
function showError(message) {
    errorSection.style.display = 'block';
    outputSection.style.display = 'none';
    autoDetectSection.style.display = 'none';
    errorMessageEl.textContent = message;
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError() {
    errorSection.style.display = 'none';
}

// ──────────────────────────────────────────────────────────────
//  Main Normalize Handler
// ──────────────────────────────────────────────────────────────
async function normalizeText() {
    const text = inputText.value.trim();

    if (!text) {
        showError('Please enter some text to normalize');
        return;
    }

    if (currentMode === 'manual') {
        const categories = getSelectedCategories();
        if (categories.length === 0) {
            showError('Please select at least one normalization category');
            return;
        }
        await normalizeManual(text, categories);
    } else {
        await normalizeAutoDetect(text);
    }
}

// ──────────────────────────────────────────────────────────────
//  Manual Mode Normalization
// ──────────────────────────────────────────────────────────────
async function normalizeManual(text, categories) {
    hideError();
    normalizeBtn.disabled = true;
    normalizeBtn.innerHTML = '<span class="btn-icon">⏳</span> Processing...';

    try {
        const response = await fetch(`${API_BASE_URL}/normalize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                categories: categories,
                language: languageSelect.value,
            }),
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Normalization failed');
        }

        normalizedTextEl.textContent = data.normalized_text;
        ssmlOutputEl.textContent = data.ssml;
        displayDFAInfo(data.dfa_info);

        autoDetectSection.style.display = 'none';
        outputSection.style.display = 'block';
        outputSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    } catch (error) {
        console.error('Error:', error);
        showError(`Error: ${error.message}. Make sure the backend server is running.`);
    } finally {
        normalizeBtn.disabled = false;
        normalizeBtn.innerHTML = '<span class="btn-icon">⚡</span> Generate Normalization';
    }
}

// ──────────────────────────────────────────────────────────────
//  Auto Detect Mode Normalization
// ──────────────────────────────────────────────────────────────
async function normalizeAutoDetect(text) {
    hideError();
    normalizeBtn.disabled = true;
    normalizeBtn.innerHTML = '<span class="btn-icon">🤖</span> Detecting & Normalizing...';

    try {
        const response = await fetch(`${API_BASE_URL}/auto-normalize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                language: languageSelect.value,
            }),
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Auto-normalization failed');
        }

        // Render results
        renderPipelineSummary(data.pipeline_summary);
        renderTokenTable(data.token_details);
        autoNormalizedTextEl.textContent = data.normalized_text;
        autoSsmlOutputEl.textContent = data.ssml;

        outputSection.style.display = 'none';
        autoDetectSection.style.display = 'block';
        autoDetectSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    } catch (error) {
        console.error('Error:', error);
        showError(`Error: ${error.message}. Make sure the backend server is running.`);
    } finally {
        normalizeBtn.disabled = false;
        normalizeBtn.innerHTML = '<span class="btn-icon">⚡</span> Generate Normalization';
    }
}

// ──────────────────────────────────────────────────────────────
//  Render Pipeline Summary
// ──────────────────────────────────────────────────────────────
function renderPipelineSummary(summary) {
    const mlLabel = summary.ml_model_used ? '✅ ML Active' : '⚠️ Rule-Only';

    pipelineSummaryEl.innerHTML = `
        <div class="summary-stat">
            <div class="summary-stat-value">${summary.total_tokens}</div>
            <div class="summary-stat-label">Total Tokens</div>
        </div>
        <div class="summary-stat">
            <div class="summary-stat-value">${summary.detected_tokens}</div>
            <div class="summary-stat-label">Detected Tokens</div>
        </div>
        <div class="summary-stat">
            <div class="summary-stat-value">${summary.categories_found.length}</div>
            <div class="summary-stat-label">Categories Found</div>
        </div>
        <div class="summary-stat">
            <div class="summary-stat-value" style="font-size: 1rem;">${mlLabel}</div>
            <div class="summary-stat-label">ML Status</div>
        </div>
    `;
}

// ──────────────────────────────────────────────────────────────
//  Render Token Detection Table
// ──────────────────────────────────────────────────────────────
function renderTokenTable(tokenDetails) {
    tokenTableBody.innerHTML = '';

    tokenDetails.forEach(detail => {
        const row = document.createElement('tr');

        const confidenceLevel = detail.final_confidence >= 0.8 ? 'high' :
                               detail.final_confidence >= 0.5 ? 'medium' : 'low';
        const confidencePercent = Math.round(detail.final_confidence * 100);

        row.innerHTML = `
            <td class="token-cell">${escapeHtml(detail.token)}</td>
            <td><span class="category-badge ${detail.rule_category}">${detail.rule_category}</span></td>
            <td><span class="category-badge ${detail.ml_category}">${detail.ml_category}</span></td>
            <td><span class="category-badge ${detail.final_category}">${detail.final_category}</span></td>
            <td>
                <div class="confidence-bar-wrapper">
                    <div class="confidence-bar">
                        <div class="confidence-fill ${confidenceLevel}" style="width: ${confidencePercent}%"></div>
                    </div>
                    <span class="confidence-value">${confidencePercent}%</span>
                </div>
            </td>
            <td class="token-cell">${escapeHtml(detail.normalized)}</td>
        `;

        tokenTableBody.appendChild(row);
    });
}

// ──────────────────────────────────────────────────────────────
//  DFA Info Display (Manual mode)
// ──────────────────────────────────────────────────────────────
function displayDFAInfo(dfaInfo) {
    if (!dfaInfo || dfaInfo.length === 0) {
        dfaInfoEl.innerHTML = '<p style="color: var(--text-muted);">No DFA transitions detected</p>';
        return;
    }

    let html = '';
    dfaInfo.forEach(item => {
        html += `
            <div class="dfa-item">
                <div class="dfa-category">${item.category}</div>
                <div class="dfa-original">Original: <strong>${item.original}</strong></div>
                <div class="dfa-states">
                    ${item.states.map((state, index) => {
            if (index === item.states.length - 1) {
                return `<span class="dfa-state">${state}</span>`;
            }
            return `<span class="dfa-state">${state}</span><span class="dfa-arrow">→</span>`;
        }).join('')}
                </div>
            </div>
        `;
    });

    dfaInfoEl.innerHTML = html;
}

// ──────────────────────────────────────────────────────────────
//  Copy SSML
// ──────────────────────────────────────────────────────────────
async function copySsml(elementId) {
    const el = document.getElementById(elementId);
    const ssmlText = el.textContent;

    try {
        await navigator.clipboard.writeText(ssmlText);

        const btn = el.parentElement.querySelector('.btn-secondary');
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        btn.style.background = 'var(--success-gradient)';
        btn.style.color = 'white';

        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
            btn.style.color = '';
        }, 2000);

    } catch (error) {
        console.error('Failed to copy:', error);
        alert('Failed to copy SSML to clipboard');
    }
}

// Legacy copy handler for manual mode
async function copySsmlToClipboard() {
    await copySsml('ssml-output');
}

// ──────────────────────────────────────────────────────────────
//  Utility
// ──────────────────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ──────────────────────────────────────────────────────────────
//  Health Check
// ──────────────────────────────────────────────────────────────
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            console.log('✓ Backend is healthy:', data);
            if (data.modes && data.modes.includes('auto_detect')) {
                console.log('✓ Auto Detect mode available');
            }
        }
    } catch (error) {
        console.warn('⚠ Backend not reachable. Please start the backend server.');
        showError('Backend server is not running. Please start it with: cd backend && python app.py');
    }
}

// ──────────────────────────────────────────────────────────────
//  Event Listeners
// ──────────────────────────────────────────────────────────────
normalizeBtn.addEventListener('click', normalizeText);
copySsmlBtn.addEventListener('click', copySsmlToClipboard);

inputText.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        normalizeText();
    }
});

window.addEventListener('DOMContentLoaded', () => {
    checkBackendHealth();
    updateModeUI();
});

console.log('💡 Tip: Use Ctrl+Enter to quickly submit text for normalization');
console.log('🤖 Auto Detect mode uses ML + Rules for category detection');
