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
  let wheelBurst = false;
  let wheelReset = 0;
  let touchStartX = 0;
  let touchStartY = 0;

  const positionCounter = () => {
    const copy = frames[0].querySelector<HTMLElement>('.mission-reel-copy-main');
    if (!copy) return;
    counter.style.top = `${copy.getBoundingClientRect().top - stage.getBoundingClientRect().top + 5}px`;
  };

  const select = (index: number) => {
    const selected = Math.max(0, Math.min(frames.length - 1, index));
    const changed = selected !== active;
    active = selected;
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
    status.textContent = document.documentElement.lang === 'en'
      ? `Solution ${active + 1} of ${frames.length}`
      : `第 ${active + 1} 个方案，共 ${frames.length} 个`;
  };

  previous.forEach((button) => button.addEventListener('click', () => select(active - 1)));
  next.forEach((button) => button.addEventListener('click', () => select(active + 1)));

  root.addEventListener('wheel', (event) => {
    if (Math.abs(event.deltaY) <= Math.abs(event.deltaX)) return;
    const rect = root.getBoundingClientRect();
    const visibleHeight = Math.max(0, Math.min(rect.bottom, innerHeight) - Math.max(rect.top, 74));
    if (visibleHeight < rect.height * 0.65) return;
    const direction = Math.sign(event.deltaY);
    if ((direction < 0 && active === 0) || (direction > 0 && active === frames.length - 1)) return;
    event.preventDefault();
    window.clearTimeout(wheelReset);
    wheelReset = window.setTimeout(() => { wheelBurst = false; }, 220);
    if (wheelBurst) return;
    wheelBurst = true;
    select(active + direction);
  }, { passive: false });

  root.addEventListener('touchstart', (event) => {
    touchStartX = event.changedTouches[0]?.clientX ?? 0;
    touchStartY = event.changedTouches[0]?.clientY ?? 0;
  }, { passive: true });
  root.addEventListener('touchend', (event) => {
    const touch = event.changedTouches[0];
    if (!touch) return;
    const deltaX = touch.clientX - touchStartX;
    const deltaY = touch.clientY - touchStartY;
    if (Math.abs(deltaX) > 50 && Math.abs(deltaX) > Math.abs(deltaY) * 1.2) {
      select(active + (deltaX < 0 ? 1 : -1));
    }
  }, { passive: true });

  select(0);
  positionCounter();
  addEventListener('resize', positionCounter);
});
