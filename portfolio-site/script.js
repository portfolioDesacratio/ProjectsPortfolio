/**
 * Desacratio Portfolio — все скрипты
 * темы, частицы, счётчики, модалка, бургер, параллакс
 */

// ========== ТРОТТЛ ==========
function throttle(fn, limit) {
    let last = 0;
    return function(...args) {
        const now = Date.now();
        if (now - last >= limit) { last = now; fn.apply(this, args); }
    };
}

// ========== ПЕРЕКЛЮЧЕНИЕ ТЕМЫ ==========
const themeToggle = document.getElementById('themeToggle');
let currentTheme = localStorage.getItem('theme') || 'dark';

function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    themeToggle.textContent = theme === 'dark' ? '🌙' : '☀️';
    localStorage.setItem('theme', theme);
    currentTheme = theme;
    if (typeof drawParticles === 'function') setTimeout(drawParticles, 50);
}

applyTheme(currentTheme);

themeToggle.addEventListener('click', () => {
    applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
});

// ========== БУРГЕР-МЕНЮ ==========
const burger = document.getElementById('burgerBtn');
const nav = document.querySelector('.nav-links');

if (burger) {
    burger.addEventListener('click', () => {
        nav.classList.toggle('active');
        burger.classList.toggle('active');
        burger.setAttribute('aria-expanded', nav.classList.contains('active'));
    });
}

document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        nav.classList.remove('active');
        burger.classList.remove('active');
        burger.setAttribute('aria-expanded', 'false');
    });
});

// ========== ПЛАВНЫЙ СКРОЛЛ ==========
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        const target = document.querySelector(href);
        if (target) {
            e.preventDefault();
            const offset = 80;
            const top = target.getBoundingClientRect().top + window.pageYOffset - offset;
            window.scrollTo({ top, behavior: 'smooth' });
        }
    });
});

// ========== АНИМАЦИЯ ЦИФР (СЧЁТЧИКИ) ==========
function animCounter(el, target, suffix = '') {
    let current = 0;
    let step = Math.ceil(target / 50);
    let timer = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        el.textContent = current + suffix;
    }, 18);
}

const cntObserver = new IntersectionObserver((entries) => {
    for (let entry of entries) {
        if (entry.isIntersecting) {
            let el = entry.target;
            let id = el.id;
            if (id == 'projectsCount') animCounter(el, 25, '+');
            if (id == 'clientsCount') animCounter(el, 10, '+');
            if (id == 'linesCount') animCounter(el, 10, 'K+');
            cntObserver.unobserve(el);
        }
    }
}, { threshold: 0.5 });

['projectsCount', 'clientsCount', 'linesCount'].forEach(id => {
    let el = document.getElementById(id);
    if (el) cntObserver.observe(el);
});

// ========== ПАРАЛЛАКС (ТРОТТЛ) ==========
window.addEventListener('scroll', throttle(() => {
    let hero = document.querySelector('.hero-content');
    if (hero) {
        let scrolled = window.pageYOffset;
        let h = window.innerHeight;
        if (scrolled < h) {
            hero.style.transform = `translateY(${scrolled * 0.08}px)`;
            hero.style.opacity = 1 - (scrolled / (h * 0.5));
        }
    }
}, 60));

