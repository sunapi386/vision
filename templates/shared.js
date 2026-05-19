// shared.js — theme toggle + nav scroll behavior, used by both index and book

// Theme
var toggle = document.getElementById('themeToggle');
var html = document.documentElement;
var saved = localStorage.getItem('theme');
if (saved) { html.setAttribute('data-theme', saved); }
else if (window.matchMedia('(prefers-color-scheme: light)').matches) { html.setAttribute('data-theme', 'light'); }
function updateIcon() { toggle.innerHTML = html.getAttribute('data-theme') === 'dark' ? '&#9788;' : '&#9790;'; }
updateIcon();
toggle.addEventListener('click', function() {
  var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  updateIcon();
});

// Nav scroll effect
var siteNav = document.getElementById('siteNav');
var lastScrollY = 0;
function updateNav() {
  var sy = window.scrollY;
  siteNav.classList.toggle('scrolled', sy > 60);
  lastScrollY = sy;
}
window.addEventListener('scroll', updateNav, { passive: true });
updateNav();

// Progress bar
var progress = document.getElementById('progress');
function updateProgress() {
  var sy = window.scrollY;
  var docH = document.documentElement.scrollHeight - window.innerHeight;
  if (docH > 0) progress.style.width = (sy / docH * 100) + '%';
}
window.addEventListener('scroll', updateProgress, { passive: true });
updateProgress();
