/* Light/dark theme toggle.
   Split out of console.js. These are classic scripts sharing one global
   scope; see channel/web/README.md before changing the load order. */

// =====================================================================
// Theme
// =====================================================================
// Fresh install is always light. A leftover cow_theme value is honored only
// after an explicit toggle (maliang_theme_explicit=1). Do not follow the OS.
function resolveThemePref() {
    if (typeof window.__maliangResolveTheme__ === 'function') {
        return window.__maliangResolveTheme__();
    }
    if (localStorage.getItem('maliang_theme_explicit') === '1') {
        const saved = localStorage.getItem('cow_theme') || localStorage.getItem('maliang_theme');
        if (saved === 'dark' || saved === 'light') return saved;
    }
    return window.__MALIANG_DEFAULT_THEME__ || 'light';
}
let currentTheme = resolveThemePref();

function applyTheme() {
    const root = document.documentElement;
    if (currentTheme === 'dark') {
        root.classList.add('dark');
        document.getElementById('theme-icon').className = 'fas fa-sun';
        document.getElementById('hljs-light').disabled = true;
        document.getElementById('hljs-dark').disabled = false;
    } else {
        root.classList.remove('dark');
        document.getElementById('theme-icon').className = 'fas fa-moon';
        document.getElementById('hljs-light').disabled = false;
        document.getElementById('hljs-dark').disabled = true;
    }
    // Color themes (themes.js) are console-only; the guest page has none.
    if (typeof applyColorTheme === 'function') applyColorTheme();
    rerenderMermaidDiagrams();
}

// Mermaid bakes the theme colors into the rendered SVG, so a theme switch
// re-renders diagrams the user already previewed. Never-previewed blocks are
// left alone, so this never triggers the mermaid download by itself.
function rerenderMermaidDiagrams() {
    document.querySelectorAll('.mermaid-block[data-mermaid="done"]').forEach(block => {
        block.dataset.mermaid = 'pending';
        const figure = block.querySelector('.mermaid-figure');
        if (figure) figure.remove();
    });
    if (document.querySelector('.mermaid-block[data-mermaid="pending"]')) {
        renderMermaidBlocks(document);
    }
}

function toggleTheme() {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('cow_theme', currentTheme);
    localStorage.setItem('maliang_theme_explicit', '1');
    applyTheme();
}

