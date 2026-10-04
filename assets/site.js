// Content and navigation work without JavaScript. This only enhances filtering
// and the screenshot viewer; no analytics or third-party code is loaded.
const filters = [...document.querySelectorAll('[data-filter]')];
const cards = [...document.querySelectorAll('[data-category]')];
filters.forEach(button => button.addEventListener('click', () => {
  filters.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
  let count = 0;
  cards.forEach(card => {
    card.hidden = button.dataset.filter !== 'all' && card.dataset.category !== button.dataset.filter;
    if (!card.hidden) count++;
  });
  const status = document.querySelector('.filter-status');
  if (status) status.textContent = count ? `${button.textContent}: ${count}` : status.dataset.empty;
}));

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
  const allowed = new Set(['booktou','speaktou','notero','lessonta','doitly','dictiony','beanjup','wordballoonpop','streaktou']);
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
