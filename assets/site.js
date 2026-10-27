// Content and navigation work without JavaScript. This only adds the hero motion, the
// screenshot viewer and legal pages; no analytics or third-party code is loaded.
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
const pointer = { x: 0, y: 0 };
addEventListener('pointermove', event => {
  pointer.x = event.clientX / innerWidth - .5;
  pointer.y = event.clientY / innerHeight - .5;
}, { passive: true });

// Home: app icons drift at their depth, lean away from the pointer and fly outwards on scroll.
const field = document.querySelector('.icon-field');
if (field && !calm) {
  const icons = [...field.children].map((el, i) => ({
    el, d: parseFloat(el.style.getPropertyValue('--d')), phase: i * 1.7,
    ox: parseFloat(el.style.getPropertyValue('--x')) / 50 - 1, oy: parseFloat(el.style.getPropertyValue('--y')) / 50 - 1
  }));
  let px = 0, py = 0, running = false;
  const frame = time => {
    if (!running) return;
    px += (pointer.x - px) * .05; py += (pointer.y - py) * .05;
    const s = Math.min(scrollY / innerHeight, 1);
    for (const icon of icons) {
      const k = icon.d, a = time / 1000 * .3 + icon.phase;
      const x = Math.sin(a) * 12 * k - px * 70 * k + icon.ox * s * 260 * k;
      const y = Math.cos(a * .8) * 12 * k - py * 70 * k + icon.oy * s * 260 * k - s * 140 * k;
      icon.el.style.transform = `translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0) scale(${(1 + s * .7 * k).toFixed(3)})`;
    }
    field.style.opacity = (1 - s * .85).toFixed(3);
    requestAnimationFrame(frame);
  };
  new IntersectionObserver(([entry]) => {
    const was = running; running = entry.isIntersecting;
    if (running && !was) requestAnimationFrame(frame);
  }).observe(field);
}

// Product pages: the app-coloured light follows the pointer across the header.
const head = document.querySelector('.product-head');
const glow = head?.querySelector('.glow');
if (glow && !calm) head.addEventListener('pointermove', event => {
  const box = head.getBoundingClientRect();
  glow.style.setProperty('--gx', `${event.clientX - box.left}px`);
  glow.style.setProperty('--gy', `${event.clientY - box.top}px`);
}, { passive: true });
// tvOS-style tilt for app icons, plus a soft spotlight that follows the pointer over the catalogue.
const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
if (fine && !calm) {
  const tilt = (icon, host, max) => {
    host.addEventListener('pointermove', event => {
      const box = icon.getBoundingClientRect();
      const x = Math.max(-1, Math.min(1, (event.clientX - box.left) / box.width * 2 - 1));
      const y = Math.max(-1, Math.min(1, (event.clientY - box.top) / box.height * 2 - 1));
      icon.classList.add('is-tilting');
      icon.style.setProperty('--rx', `${(-y * max).toFixed(2)}deg`);
      icon.style.setProperty('--ry', `${(x * max).toFixed(2)}deg`);
    });
    host.addEventListener('pointerleave', () => {
      icon.classList.remove('is-tilting');
      icon.style.removeProperty('--rx');
      icon.style.removeProperty('--ry');
    });
  };
  document.querySelectorAll('.tile').forEach(tile => tilt(tile.querySelector('.icon'), tile, 14));
  const productIcon = document.querySelector('.product-icon');
  if (productIcon) tilt(productIcon, document.querySelector('.product-head'), 10);

  const catalogue = document.querySelector('.catalogue');
  catalogue?.addEventListener('pointermove', event => {
    const box = catalogue.getBoundingClientRect();
    catalogue.style.setProperty('--mx', `${event.clientX - box.left + 120}px`);
    catalogue.style.setProperty('--my', `${event.clientY - box.top + 40}px`);
    catalogue.style.setProperty('--spot', '1');
  });
  catalogue?.addEventListener('pointerleave', () => catalogue.style.setProperty('--spot', '0'));
}

// Screenshot strip: arrow buttons for mouse users, shown only when the strip overflows.
const row = document.querySelector('.screens-row');
if (row) {
  const nav = document.createElement('div');
  nav.className = 'screens-nav';
  const rtl = getComputedStyle(row).direction === 'rtl' ? -1 : 1;
  const buttons = [['previous', '‹', -1], ['next', '›', 1]].map(([key, glyph, step]) => {
    const button = document.createElement('button');
    button.type = 'button'; button.textContent = glyph; button.setAttribute('aria-label', row.dataset[key]);
    button.addEventListener('click', () => row.scrollBy({ left: step * rtl * row.clientWidth * .8, behavior: calm ? 'auto' : 'smooth' }));
    nav.append(button);
    return button;
  });
  const sync = () => {
    const max = row.scrollWidth - row.clientWidth, at = Math.abs(row.scrollLeft);
    nav.hidden = max < 4;
    buttons[0].disabled = at < 4;
    buttons[1].disabled = at > max - 4;
  };
  row.parentElement.querySelector('.screens-foot').append(nav);
  row.addEventListener('scroll', sync, { passive: true });
  addEventListener('resize', sync);
  addEventListener('load', sync);
  sync();
}

