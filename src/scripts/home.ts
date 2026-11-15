const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!reduceMotion) document.documentElement.classList.add('yh-motion-ready');

const hero = document.querySelector<HTMLElement>('[data-yh-hero]');
const heroVideo = hero?.querySelector<HTMLVideoElement>('[data-yh-hero-video]');
if (hero) {
  const showTitle = () => hero.classList.add('is-ready');
  if (reduceMotion || !heroVideo) {
    heroVideo?.pause();
    showTitle();
  } else {
    const started = () => {
      hero.classList.add('is-video-playing');
      showTitle();
    };
    heroVideo.addEventListener('playing', started, { once: true });
    heroVideo.addEventListener('error', showTitle, { once: true });
    if (!heroVideo.paused && heroVideo.currentTime > 0) started();
    else heroVideo.play().catch(showTitle);
    window.setTimeout(showTitle, 2000);
  }
}

const products = document.querySelector<HTMLElement>('.yh-products');
if (hero && products && !reduceMotion) {
  let queued = false;
  const updateTransition = () => {
    queued = false;
    const height = hero.offsetHeight;
    const progress = Math.min(1, Math.max(0, (window.scrollY - height * 0.24) / (height * 0.68)));
    hero.style.setProperty('--yh-hero-opacity', String(1 - progress * 0.94));
    products.style.setProperty('--yh-products-opacity', String(0.35 + progress * 0.65));
    products.style.setProperty('--yh-products-y', `${Math.round((1 - progress) * 64)}px`);
  };
  const schedule = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(updateTransition);
  };
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  updateTransition();
}

const productCarousel = document.querySelector<HTMLElement>('[data-yh-product-carousel]');
if (productCarousel) {
  const track = productCarousel.querySelector<HTMLElement>('[data-yh-product-track]');
  const slides = Array.from(productCarousel.querySelectorAll<HTMLElement>('[data-yh-product-slide]'));
  const selects = Array.from(productCarousel.querySelectorAll<HTMLButtonElement>('[data-yh-product-select]'));
  const dots = Array.from(productCarousel.querySelectorAll<HTMLButtonElement>('[data-yh-product-dot]'));
  const status = productCarousel.querySelector<HTMLElement>('[data-yh-product-status]');
  let selected = 0;
  let userScrolling = false;
  let scrollQueued = false;

  const selectProduct = (index: number, scroll = true) => {
    if (!track || !slides.length) return;
    selected = (index + slides.length) % slides.length;
    userScrolling = false;
    slides.forEach((slide, slideIndex) => slide.classList.toggle('is-selected', slideIndex === selected));
    selects.forEach((button, buttonIndex) => button.setAttribute('aria-pressed', String(buttonIndex === selected)));
    dots.forEach((dot, dotIndex) => {
      dot.classList.toggle('is-active', dotIndex === selected);
      dot.setAttribute('aria-pressed', String(dotIndex === selected));
    });
    if (status) status.textContent = `当前产品 ${slides[selected].querySelector('strong')?.textContent ?? ''}，第 ${selected + 1} 款，共 ${slides.length} 款`;
    if (!scroll) return;

    const firstLeft = slides[0].offsetLeft;
    const cardLeft = slides[selected].offsetLeft - firstLeft;
    const cardRight = cardLeft + slides[selected].offsetWidth;
    const edge = 10;
    let targetLeft = track.scrollLeft;
    if (cardLeft < track.scrollLeft + edge) targetLeft = cardLeft - edge;
    else if (cardRight > track.scrollLeft + track.clientWidth - edge) {
      targetLeft = cardRight - track.clientWidth + edge;
    }
    track.scrollTo({ left: Math.max(0, targetLeft), behavior: reduceMotion ? 'instant' : 'smooth' });
  };

  selects.forEach((button, index) => button.addEventListener('click', () => selectProduct(index)));
  dots.forEach((dot, index) => dot.addEventListener('click', () => selectProduct(index)));
  productCarousel.querySelector('[data-yh-product-prev]')?.addEventListener('click', () => selectProduct(selected - 1));
  productCarousel.querySelector('[data-yh-product-next]')?.addEventListener('click', () => selectProduct(selected + 1));
  track?.addEventListener('keydown', (event) => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    selectProduct(selected + (event.key === 'ArrowRight' ? 1 : -1));
  });
  track?.addEventListener('touchstart', () => { userScrolling = true; }, { passive: true });
  track?.addEventListener('wheel', (event) => {
    if (Math.abs(event.deltaX) > Math.abs(event.deltaY)) userScrolling = true;
  }, { passive: true });
  track?.addEventListener('scroll', () => {
    if (!userScrolling || scrollQueued || !track || !slides.length) return;
    scrollQueued = true;
    requestAnimationFrame(() => {
      scrollQueued = false;
      if (!userScrolling || !track) return;
      const firstLeft = slides[0].offsetLeft;
      const leadingEdge = track.scrollLeft + slides[0].offsetWidth * 0.5;
      let nearest = 0;
      let distance = Infinity;
      slides.forEach((slide, index) => {
        const nextDistance = Math.abs(slide.offsetLeft - firstLeft + slide.offsetWidth * 0.5 - leadingEdge);
        if (nextDistance < distance) {
          nearest = index;
          distance = nextDistance;
        }
      });
      selectProduct(nearest, false);
      userScrolling = true;
    });
  }, { passive: true });
  selectProduct(0, false);
}

