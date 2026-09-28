// Shared by index.html (20-minute version) and long.html (full version).
// Beamer-like footline: author | title | venue + frame number (appendix frames are numbered A1, A2…)
const FOOT_A = 'M. Acher (INSA Rennes · IRISA · Inria)';
const FOOT_B = 'Towards an Encyclopedia of Programming Languages';
const FOOT_C = 'CodeCommons plenary · 28 Sept. 2026';

function addFootlines() {
  const slides = Reveal.getSlides();
  const backupStart = slides.findIndex(s => s.classList.contains('backup-start'));
  const nMain = backupStart >= 0 ? backupStart : slides.length;
  slides.forEach((s, i) => {
    if (s.classList.contains('titlepage') || s.querySelector(':scope > .footline')) return;
    const num = i < nMain ? `${i + 1} / ${nMain}` : (i === backupStart ? 'Appendix' : `A${i - backupStart}`);
    const f = document.createElement('div');
    f.className = 'footline';
    f.innerHTML = `<span class="fl-a">${FOOT_A}</span><span class="fl-b">${FOOT_B}</span>` +
                  `<span class="fl-c"><span>${FOOT_C}</span><span>${num}</span></span>`;
    s.appendChild(f);
  });
}

// Inline the SVG diagrams (img[data-inline]) so that they use the page fonts (Latin Modern)
function inlineSvgs() {
  document.querySelectorAll('.reveal img[data-inline]').forEach(img => {
    fetch(img.getAttribute('src')).then(r => r.text()).then(txt => {
      const box = document.createElement('div');
      box.innerHTML = txt;
      const svg = box.querySelector('svg');
      if (!svg) return;
      svg.classList.add('inline-svg');
      if (img.className) img.className.split(' ').forEach(c => c && svg.classList.add(c));
      if (img.getAttribute('style')) svg.setAttribute('style', img.getAttribute('style'));
      svg.setAttribute('role', 'img');
      svg.setAttribute('aria-label', img.alt || '');
      img.replaceWith(svg);
    }).catch(() => { /* file:// or offline: keep the <img> */ });
  });
}

Reveal.initialize({
  hash: true,
  slideNumber: false,
  controls: false,
  progress: false,
  center: false,
  display: 'flex',
  transition: 'none',
  width: 1280,
  height: 720,
  margin: 0,
  pdfSeparateFragments: false,
  plugins: [ RevealMarkdown, RevealHighlight, RevealNotes, RevealZoom ]
}).then(() => { addFootlines(); inlineSvgs(); });
