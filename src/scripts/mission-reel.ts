document.querySelectorAll<HTMLElement>('[data-mission-reel]').forEach((root) => {
  const frames = Array.from(root.querySelectorAll<HTMLElement>('[data-reel-frame]'));
  const fill = root.querySelector<HTMLElement>('[data-reel-fill]');
  const dot = root.querySelector<HTMLElement>('[data-reel-dot]');
  const count = root.querySelector<HTMLElement>('[data-reel-count]');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  if (!frames.length || !fill || !dot || !count || reducedMotion.matches) return;

  root.classList.add('is-enhanced');
  let pending = false;
  const update = () => {
    pending = false;
    const rect = root.getBoundingClientRect();
    const travel = Math.max(1, root.offsetHeight - window.innerHeight);
    const progress = Math.max(0, Math.min(1, -rect.top / travel));
    const position = progress * (frames.length - 1);
    const step = Math.min(window.innerHeight * 0.78, 650);
    const active = Math.min(frames.length - 1, Math.floor(position + 0.5));
    frames.forEach((frame, index) => {
      const distance = index - position;
      frame.style.transform = `translate3d(0, ${distance * step}px, 0)`;
      frame.style.opacity = String(Math.max(0, 1 - Math.abs(distance) * 0.76));
      frame.style.visibility = Math.abs(distance) > 1.3 ? 'hidden' : 'visible';
      frame.inert = index !== active;
    });
    fill.style.height = `${progress * 100}%`;
    dot.style.top = `${progress * 100}%`;
    count.textContent = String(active + 1).padStart(2, '0');
  };
  const queue = () => {
    if (!pending) {
      pending = true;
      requestAnimationFrame(update);
    }
  };
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', queue);
  update();
});
