/* ═══════════════════════════════════════
   the.designdhamaka — Main JS
═══════════════════════════════════════ */

// ── LOADER
window.addEventListener('load', () => {
  setTimeout(() => {
    document.getElementById('loader').classList.add('hidden');
  }, 1500);
});

// ── AOS INIT
AOS.init({ duration: 700, easing: 'ease-out', once: true, offset: 60 });

// ── CURSOR
const cursor = document.getElementById('cursor');
const follower = document.getElementById('cursor-follower');
if (cursor && window.matchMedia('(hover: hover)').matches) {
  let mx = 0, my = 0, fx = 0, fy = 0;
  document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; cursor.style.left = mx + 'px'; cursor.style.top = my + 'px'; });
  function animFollower() { fx += (mx - fx) * 0.12; fy += (my - fy) * 0.12; follower.style.left = fx + 'px'; follower.style.top = fy + 'px'; requestAnimationFrame(animFollower); }
  animFollower();
  document.querySelectorAll('a, button, .card, .portfolio-item').forEach(el => {
    el.addEventListener('mouseenter', () => { cursor.style.width = '14px'; cursor.style.height = '14px'; follower.style.width = '50px'; follower.style.height = '50px'; follower.style.borderColor = 'rgba(255,107,0,0.8)'; });
    el.addEventListener('mouseleave', () => { cursor.style.width = '8px'; cursor.style.height = '8px'; follower.style.width = '32px'; follower.style.height = '32px'; follower.style.borderColor = 'rgba(255,107,0,0.5)'; });
  });
}

// ── NAVBAR SCROLL
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 40);
});

// ── HAMBURGER
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');
if (hamburger) {
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('open');
  });
  document.querySelectorAll('.nav-link, .nav-cta').forEach(l => l.addEventListener('click', () => {
    hamburger.classList.remove('active');
    navLinks.classList.remove('open');
  }));
}

// ── THEME TOGGLE
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
const html = document.documentElement;
const savedTheme = localStorage.getItem('theme') || 'dark';
html.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);
if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const t = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', t);
    localStorage.setItem('theme', t);
    updateThemeIcon(t);
  });
}
function updateThemeIcon(t) { if (themeIcon) themeIcon.className = t === 'dark' ? 'fas fa-moon' : 'fas fa-sun'; }

// ── COUNTER ANIMATION
function animateCounter(el) {
  const target = parseFloat(el.dataset.target);
  const isDecimal = target % 1 !== 0;
  const duration = 2000;
  const start = performance.now();
  function step(ts) {
    const progress = Math.min((ts - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const val = target * eased;
    el.textContent = isDecimal ? val.toFixed(1) : Math.floor(val).toLocaleString();
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = isDecimal ? target.toFixed(1) : target.toLocaleString();
  }
  requestAnimationFrame(step);
}
const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { animateCounter(e.target); counterObserver.unobserve(e.target); }});
}, { threshold: 0.5 });
document.querySelectorAll('.counter[data-target]').forEach(el => counterObserver.observe(el));

// ── SKILL BARS
const barObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.style.width = e.target.dataset.width + '%'; barObserver.unobserve(e.target); }});
}, { threshold: 0.3 });
document.querySelectorAll('.skill-fill[data-width]').forEach(el => barObserver.observe(el));

// ── ACCORDION
document.querySelectorAll('.accordion-header').forEach(header => {
  header.addEventListener('click', () => {
    const body = header.nextElementSibling;
    const isOpen = body.classList.contains('open');
    document.querySelectorAll('.accordion-body').forEach(b => b.classList.remove('open'));
    document.querySelectorAll('.accordion-header').forEach(h => h.classList.remove('active'));
    if (!isOpen) { body.classList.add('open'); header.classList.add('active'); }
  });
});

// ── PORTFOLIO FILTER
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const filter = btn.dataset.filter;
    document.querySelectorAll('.portfolio-item').forEach(item => {
      const match = filter === 'all' || item.dataset.category === filter;
      item.style.display = match ? 'block' : 'none';
      if (match) item.style.animation = 'fadeInUp 0.4s ease forwards';
    });
  });
});

// ── SMOOTH SCROLL (same-page anchors only)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', e => {
    const id = anchor.getAttribute('href');
    if (id === '#') return;
    const target = document.querySelector(id);
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });
});

// Handle cross-page anchor links (e.g. /services#seo)
window.addEventListener('DOMContentLoaded', () => {
  if (window.location.hash) {
    setTimeout(() => {
      const target = document.querySelector(window.location.hash);
      if (target) { target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    }, 400);
  }
});

// ── FLASH AUTO-DISMISS
document.querySelectorAll('.flash').forEach(f => {
  setTimeout(() => f.style.opacity = '0', 4000);
  setTimeout(() => f.remove(), 4500);
});

// ── SCROLL PROGRESS BAR (optional)
const progressBar = document.createElement('div');
progressBar.style.cssText = 'position:fixed;top:0;left:0;height:3px;background:var(--orange);z-index:9999;transition:width 0.1s;width:0%;pointer-events:none;';
document.body.appendChild(progressBar);
window.addEventListener('scroll', () => {
  const pct = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
  progressBar.style.width = pct + '%';
});
