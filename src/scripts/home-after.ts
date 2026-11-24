import { updatesStatus } from './ui-locale';

const reducedAfterMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const taskShowcase = document.querySelector<HTMLElement>('[data-yh-task-showcase]');
if (taskShowcase) {
  const stage = taskShowcase.querySelector<HTMLElement>('[data-yh-task-stage]');
  const tabs = Array.from(taskShowcase.querySelectorAll<HTMLButtonElement>('[data-yh-task-tab]'));
  const stories = Array.from(taskShowcase.querySelectorAll<HTMLElement>('[data-yh-task-story]'));
  const images = Array.from(taskShowcase.querySelectorAll<HTMLImageElement>('[data-yh-task-image]'));
  const label = taskShowcase.querySelector<HTMLElement>('[data-yh-task-label]');
  const progress = taskShowcase.querySelector<HTMLElement>('[data-yh-task-progress]');
  let active = 0;
  let visible = false;
  let paused = false;
  let timer = 0;

  const stop = () => window.clearTimeout(timer);
  const schedule = () => {
    stop();
    if (progress) {
      progress.style.animation = 'none';
      void progress.offsetWidth;
      progress.style.animation = '';
      progress.style.animationPlayState = visible && !paused ? 'running' : 'paused';
    }
    if (!visible || paused || reducedAfterMotion || document.hidden || tabs.length < 2) return;
    timer = window.setTimeout(() => select((active + 1) % tabs.length), 5800);
  };
  const select = (index: number, focus = false) => {
    active = (index + tabs.length) % tabs.length;
    tabs.forEach((tab, itemIndex) => {
      const selected = itemIndex === active;
      tab.classList.toggle('is-active', selected);
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      if (selected && focus) tab.focus();
    });
    stories.forEach((story, itemIndex) => {
      const selected = itemIndex === active;
      story.classList.toggle('is-active', selected);
      story.setAttribute('aria-hidden', String(!selected));
      const link = story.querySelector('a');
      if (link) link.tabIndex = selected ? 0 : -1;
    });
    images.forEach((image, itemIndex) => image.classList.toggle('is-active', itemIndex === active));
    if (label) label.textContent = tabs[active]?.dataset.yhTaskLabel ?? '';
    schedule();
  };

  tabs.forEach((tab, index) => tab.addEventListener('click', () => select(index)));
  taskShowcase.querySelector('.yh-task-tabs')?.addEventListener('keydown', (event) => {
    if (!(event instanceof KeyboardEvent)) return;
    const step = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0;
    if (!step && event.key !== 'Home' && event.key !== 'End') return;
    event.preventDefault();
    select(event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : active + step, true);
  });
  taskShowcase.addEventListener('pointerenter', () => { paused = true; schedule(); });
  taskShowcase.addEventListener('pointerleave', () => { paused = false; schedule(); });
  taskShowcase.addEventListener('focusin', () => { paused = true; schedule(); });
  taskShowcase.addEventListener('focusout', (event) => {
    if (taskShowcase.contains(event.relatedTarget as Node | null)) return;
    paused = false;
    schedule();
  });
  document.addEventListener('visibilitychange', schedule);
  if (stage && 'IntersectionObserver' in window) {
    new IntersectionObserver((entries) => {
      visible = entries[0].isIntersecting;
      if (visible) {
        stage.classList.add('is-visible');
        taskShowcase.classList.add('is-visible');
      }
      schedule();
    }, { threshold: 0.22 }).observe(stage);
  } else {
    visible = true;
    stage?.classList.add('is-visible');
    taskShowcase.classList.add('is-visible');
    schedule();
  }
}

const latest = document.querySelector<HTMLElement>('[data-yh-latest]');
if (latest) {
  const grid = latest.querySelector<HTMLElement>('[data-yh-latest-grid]');
  const cards = Array.from(latest.querySelectorAll<HTMLAnchorElement>('[data-yh-latest-card]'));
  const status = latest.querySelector<HTMLElement>('[data-yh-latest-status]');
  let start = 0;
  let touchX = 0;
  let touchY = 0;
  const visibleCount = () => window.innerWidth <= 700 ? 1 : window.innerWidth <= 900 ? 2 : 3;
  const paint = (animate = true) => {
    const count = Math.min(visibleCount(), cards.length);
    const visibleIndices = Array.from({ length: count }, (_, offset) => (start + offset) % cards.length);
    cards.forEach((card, index) => {
      const position = visibleIndices.indexOf(index);
      card.hidden = position < 0;
      card.style.order = String(position);
      card.tabIndex = position < 0 ? -1 : 0;
      card.classList.remove('is-entering');
    });
    if (animate && !reducedAfterMotion && grid) {
      void grid.offsetWidth;
      visibleIndices.forEach((index) => cards[index].classList.add('is-entering'));
    }
    if (status) status.textContent = updatesStatus(start + 1, count, cards.length);
  };
  const step = (direction: number) => {
    start = (start + direction + cards.length) % cards.length;
    paint();
  };
  latest.querySelector('[data-yh-latest-prev]')?.addEventListener('click', () => step(-1));
  latest.querySelector('[data-yh-latest-next]')?.addEventListener('click', () => step(1));
  grid?.addEventListener('keydown', (event) => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    step(event.key === 'ArrowRight' ? 1 : -1);
  });
  grid?.addEventListener('touchstart', (event) => {
    touchX = event.changedTouches[0].clientX;
    touchY = event.changedTouches[0].clientY;
  }, { passive: true });
  grid?.addEventListener('touchend', (event) => {
    const dx = event.changedTouches[0].clientX - touchX;
    const dy = event.changedTouches[0].clientY - touchY;
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) step(dx < 0 ? 1 : -1);
  }, { passive: true });
  window.addEventListener('resize', () => paint(false));
  paint(false);
}

const closing = document.querySelector<HTMLElement>('[data-yh-closing]');
const closingTiles = Array.from(closing?.querySelectorAll<HTMLElement>('[data-yh-closing-tile]') ?? []);
if (!reducedAfterMotion) document.documentElement.classList.add('yh-after-motion');

if ('IntersectionObserver' in window) {
  const reveal = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      reveal.unobserve(entry.target);
    });
  }, { threshold: 0.12 });
  if (latest) reveal.observe(latest);
  const tileReveal = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      tileReveal.unobserve(entry.target);
    });
  }, { threshold: 0.12 });
  closingTiles.forEach((tile) => tileReveal.observe(tile));
} else {
  latest?.classList.add('is-visible');
  closingTiles.forEach((tile) => tile.classList.add('is-visible'));
}
