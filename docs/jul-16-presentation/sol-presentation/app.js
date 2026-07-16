(() => {
  const slides = [...document.querySelectorAll('.slide')];
  const mainSlides = slides.filter(slide => !slide.classList.contains('backup'));
  const backupSlides = slides.filter(slide => slide.classList.contains('backup'));
  const progress = document.getElementById('progress-fill');
  const counter = document.getElementById('counter');
  const sectionLabel = document.getElementById('section-label');
  const notesPanel = document.getElementById('notes-panel');
  const notesContent = document.getElementById('notes-content');
  const notesTime = document.getElementById('notes-time');
  const revealAll = new URLSearchParams(location.search).has('all');
  let current = 0;

  const pad = n => String(n).padStart(2, '0');
  const buildsFor = slide => [...slide.querySelectorAll('[data-build]')];

  function hashIndex() {
    const raw = location.hash.replace('#', '');
    if (!raw) return 0;
    if (/^b\d+$/i.test(raw)) return mainSlides.length + Number(raw.slice(1)) - 1;
    const parsed = Number(raw);
    return Number.isFinite(parsed) ? parsed - 1 : 0;
  }

  function updateHash(index) {
    const hash = index < mainSlides.length ? `#${index + 1}` : `#b${index - mainSlides.length + 1}`;
    history.replaceState(null, '', hash);
  }

  function updateNotes() {
    const slide = slides[current];
    const source = slide.querySelector('.notes');
    notesContent.textContent = source ? source.textContent.trim() : 'No notes for this slide.';
    const seconds = Number(slide.dataset.duration || 0);
    notesTime.textContent = seconds ? `${Math.floor(seconds / 60)}:${pad(seconds % 60)}` : 'backup';
  }

  function show(index, { preserveBuilds = false } = {}) {
    current = Math.max(0, Math.min(index, slides.length - 1));
    slides.forEach((slide, i) => {
      slide.classList.toggle('active', i === current);
      slide.classList.toggle('previous', i < current);
      if (i === current && !preserveBuilds) {
        buildsFor(slide).forEach(el => el.classList.toggle('revealed', revealAll));
      }
    });

    const inMain = current < mainSlides.length;
    if (inMain) {
      counter.textContent = `${pad(current + 1)} / ${mainSlides.length}`;
      progress.style.width = `${((current + 1) / mainSlides.length) * 100}%`;
    } else {
      counter.textContent = `B${current - mainSlides.length + 1} / ${backupSlides.length}`;
      progress.style.width = '100%';
    }
    sectionLabel.textContent = slides[current].dataset.section || '';
    updateHash(current);
    updateNotes();
  }

  function next() {
    const builds = buildsFor(slides[current]);
    const nextBuild = builds.find(el => !el.classList.contains('revealed'));
    if (nextBuild) {
      nextBuild.classList.add('revealed');
      return;
    }
    if (current < slides.length - 1) show(current + 1);
  }

  function previous() {
    const builds = buildsFor(slides[current]);
    const revealed = builds.filter(el => el.classList.contains('revealed'));
    if (revealed.length) {
      revealed.at(-1).classList.remove('revealed');
      return;
    }
    if (current > 0) {
      show(current - 1);
      buildsFor(slides[current]).forEach(el => el.classList.add('revealed'));
    }
  }

  function toggleNotes(force) {
    const open = typeof force === 'boolean' ? force : !notesPanel.classList.contains('open');
    notesPanel.classList.toggle('open', open);
  }

  function fullscreen() {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen?.();
    else document.exitFullscreen?.();
  }

  document.addEventListener('keydown', event => {
    if (['ArrowRight', 'PageDown', 'Enter'].includes(event.key) || event.code === 'Space') {
      event.preventDefault(); next();
    } else if (['ArrowLeft', 'PageUp', 'Backspace'].includes(event.key)) {
      event.preventDefault(); previous();
    } else if (event.key === 'Home') {
      event.preventDefault(); show(0);
    } else if (event.key === 'End') {
      event.preventDefault(); show(mainSlides.length - 1);
    } else if (event.key.toLowerCase() === 'n') {
      toggleNotes();
    } else if (event.key.toLowerCase() === 'f') {
      fullscreen();
    } else if (event.key.toLowerCase() === 'p') {
      window.print();
    } else if (event.key === 'Escape') {
      toggleNotes(false);
    }
  });

  document.getElementById('next').addEventListener('click', next);
  document.getElementById('prev').addEventListener('click', previous);
  document.getElementById('notes-toggle').addEventListener('click', () => toggleNotes());
  document.getElementById('fullscreen').addEventListener('click', fullscreen);
  document.getElementById('deck').addEventListener('click', event => {
    if (event.target.closest('button, a')) return;
    if (event.clientX < window.innerWidth * .22) previous(); else next();
  });
  window.addEventListener('hashchange', () => show(hashIndex()));

  show(hashIndex());
})();
