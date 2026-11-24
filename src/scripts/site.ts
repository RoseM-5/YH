import { ui } from './ui-locale';

const header = document.querySelector<HTMLElement>('#site-header');
const updateHeader = () => header?.classList.toggle('is-scrolled', window.scrollY > 40);
updateHeader();
window.addEventListener('scroll', updateHeader, { passive: true });

const mobileButton = document.querySelector<HTMLButtonElement>('[data-menu-toggle]');
const mobileNav = document.querySelector<HTMLElement>('#mobile-nav');
const closeMobile = () => {
  if (!mobileButton || !mobileNav) return;
  mobileNav.hidden = true;
  mobileButton.setAttribute('aria-expanded', 'false');
  mobileButton.setAttribute('aria-label', ui.openMenu);
  document.body.classList.remove('mobile-open');
};
mobileButton?.addEventListener('click', () => {
  if (!mobileNav || !mobileButton) return;
  const open = mobileNav.hidden === true;
  mobileNav.hidden = !open;
  mobileButton.setAttribute('aria-expanded', String(open));
  mobileButton.setAttribute('aria-label', open ? ui.closeMenu : ui.openMenu);
  document.body.classList.toggle('mobile-open', open);
});
mobileNav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMobile));
window.addEventListener('resize', () => {
  if (window.innerWidth > 960) closeMobile();
});

const productMenu = document.querySelector<HTMLDetailsElement>('#product-menu');
const hoverMenu = window.matchMedia('(hover: hover) and (min-width: 961px)');
productMenu?.querySelector('summary')?.addEventListener('click', (event) => {
  if (hoverMenu.matches && (event as MouseEvent).detail > 0) {
    event.preventDefault();
    productMenu.open = true;
  }
});
productMenu?.addEventListener('mouseenter', () => {
  if (hoverMenu.matches) productMenu.open = true;
});
productMenu?.addEventListener('mouseleave', () => {
  if (hoverMenu.matches) productMenu.open = false;
});
const preview = productMenu?.querySelector<HTMLImageElement>('[data-mega-preview]');
const previewCaption = productMenu?.querySelector<HTMLElement>('[data-mega-caption]');
productMenu?.querySelectorAll<HTMLAnchorElement>('[data-mega-image]').forEach((link) => {
  const update = () => {
    if (!preview) return;
    const next = link.dataset.megaImage;
    if (!next || preview.src.endsWith(next)) return;
    preview.classList.add('is-swapping');
    const probe = new Image();
    probe.onload = () => {
      preview.src = next;
      preview.alt = link.dataset.megaAlt ?? '';
      if (previewCaption) previewCaption.textContent = link.dataset.megaName ?? '';
      requestAnimationFrame(() => preview.classList.remove('is-swapping'));
    };
    probe.src = next;
  };
  link.addEventListener('mouseenter', update);
  link.addEventListener('focus', update);
});
document.addEventListener('click', (event) => {
  if (productMenu && !productMenu.contains(event.target as Node)) productMenu.open = false;
});

const languageMenu = document.querySelector<HTMLDetailsElement>('[data-language-menu]');
document.addEventListener('click', (event) => {
  if (languageMenu && !languageMenu.contains(event.target as Node)) languageMenu.open = false;
});

if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const targets = document.querySelectorAll<HTMLElement>('[data-reveal]');
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.09, rootMargin: '0px 0px -35px 0px' },
  );
  targets.forEach((target, index) => {
    if (target.getBoundingClientRect().top <= innerHeight * 0.88) return;
    target.classList.add('reveal-ready');
    target.style.setProperty('--reveal-delay', `${(index % 3) * 70}ms`);
    observer.observe(target);
  });
}

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    closeMobile();
    if (languageMenu) languageMenu.open = false;
  }
});
