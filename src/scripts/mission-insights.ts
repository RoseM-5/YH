document.querySelectorAll<HTMLElement>('[data-mission-insights]').forEach((root) => {
  const track = root.querySelector<HTMLElement>('[data-insights-track]');
  const cards = Array.from(root.querySelectorAll<HTMLElement>('[data-insights-card]'));
  const previous = root.querySelector<HTMLButtonElement>('[data-insights-prev]');
  const next = root.querySelector<HTMLButtonElement>('[data-insights-next]');
  const progress = root.querySelector<HTMLElement>('[data-insights-progress]');
  if (!track || !cards.length || !previous || !next || !progress) return;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let active = 0;
  let frame = 0;

  const update = () => {
    frame = 0;
    active = cards.reduce((nearest, card, index) =>
      Math.abs(card.offsetLeft - track.offsetLeft - track.scrollLeft) <
      Math.abs(cards[nearest].offsetLeft - track.offsetLeft - track.scrollLeft)
        ? index : nearest, 0);
    const maxScroll = Math.max(0, track.scrollWidth - track.clientWidth);
    previous.disabled = track.scrollLeft <= 2;
    next.disabled = track.scrollLeft >= maxScroll - 2;
    progress.style.width = `${maxScroll ? 20 + (track.scrollLeft / maxScroll) * 80 : 100}%`;
  };
  const goTo = (index: number) => {
    const target = Math.max(0, Math.min(cards.length - 1, index));
    track.scrollTo({
      left: cards[target].offsetLeft - track.offsetLeft,
      behavior: reducedMotion.matches ? 'instant' : 'smooth',
    });
  };
  previous.addEventListener('click', () => goTo(active - 1));
  next.addEventListener('click', () => goTo(active + 1));
  track.addEventListener('scroll', () => {
    if (!frame) frame = requestAnimationFrame(update);
  }, { passive: true });
  track.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      goTo(active + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  update();
});
