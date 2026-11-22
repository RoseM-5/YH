const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const heroEnglish = document.documentElement.lang === 'en';
if (!reduceMotion) document.documentElement.classList.add('yh-motion-ready');

const hero = document.querySelector<HTMLElement>('[data-yh-hero]');
const heroVideo = hero?.querySelector<HTMLVideoElement>('[data-yh-hero-video]');
const soundButton = hero?.querySelector<HTMLButtonElement>('[data-yh-sound]');
if (hero) {
  const showTitle = () => hero.classList.add('is-ready');
  if (reduceMotion || !heroVideo) {
    heroVideo?.pause();
    showTitle();
  } else {
    const syncSoundButton = () => {
      if (!soundButton) return;
      const audible = !heroVideo.muted;
      soundButton.setAttribute('aria-pressed', String(audible));
      soundButton.setAttribute('aria-label', heroEnglish ? (audible ? 'Mute video' : 'Turn on video sound') : (audible ? '静音视频' : '开启视频声音'));
      const label = soundButton.querySelector<HTMLElement>('[data-yh-sound-label]');
      if (label) label.textContent = heroEnglish ? (audible ? 'Mute' : 'Sound on') : (audible ? '静音' : '开启声音');
    };
    const started = () => {
      hero.classList.add('is-video-playing');
      if (soundButton) soundButton.hidden = false;
      showTitle();
    };
    soundButton?.addEventListener('click', async () => {
      heroVideo.muted = !heroVideo.muted;
      if (!heroVideo.muted) {
        heroVideo.volume = 1;
        try {
          await heroVideo.play();
        } catch {
          heroVideo.muted = true;
        }
      }
      syncSoundButton();
    });
    heroVideo.addEventListener('volumechange', syncSoundButton);
    syncSoundButton();
    heroVideo.addEventListener('playing', started, { once: true });
    heroVideo.addEventListener('error', showTitle, { once: true });
    if (!heroVideo.paused && heroVideo.currentTime > 0) started();
    else heroVideo.play().catch(showTitle);
    window.setTimeout(showTitle, 2000);
  }
}

const homeClosing = document.querySelector<HTMLElement>('[data-yh-closing]');
if (hero && homeClosing && !reduceMotion) {
  let queued = false;
  const updateTransition = () => {
    queued = false;
    const height = hero.offsetHeight;
    const progress = Math.min(1, Math.max(0, (window.scrollY - height * 0.24) / (height * 0.68)));
    hero.style.setProperty('--yh-hero-opacity', String(1 - progress * 0.94));
    homeClosing.style.setProperty('--yh-closing-opacity', String(0.4 + progress * 0.6));
    homeClosing.style.setProperty('--yh-closing-y', `${Math.round((1 - progress) * 52)}px`);
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

const revealTargets = Array.from(document.querySelectorAll<HTMLElement>('[data-yh-reveal]'));
if (!reduceMotion && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.remove('yh-reveal-pending');
      observer.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -30px 0px', threshold: 0.08 });
  revealTargets.forEach((target) => {
    if (target.getBoundingClientRect().top < window.innerHeight * 0.84) return;
    target.classList.add('yh-reveal-pending');
    observer.observe(target);
  });
}
