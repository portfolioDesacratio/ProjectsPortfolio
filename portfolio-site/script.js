/**
 * всякие приколы для сайта
 * анимации, меню на телефонах, счётчики
 */

// ========== БУРГЕР-МЕНЮ (ДЛЯ ТЕЛЕФОНОВ) ==========
const burger = document.getElementById('burgerBtn');
const nav = document.querySelector('.nav-links');

if (burger) {
    burger.addEventListener('click', () => {
        nav.classList.toggle('active');
        // просто анимация иконки
        const spans = burger.querySelectorAll('span');
        for (let s of spans) {
            s.classList.toggle('active');
        }
    });
}

// когда нажали на ссылку - закрываем меню
const links = document.querySelectorAll('.nav-links a');
for (let link of links) {
    link.addEventListener('click', () => {
        nav.classList.remove('active');
    });
}

// ========== АНИМАЦИЯ ЦИФР (СЧЁТЧИКИ) ==========
function animCounter(el, target, suffix = '') {
    let current = 0;
    let step = Math.ceil(target / 60); // чтоб за секунду досчитало
    let timer = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        el.textContent = current + suffix;
    }, 16);
}

// запускаем счётчики когда доскроллили до них
const observer = new IntersectionObserver((entries) => {
    for (let entry of entries) {
        if (entry.isIntersecting) {
            let el = entry.target;
            let id = el.id;
            if (id == 'projectsCount') animCounter(el, 5, '+');
            if (id == 'clientsCount') animCounter(el, 3, '+');
            if (id == 'linesCount') animCounter(el, 2, 'K+');
            observer.unobserve(el); // чтоб второй раз не сработало
        }
    }
}, { threshold: 0.5 });

// следим за элементами
let ids = ['projectsCount', 'clientsCount', 'linesCount'];
for (let id of ids) {
    let el = document.getElementById(id);
    if (el) observer.observe(el);
}

// ========== ПЛАВНЫЙ СКРОЛЛ К ЯКОРЯМ ==========
let anchors = document.querySelectorAll('a[href^="#"]');
for (let a of anchors) {
    a.addEventListener('click', function(e) {
        e.preventDefault();
        let target = this.getAttribute('href');
        if (target == '#') return;
        let el = document.querySelector(target);
        if (el) {
            el.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
            });
        }
    });
}

// ========== ПАРАЛЛАКС (ПРИКОЛЬНЫЙ ЭФФЕКТ) ==========
window.addEventListener('scroll', () => {
    let hero = document.querySelector('.hero-content');
    if (hero) {
        let scrolled = window.pageYOffset;
        hero.style.transform = `translateY(${scrolled * 0.1}px)`;
        hero.style.opacity = 1 - (scrolled / 600);
    }
});

// чисто для прикола в консоли
console.log('привет! если ты это читаешь - напиши мне в тг)');
