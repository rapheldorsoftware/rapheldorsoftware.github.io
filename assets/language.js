// Only the unlocalized home entry uses device language. Explicit page URLs win.
// A manual language choice is remembered locally, without analytics or cookies.
(() => {
  const supported = new Set(['en','tr','ar','da','de','el','es','fi','fil','fr','hi','id','it','ja','ko','ms','nb','nl','pl','pt','ro','ru','sv','th','vi','zh']);
  const key = 'rapheldor-language';
  const resolve = value => {
    if(typeof value !== 'string') return null;
    const base=value.toLowerCase().split(/[-_]/)[0];
    const alias={no:'nb',tl:'fil',in:'id'}[base] || base;
    return supported.has(alias) ? alias : null;
  };
  let saved=null;
  try { saved=resolve(localStorage.getItem(key)); } catch (_) {}
  if(location.pathname==='/' || location.pathname==='/index.html') {
    const requested=resolve(new URLSearchParams(location.search).get('lang'));
    const device=(navigator.languages?.length ? navigator.languages : [navigator.language]).map(resolve).find(Boolean);
    const language=requested || saved || device || 'en';
    if(language!=='en') location.replace('/'+language+'/'+location.search+location.hash);
  }
  document.addEventListener('click', event => {
    const link=event.target instanceof Element ? event.target.closest('a[data-site-language]') : null;
    const language=resolve(link?.dataset.siteLanguage);
    if(language) { try { localStorage.setItem(key,language); } catch (_) {} }
  });
})();