const revealTargets = Array.from(document.querySelectorAll<HTMLElement>('[data-yh-reveal]'));
if (!reduceMotion && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.remove('yh-reveal-pending');
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: '0px 0px -30px 0px', threshold: 0.08 },
  );
  revealTargets.forEach((target) => {
    if (target.getBoundingClientRect().top < window.innerHeight * 0.84) return;
    target.classList.add('yh-reveal-pending');
    observer.observe(target);
  });
}

const insights = document.querySelector<HTMLElement>('[data-yh-insights]');
if (insights) {
  const cards = Array.from(insights.querySelectorAll<HTMLElement>('.yh-insight-card'));
  const status = insights.querySelector<HTMLElement>('[data-yh-insight-status]');
  let page = 0;
  const pageSize = 2;
  const pageCount = Math.max(1, Math.ceil(cards.length / pageSize));
  const show = (next: number) => {
    page = (next + pageCount) % pageCount;
    cards.forEach((card, index) => {
      card.hidden = Math.floor(index / pageSize) !== page;
      if (!card.hidden) card.classList.remove('yh-reveal-pending');
    });
    if (status) status.textContent = `第 ${page + 1} 组，共 ${pageCount} 组动态`;
  };
  insights.querySelector('[data-yh-insight-prev]')?.addEventListener('click', () => show(page - 1));
  insights.querySelector('[data-yh-insight-next]')?.addEventListener('click', () => show(page + 1));
  show(0);
}

const scenes = document.querySelector<HTMLElement>('[data-yh-scenes]');
if (scenes) {
  const buttons = Array.from(scenes.querySelectorAll<HTMLButtonElement>('[data-yh-scene-select]'));
  const image = scenes.querySelector<HTMLImageElement>('.yh-scene-stage img[data-yh-scene-image]');
  const copy = scenes.querySelector<HTMLElement>('.yh-scene-copy');
  const heading = scenes.querySelector<HTMLElement>('[data-yh-scene-heading]');
  const summary = copy?.querySelector<HTMLElement>('[data-yh-scene-summary]');
  const link = scenes.querySelector<HTMLAnchorElement>('[data-yh-scene-link]');
  const data = buttons.map((button) => ({
    title: button.dataset.yhSceneTitle ?? '',
    summary: button.dataset.yhSceneSummary ?? '',
    image: button.dataset.yhSceneImage ?? '',
    imageAlt: button.dataset.yhSceneImageAlt ?? '',
    url: button.dataset.yhSceneUrl ?? '/solutions/',
  }));
  let current = 0;
  let token = 0;
  let timer = 0;
  let visible = false;
  const stopTimer = () => window.clearTimeout(timer);
  const startTimer = () => {
    stopTimer();
    if (!visible || reduceMotion || document.hidden || data.length < 2) return;
    timer = window.setTimeout(() => void changeScene(current + 1), 5800);
  };
  const changeScene = async (index: number) => {
    if (!data.length) return;
    stopTimer();
    const next = (index + data.length) % data.length;
    const thisToken = ++token;
    if (next === current) {
      startTimer();
      return;
    }
    const nextImage = new Image();
    nextImage.src = data[next].image;
    try {
      await nextImage.decode();
    } catch {
      startTimer();
      return;
    }
    if (thisToken !== token) return;
    image?.classList.add('is-changing');
    copy?.classList.add('is-changing');
    await new Promise((resolve) => window.setTimeout(resolve, reduceMotion ? 0 : 260));
    if (thisToken !== token) return;
    current = next;
    if (image) {
      image.src = data[current].image;
      image.alt = data[current].imageAlt;
      image.classList.remove('is-changing');
    }
    if (heading) heading.textContent = data[current].title;
    if (summary) summary.textContent = data[current].summary;
    if (link) link.href = data[current].url;
    copy?.classList.remove('is-changing');
    buttons.forEach((button, buttonIndex) => {
      const active = buttonIndex === current;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    startTimer();
  };
  buttons.forEach((button, index) => button.addEventListener('click', () => void changeScene(index)));
  scenes.querySelector('[data-yh-scene-prev]')?.addEventListener('click', () => void changeScene(current - 1));
  scenes.querySelector('[data-yh-scene-next]')?.addEventListener('click', () => void changeScene(current + 1));
  if ('IntersectionObserver' in window) {
    new IntersectionObserver((entries) => {
      visible = entries[0].isIntersecting;
      if (visible) startTimer();
      else stopTimer();
    }, { threshold: 0.25 }).observe(scenes);
  } else {
    visible = true;
    startTimer();
  }
  document.addEventListener('visibilitychange', startTimer);
}
