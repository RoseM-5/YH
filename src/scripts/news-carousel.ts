const carousel = document.querySelector<HTMLElement>('[data-news-carousel]');
if (carousel) {
  const track = carousel.querySelector<HTMLElement>('[data-news-track]');
  const slides = Array.from(carousel.querySelectorAll<HTMLElement>('[data-news-slide]'));
  const previous = carousel.querySelector<HTMLButtonElement>('[data-news-prev]');
  const next = carousel.querySelector<HTMLButtonElement>('[data-news-next]');
  const count = carousel.querySelector<HTMLOutputElement>('[data-news-count]');
  const progress = carousel.querySelector<HTMLElement>('[data-news-progress]');
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let current = 0;
  let queued = false;

  const visibleCards = () => matchMedia('(max-width: 700px)').matches ? 1 : matchMedia('(max-width: 1020px)').matches ? 2 : 3;
  const maxIndex = () => Math.max(0, slides.length - visibleCards());
  const render = () => {
    const pages = maxIndex() + 1;
    if (count) count.textContent = `${String(current + 1).padStart(2, '0')} / ${String(pages).padStart(2, '0')}`;
    if (progress) progress.style.width = `${((current + 1) / pages) * 100}%`;
    if (previous) previous.disabled = current === 0;
    if (next) next.disabled = current === maxIndex();
  };
  const update = () => {
    if (!track || !slides.length) return;
    const step = slides[1] ? slides[1].offsetLeft - slides[0].offsetLeft : slides[0].offsetWidth;
    current = Math.min(maxIndex(), Math.max(0, Math.round(track.scrollLeft / step)));
    render();
  };
  const goTo = (index: number) => {
    if (!track || !slides.length) return;
    current = Math.min(maxIndex(), Math.max(0, index));
    render();
    track.scrollTo({
      left: slides[current].offsetLeft - slides[0].offsetLeft,
      behavior: reduceMotion ? 'auto' : 'smooth',
    });
  };
  previous?.addEventListener('click', () => goTo(current - 1));
  next?.addEventListener('click', () => goTo(current + 1));
  track?.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight') {
      event.preventDefault();
      goTo(current + 1);
    } else if (event.key === 'ArrowLeft') {
      event.preventDefault();
      goTo(current - 1);
    }
  });
  track?.addEventListener('scroll', () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => {
      queued = false;
      update();
    });
  }, { passive: true });
  window.addEventListener('resize', () => goTo(current));
  update();
}