// ========== ЧАСТИЦЫ ==========
(function() {
    const canvas = document.getElementById('particlesCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    let rafId = null;
    let running = false;
    let lastFrame = 0;
    let currentW = 0, currentH = 0;
    let resizeTimer = null;

    function rand(min, max) { return Math.random() * (max - min) + min; }
    function isMobile() { return window.innerWidth <= 768; }
    function isTiny() { return window.innerWidth <= 480; }
    function particleCount() {
        if (isTiny()) return 45;
        if (isMobile()) return 70;
        return 100;
    }
    function effectiveDPR() {
        const dpr = window.devicePixelRatio || 1;
        return isMobile() ? Math.min(dpr, 2) : Math.min(dpr, 3);
    }

    function createParticle(w, h, fromBottom) {
        const small = isTiny();
        return {
            x: rand(0, w),
            y: fromBottom ? rand(h + 5, h + 40) : rand(0, h),
            size: rand(small ? 1.2 : 1.5, small ? 2.8 : 3.5),
            alpha: rand(small ? 0.25 : 0.3, small ? 0.55 : 0.75),
            speedY: rand(0.08, 0.25),
            driftX: rand(-0.15, 0.15),
            phase: rand(0, Math.PI * 2),
            phaseSpeed: rand(0.004, 0.012),
            sway: rand(0.02, 0.06),
        };
    }

    window.drawParticles = function() { draw(); };

    function resize() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        if (w === currentW && h === currentH) return;
        currentW = w; currentH = h;
        const dpr = effectiveDPR();
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        canvas.style.width = w + 'px';
        canvas.style.height = h + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        const num = particleCount();
        const next = [];
        for (let i = 0; i < num; i++) {
            if (particles[i]) next.push(particles[i]);
            else next.push(createParticle(w, h, false));
        }
        particles = next;
    }

    function debouncedResize() {
        if (resizeTimer) { cancelAnimationFrame(resizeTimer); resizeTimer = null; }
        resizeTimer = requestAnimationFrame(resize);
    }

    function draw() {
        const w = window.innerWidth, h = window.innerHeight;
        ctx.clearRect(0, 0, w, h);
        const isLight = document.body.getAttribute('data-theme') === 'light';
        const color = isLight ? '0,0,0' : '255,255,255';
        const mobile = isMobile();

        // Частицы
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            p.phase += p.phaseSpeed;
            p.x += p.driftX + Math.sin(p.phase) * p.sway;
            p.y -= p.speedY;
            if (p.y + p.size < 0) { particles[i] = createParticle(w, h, true); continue; }
            if (p.x < -10) p.x = w + 10;
            if (p.x > w + 10) p.x = -10;
            ctx.beginPath();
            ctx.fillStyle = `rgba(${color},${p.alpha})`;
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        }

        // Паутинка (links)
        const linkDist = mobile ? 100 : 160;
        const linkDistSq = linkDist * linkDist;
        const maxLinks = mobile ? 2 : 3;
        for (let i = 0; i < particles.length; i++) {
            const a = particles[i];
            let links = 0;
            for (let j = i + 1; j < particles.length; j++) {
                if (links >= maxLinks) break;
                const b = particles[j];
                const dx = a.x - b.x, dy = a.y - b.y;
                const distSq = dx * dx + dy * dy;
                if (distSq > linkDistSq) continue;
                const strength = 1 - (distSq / linkDistSq);
                const alpha = Math.max(0, (mobile ? 0.35 : 0.5) * strength);
                ctx.beginPath();
                ctx.strokeStyle = `rgba(${color},${alpha})`;
                ctx.lineWidth = mobile ? 0.6 : 1.0;
                ctx.moveTo(a.x, a.y);
                const mx = (a.x + b.x) / 2 + Math.sin(a.phase + b.phase) * 1.2;
                const my = (a.y + b.y) / 2 + Math.cos(a.phase + b.phase) * 1;
                ctx.quadraticCurveTo(mx, my, b.x, b.y);
                ctx.stroke();
                links++;
            }
        }
    }

    function animate(ts) {
        if (!running) return;
        const fps = isMobile() ? 24 : 40;
        const frameMs = 1000 / fps;
        if (!lastFrame || ts - lastFrame >= frameMs) { lastFrame = ts; draw(); }
        rafId = requestAnimationFrame(animate);
    }

    function start() { if (!running) { running = true; rafId = requestAnimationFrame(animate); } }
    function stop() { running = false; if (rafId) { cancelAnimationFrame(rafId); rafId = null; } }

    document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); else start(); });
    window.addEventListener('resize', debouncedResize);
    resize();
    start();
})();

// ========== ПОДСВЕТКА РАЗДЕЛА В НАВБАРЕ ==========
const sections = document.querySelectorAll('section[id]');
const navAnchors = document.querySelectorAll('.nav-links a');
window.addEventListener('scroll', throttle(() => {
    let current = '';
    const scrollY = window.pageYOffset;
    sections.forEach(section => {
        const top = section.offsetTop - 150;
        if (scrollY >= top) current = section.getAttribute('id');
    });
    navAnchors.forEach(a => {
        a.style.color = a.getAttribute('href') === '#' + current ? 'var(--accent1)' : '';
    });
}, 80));

// ========== МОДАЛКА ДЛЯ ПРОЕКТОВ ==========
const projectCards = document.querySelectorAll('.project-card');
const modalOverlay = document.getElementById('projectModal');
const modalTitle = document.getElementById('modalTitle');
const modalBody = document.getElementById('modalBody');
const modalClose = document.getElementById('modalClose');

if (modalOverlay) {
    projectCards.forEach(card => {
        card.addEventListener('click', function() {
            const title = this.querySelector('h3').textContent;
            const desc = this.querySelector('.project-desc').textContent;
            const techs = [...this.querySelectorAll('.project-tech span')].map(s => s.textContent);
            const link = this.querySelector('.project-link')?.getAttribute('href');

            modalTitle.textContent = title;
            modalBody.innerHTML = `
                <p>${desc}</p>
                <h3>Технологии</h3>
                <div class="project-tech">${techs.map(t => `<span>${t}</span>`).join('')}</div>
                ${link ? `<a href="${link}" class="project-link" target="_blank" rel="noopener">→ Открыть на GitHub</a>` : ''}
            `;
            modalOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    });

    function closeModal() {
        modalOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    modalClose.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

// ===== ПРИВЕТСТВИЕ В КОНСОЛИ =====
console.log('%c Desacratio ', 'background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; font-size: 18px; padding: 10px 20px; border-radius: 8px; font-weight: bold;');
console.log('%c Пишу коды, для вас ', 'color: #667eea; font-size: 13px;');
console.log('%c tg: @desacratio ', 'color: #764ba2; font-size: 13px;');