const dialog = document.querySelector('.image-dialog');
if (dialog) {
  const shots = [...document.querySelectorAll('[data-shot]')];
  let index = 0;
  let trigger;
  const update = () => {
    const image = dialog.querySelector('img');
    image.src = shots[index].dataset.shot;
    image.alt = shots[index].getAttribute('aria-label');
    dialog.querySelector('[data-position]').textContent = `${index + 1} / ${shots.length}`;
    dialog.querySelector('[data-previous]').disabled = index === 0;
    dialog.querySelector('[data-next]').disabled = index === shots.length - 1;
  };
  shots.forEach((shot,i) => shot.addEventListener('click', () => {
    index = i; trigger = shot; update(); dialog.showModal();
  }));
  dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
  dialog.querySelector('[data-previous]').addEventListener('click', () => { if(index>0) { index--; update(); } });
  dialog.querySelector('[data-next]').addEventListener('click', () => { if(index<shots.length-1) { index++; update(); } });
  dialog.addEventListener('close', () => trigger?.focus());
  dialog.addEventListener('click', event => { if(event.target === dialog) dialog.close(); });
}

// Render existing, first-party policy files. Escape input before recognising
// a small Markdown subset, so policy text cannot inject scripts or handlers.
const legal = document.body.dataset.legal;
if (legal) {
  const app = new URLSearchParams(location.search).get('app');
  const allowed = new Set(['booktou','speaktou','notero','lessonta','doitly','dictiony','beanjup','wordballoonpop','streaktou','carsurf','bumperpop','baggageflow']);
  const policy = document.querySelector('#policy');
  const esc = text => text.replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const inline = text => esc(text)
    .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+|mailto:[^\s)]+)\)/g,'<a href="$2">$1</a>');
  if (allowed.has(app)) {
    const file = `/assets/${legal}/${app}/${legal}-en.txt`;
    fetch(file).then(response => {
      if(!response.ok) throw new Error('Policy unavailable');
      return response.text();
    }).then(text => {
      let output = '', paragraph = [], items = [];
      const flush = () => { if(paragraph.length) { output += `<p>${inline(paragraph.join(' '))}</p>`; paragraph = []; } };
      const flushList = () => { if(items.length) { output += '<ul>'+items.map(item=>`<li>${inline(item)}</li>`).join('')+'</ul>'; items=[]; } };
      for (const line of text.split(/\r?\n/)) {
        const heading = line.trim().match(/^(#{1,3})\s+(.+)$/);
        const numberedHeading = line.trim().match(/^\d+\.\s+(.+)$/);
        const bullet = line.trim().match(/^[-*]\s+(.+)$/);
        if(bullet) { flush(); items.push(bullet[1]); continue; }
        if(items.length && /^\s{2,}\S/.test(line) && !heading && !numberedHeading) { items[items.length-1]+=' '+line.trim(); continue; }
        flushList();
        if(!line.trim() || heading || numberedHeading) flush();
        if(heading) { const level=Math.max(2,heading[1].length); output += `<h${level}>${inline(heading[2])}</h${level}>`; }
        else if(numberedHeading) output += `<h2>${inline(line.trim())}</h2>`;
        else if(line.trim()) paragraph.push(line.trim());
      }
      flush(); flushList();
      policy.innerHTML = output;
      const appName = document.querySelector(`a[href="/${legal}?app=${app}"] span`)?.textContent || app;
      document.title = `${appName} | ${legal === 'privacy' ? 'Privacy policy' : 'Terms of use'}`;
      document.querySelectorAll('.legal-app-picker a').forEach(a => { if(a.href.endsWith(`app=${app}`)) a.setAttribute('aria-current','page'); });
      const canonical = document.querySelector('link[rel="canonical"]');
      if(canonical) canonical.href = `https://www.rapheldorsoftware.com/${legal}?app=${app}`;
    }).catch(() => {
      policy.textContent = 'This policy could not be loaded. Please contact rapheldorsoftware@gmail.com.';
    });
  }
}
