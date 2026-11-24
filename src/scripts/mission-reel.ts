import { solutionStatus } from './ui-locale';

document.querySelectorAll<HTMLElement>('[data-mission-reel]').forEach((root) => {
  const frames = Array.from(root.querySelectorAll<HTMLElement>('[data-reel-frame]'));
  const stage = root.querySelector<HTMLElement>('.mission-reel-stage');
  const counter = root.querySelector<HTMLElement>('.mission-reel-fixed-number');
  const currentNumber = root.querySelector<HTMLElement>('[data-reel-current]');
  const fill = root.querySelector<HTMLElement>('[data-reel-fill]');
  const dot = root.querySelector<HTMLElement>('[data-reel-dot]');
  const previous = Array.from(root.querySelectorAll<HTMLButtonElement>('[data-reel-prev]'));
  const next = Array.from(root.querySelectorAll<HTMLButtonElement>('[data-reel-next]'));
  const status = root.querySelector<HTMLElement>('[data-reel-status]');
  if (!frames.length || !stage || !counter || !currentNumber || !fill || !dot || !previous.length || !next.length || !status) return;

  root.classList.add('is-enhanced');
  let active = 0;
  let hasSelected = false;
  let lastScrollY = window.scrollY;
  let wheelCooldownUntil = 0;

  const positionCounter = () => {
    const copy = frames[0].querySelector<HTMLElement>('.mission-reel-copy-main');
    if (!copy) return;
    counter.style.top = `${copy.getBoundingClientRect().top - stage.getBoundingClientRect().top + 5}px`;
  };

  const select = (index: number) => {
    const selected = Math.max(0, Math.min(frames.length - 1, index));
    if (selected === active && hasSelected) return;
    const changed = selected !== active;
    active = selected;
    hasSelected = true;
    frames.forEach((frame, index) => {
      frame.classList.toggle('is-active', index === active);
      frame.classList.toggle('is-before', index < active);
      frame.classList.toggle('is-after', index > active);
      frame.setAttribute('aria-hidden', String(index !== active));
      frame.inert = index !== active;
    });
    const progress = frames.length > 1 ? active / (frames.length - 1) : 0;
    fill.style.height = `${progress * 100}%`;
    dot.style.top = `${progress * 100}%`;
    if (changed) {
      currentNumber.textContent = String(active + 1).padStart(2, '0');
      currentNumber.classList.remove('is-changing');
      void currentNumber.offsetWidth;
      currentNumber.classList.add('is-changing');
    }
    previous.forEach((button) => { button.disabled = active === 0; });
    next.forEach((button) => { button.disabled = active === frames.length - 1; });
    status.textContent = solutionStatus(active + 1, frames.length);
  };

  const reelStart = () => {
    const stickyTop = Number.parseFloat(getComputedStyle(stage).top) || 0;
    return root.getBoundingClientRect().top + window.scrollY - stickyTop;
  };

  const syncToScroll = () => {
    const step = stage.offsetHeight;
    if (!step) return;
    const start = reelStart();
    const end = start + frames.length * step;
    const current = window.scrollY;
    const index = Math.max(0, Math.min(frames.length - 1, Math.floor((current - start) / step + 0.5)));
    let limitedIndex: number | null = null;

    if (lastScrollY < start && current >= start && index > 0) {
      limitedIndex = 0;
    } else if (lastScrollY > end && current <= end && index < frames.length - 1) {
      limitedIndex = frames.length - 1;
    } else if (current > lastScrollY && (index > active + 1 || (current >= end && active < frames.length - 1))) {
      limitedIndex = Math.min(active + 1, frames.length - 1);
    } else if (current < lastScrollY && (index < active - 1 || (current < start && active > 0))) {
      limitedIndex = Math.max(active - 1, 0);
    }

    if (limitedIndex !== null) {
      window.scrollTo({ top: start + limitedIndex * step, behavior: 'instant' });
      select(limitedIndex);
    } else {
      select(index);
    }
    lastScrollY = window.scrollY;
  };

  const scrollToFrame = (index: number) => {
    const selected = Math.max(0, Math.min(frames.length - 1, index));
    window.scrollTo({
      top: reelStart() + selected * stage.offsetHeight,
      behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
    });
  };

  previous.forEach((button) => button.addEventListener('click', () => scrollToFrame(active - 1)));
  next.forEach((button) => button.addEventListener('click', () => scrollToFrame(active + 1)));

  addEventListener('wheel', (event) => {
    if (Math.abs(event.deltaY) <= Math.abs(event.deltaX)) return;
    const rect = root.getBoundingClientRect();
    const stickyTop = Number.parseFloat(getComputedStyle(stage).top) || 0;
    const entering = event.deltaY > 0 && rect.top > stickyTop && rect.top < innerHeight * 0.75;
    const pinned = rect.top <= stickyTop + 2 && rect.bottom > innerHeight;
    if (!entering && !pinned) return;

    const now = performance.now();
    if (entering) {
      event.preventDefault();
      if (now < wheelCooldownUntil) return;
      wheelCooldownUntil = now + 650;
      scrollToFrame(0);
      return;
    }

    const direction = Math.sign(event.deltaY);
    if ((direction < 0 && active === 0) || (direction > 0 && active === frames.length - 1)) {
      if (now < wheelCooldownUntil) event.preventDefault();
      return;
    }
    event.preventDefault();
    if (now < wheelCooldownUntil) return;
    wheelCooldownUntil = now + 650;
    scrollToFrame(active + direction);
  }, { passive: false });

  const updateGeometry = () => {
    // The extra stage height lets the final frame remain visible before the footer enters.
    root.style.height = `${stage.offsetHeight * (frames.length + 1)}px`;
    positionCounter();
    lastScrollY = window.scrollY;
    syncToScroll();
  };

  updateGeometry();
  addEventListener('scroll', syncToScroll, { passive: true });
  addEventListener('resize', updateGeometry);
});
