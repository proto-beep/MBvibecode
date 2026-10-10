// ==UserScript==
// @name         MB x Vibecode: Import Discogs credits COMPANION
// @namespace    https://github.com/proto-beep/MBvibecode
// @version      1.4.0
// @date         2026-10-10
// @description  Companion for "MB x Vibecode: Import Discogs credits": connects the import dashboard with a Discogs tab (e.g. the other half of a split view), loads the release there and highlights where each credit comes from.
// @description:de Ergänzung zu „MB x Vibecode: Import Discogs credits“: verbindet das Import-Dashboard mit einem Discogs-Tab (z. B. der anderen Hälfte einer geteilten Ansicht), lädt dort das Release und markiert, woher jeder Credit stammt.
// @description:es Complemento de «MB x Vibecode: Import Discogs credits»: conecta el panel de importación con una pestaña de Discogs (p. ej. la otra mitad de una vista dividida), carga allí la publicación y resalta de dónde viene cada crédito.
// @description:fr Complément de « MB x Vibecode: Import Discogs credits » : relie le tableau d'import à un onglet Discogs (p. ex. l'autre moitié d'un écran partagé), y charge la parution et met en évidence l'origine de chaque crédit.
// @author       proto-beep
// @license      CC0-1.0
// @homepageURL  https://github.com/proto-beep/MBvibecode
// @supportURL   https://github.com/proto-beep/MBvibecode/issues
// @downloadURL  https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-discogs-credits-sync.user.js
// @updateURL    https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-discogs-credits-sync.user.js
// @match        *://musicbrainz.org/release/*/edit-relationships*
// @match        *://*.musicbrainz.org/release/*/edit-relationships*
// @match        *://musicbrainz.org/release/*
// @match        *://*.musicbrainz.org/release/*
// @match        *://www.discogs.com/*
// @match        *://discogs.com/*
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_deleteValue
// @grant        GM_listValues
// @grant        GM_addValueChangeListener
// @grant        GM_openInTab
// @noframes
// @run-at       document-idle
// ==/UserScript==

/* global GM_setValue, GM_getValue, GM_deleteValue, GM_listValues, GM_addValueChangeListener, GM_openInTab */
(function () {
  'use strict';

  // How it works:
  // - Every Discogs tab with this script writes a heartbeat into the shared userscript storage.
  // - On the MB relationship editor this script relays between the dashboard of the main script
  //   (DOM events carrying JSON strings, which cross the page/sandbox boundary safely) and that storage.
  // - Commands go to one Discogs tab: a visible one first (e.g. in split view), else the most recently seen.
  // The main script never needs special permissions; only this companion does.

  const HEARTBEAT_MS = 2000;
  const STALE_MS = 7000;
  const norm = (s) => String(s == null ? '' : s).toLowerCase().replace(/\s+/g, ' ').trim();
  const isMusicBrainz = /(^|\.)musicbrainz\.org$/i.test(location.hostname);

  // ---------------------------------------------------------------------------
  // MusicBrainz side
  // ---------------------------------------------------------------------------

  /** The last status map of each release (at most 30 releases), for its MusicBrainz release page. */
  const PER_RELEASE_MAX = 30;
  function keepPerRelease(map) {
    GM_setValue(`statusMap:${map.mbRelease}`, map);
    const index = [map.mbRelease, ...(GM_getValue('statusMapIndex') || []).filter((x) => x !== map.mbRelease)];
    index.slice(PER_RELEASE_MAX).forEach((x) => GM_deleteValue(`statusMap:${x}`));
    GM_setValue('statusMapIndex', index.slice(0, PER_RELEASE_MAX));
  }

  function initMusicBrainzSide() {
    const send = (msg) => document.dispatchEvent(new CustomEvent('dci:from-discogs', { detail: JSON.stringify(msg) }));
    // The status marks on Discogs belong to this edit page: shown only while it is open.
    const pageId = Math.random().toString(36).slice(2, 10);
    let beatTimer = null;
    const mbRelease = (location.pathname.match(/[0-9a-f-]{36}/) || [])[0] || '';
    const statusBeat = () => GM_setValue('statusBeat', { pageId, release: mbRelease, ts: Date.now() });
    window.addEventListener('pagehide', () => {
      // With "status on the release page" the release page (where "Enter edit" leads) keeps the marks;
      // otherwise they go now. Either way they disappear once no page of the release reports any more.
      const map = GM_getValue('statusMap');
      if (map && map.pageId === pageId && !map.keepOnRelease) GM_setValue('statusMap', { pageId, enabled: false, items: [], ts: Date.now() });
    });

    const liveTabs = () => {
      const now = Date.now();
      const tabs = [];
      for (const key of GM_listValues()) {
        if (!String(key).startsWith('tab:')) continue;
        const tab = GM_getValue(key);
        if (tab && now - tab.ts < STALE_MS) tabs.push(tab);
        else if (!tab || now - tab.ts > 60000) GM_deleteValue(key);
      }
      return tabs;
    };

    const pickTab = (tabs, releaseId = null) => {
      // A tab that already shows the release comes first, then a visible one, then the last viewed one
      const same = releaseId ? tabs.filter((t) => String(t.releaseId) === String(releaseId)) : [];
      return [...(same.length ? same : tabs)].sort((a, b) => (Number(b.visible) - Number(a.visible)) || (b.lastVisible - a.lastVisible))[0] || null;
    };

    const status = () => {
      const tabs = liveTabs();
      const target = pickTab(tabs);
      send({
        type: 'status',
        tabs: tabs.length,
        target: target && { id: target.id, visible: target.visible, releaseId: target.releaseId },
        // Releases shown in the open Discogs tabs: "connected" means one of them is the dashboard's release
        releases: tabs.map((t) => String(t.releaseId || '')).filter(Boolean),
      });
    };

    // Other scripts on the page could send these events too, so only MusicBrainz and Discogs pages are opened.
    const mayOpen = (url) => /^https:\/\/((beta|test)\.)?musicbrainz\.org\//.test(String(url)) || /^https:\/\/(www\.)?discogs\.com\//.test(String(url));

    document.addEventListener('dci:to-discogs', (e) => {
      let msg;
      try {
        msg = JSON.parse(e.detail);
      } catch (err) {
        return;
      }
      if (msg.type === 'ping') {
        status();
      } else if (msg.type === 'open') {
        if (!mayOpen(msg.url)) return;
        GM_openInTab(msg.url, { active: false, insert: true });
        setTimeout(status, 2500);
      } else if (msg.type === 'open-tabs') {
        // Background tabs for the dashboard (e.g. the works of a release); at most 50 at once.
        const urls = (Array.isArray(msg.urls) ? msg.urls : []).filter(mayOpen).slice(0, 50);
        urls.forEach((u) => GM_openInTab(u, { active: false, insert: true }));
        send({ type: 'opened', n: urls.length });
      } else if (msg.type === 'reload') {
        const target = pickTab(liveTabs(), msg.releaseId);
        if (target) GM_setValue('cmd', { type: 'reload', target: target.id, id: Date.now(), sent: Date.now() });
      } else if (msg.type === 'status-map') {
        // Status of every Discogs credit, shown on the Discogs page (all tabs of that release)
        const map = { ...msg, pageId, ts: Date.now() };
        GM_setValue('statusMap', map);
        if (msg.mbRelease) keepPerRelease(map);
        statusBeat();
        if (!beatTimer) beatTimer = setInterval(statusBeat, 2000);
      } else if (msg.type === 'show') {
        const target = pickTab(liveTabs(), msg.releaseId);
        if (!target) {
          send({ type: 'result', id: msg.id, found: 'no-tab' });
          return;
        }
        GM_setValue('cmd', { ...msg, target: target.id, sent: Date.now() });
      }
    });

    GM_addValueChangeListener('result', (name, oldValue, newValue) => {
      if (newValue) send({ type: 'result', ...newValue });
    });
    // From the Discogs page back to the dashboard: a click on a status mark, a track under the mouse
    GM_addValueChangeListener('fromDiscogs', (name, oldValue, newValue) => {
      if (newValue && ['focus-row', 'hover-track'].includes(newValue.type)) send(newValue);
    });

    status();
  }

  // ---------------------------------------------------------------------------
  // Discogs side
  // ---------------------------------------------------------------------------

  function initDiscogsSide() {
    // sessionStorage survives navigation within the tab, so the tab keeps its id.
    let tabId = sessionStorage.getItem('dci-tab-id');
    if (!tabId) {
      tabId = Math.random().toString(36).slice(2, 10);
      sessionStorage.setItem('dci-tab-id', tabId);
    }
    let lastVisible = 0;
    const currentReleaseId = () => (location.pathname.match(/\/release\/(\d+)/) || [])[1] || '';

    const beat = () => {
      const visible = document.visibilityState === 'visible';
      if (visible) lastVisible = Date.now();
      GM_setValue(`tab:${tabId}`, { id: tabId, ts: Date.now(), visible, lastVisible, releaseId: currentReleaseId() });
    };
    beat();
    setInterval(beat, HEARTBEAT_MS);
    document.addEventListener('visibilitychange', beat);
    window.addEventListener('pagehide', () => GM_deleteValue(`tab:${tabId}`));

    const report = (cmd, found) => GM_setValue('result', { id: cmd.id, found, ts: Date.now() });

    const handle = async (cmd) => {
      if (cmd.type === 'reload') {
        location.reload();
        return;
      }
      if (String(cmd.releaseId) !== currentReleaseId()) {
        // Load the release first; the command is picked up again after the navigation.
        sessionStorage.setItem('dci-pending', JSON.stringify(cmd));
        report(cmd, 'loading');
        location.assign(`${location.origin}/release/${cmd.releaseId}`);
        return;
      }
      // "Load the release there": nothing to point at
      if (cmd.loadOnly) {
        report(cmd, 'loaded');
        return;
      }
      report(cmd, await locateWithRetry(cmd));
    };

    GM_addValueChangeListener('cmd', (name, oldValue, cmd) => {
      if (cmd && cmd.target === tabId) handle(cmd);
    });

    // Status marks of the dashboard
    let lastMap = null;
    let shown = false;
    // The edit page that sent the status is still open (it reports every 3 seconds)
    const senderAlive = (map) => {
      const beat = GM_getValue('statusBeat');
      const same = beat && (beat.release && map && map.mbRelease ? beat.release === map.mbRelease : beat.pageId === (map && map.pageId));
      return !!(map && same && Date.now() - beat.ts < 8000);
    };
    let artShown = false;
    const showMap = (map) => {
      lastMap = map;
      const here = !!(map && String(map.releaseId) === currentReleaseId() && senderAlive(map));
      shown = here && !!map.enabled;
      artShown = here && !!map.artwork;
      renderStatus(shown ? map : null);
      renderArtwork(artShown ? map : null);
    };
    GM_addValueChangeListener('statusMap', (name, oldValue, map) => showMap(map || null));
    const stored = GM_getValue('statusMap');
    if (stored) setTimeout(() => showMap(stored), 1500);
    // Discogs renders parts of the page later: mark again once the credits are there
    setTimeout(() => { if (lastMap) showMap(lastMap); }, 4000);
    // The edit page was closed (or crashed): remove the marks; they come back when it reports again
    setInterval(() => {
      if (!lastMap) return;
      const here = senderAlive(lastMap) && String(lastMap.releaseId) === currentReleaseId();
      if (shown !== (here && !!lastMap.enabled) || artShown !== (here && !!lastMap.artwork)) showMap(lastMap);
    }, 3000);
    document.addEventListener('click', (e) => {
      const mark = e.target.closest && e.target.closest('.dci-dg-mark');
      if (!mark) return;
      e.preventDefault();
      e.stopPropagation();
      GM_setValue('fromDiscogs', { type: 'focus-row', row: mark.dataset.row, releaseId: currentReleaseId(), ts: Date.now() });
    }, true);
    let hoverTimer = null;
    let lastPos = '';
    document.addEventListener('mouseover', (e) => {
      const row = e.target.closest && (e.target.closest('[data-track-position]') || e.target.closest('#release-tracklist tr, [id*="tracklist" i] tr'));
      if (!row) return;
      const pos = row.getAttribute('data-track-position') || ((row.querySelector('td, th') || {}).textContent || '').trim();
      if (!pos || pos === lastPos) return;
      lastPos = pos;
      clearTimeout(hoverTimer);
      hoverTimer = setTimeout(() => GM_setValue('fromDiscogs', { type: 'hover-track', position: pos, releaseId: currentReleaseId(), ts: Date.now() }), 250);
    });

    const pending = sessionStorage.getItem('dci-pending');
    if (pending) {
      sessionStorage.removeItem('dci-pending');
      try {
        const cmd = JSON.parse(pending);
        if (Date.now() - cmd.sent < 60000) handle(cmd);
      } catch (e) { /* ignore */ }
    }
  }

  // --- Finding the source of a credit on the Discogs release page ---------------
  // Discogs' markup has no stable hooks for scripts. The search therefore relies on
  // artist links (/artist/<id>-…), the role text and track positions.

  const HIGHLIGHT = 'dci-discogs-highlight';

  function ensureStyle() {
    if (document.getElementById('dci-discogs-style')) return;
    const style = document.createElement('style');
    style.id = 'dci-discogs-style';
    style.textContent = `
      .${HIGHLIGHT} {
        outline: 3px solid #eb743b !important;
        outline-offset: 2px !important;
        background-color: rgba(235, 116, 59, 0.14) !important;
        scroll-margin: 120px;
      }
      .dci-dg-mark { display: inline-block; min-width: 1.4em; margin-right: 0.35em; padding: 0 0.3em; border: 0; border-radius: 3px;
        font: bold 12px/1.5 sans-serif; text-align: center; color: #fff; cursor: pointer; vertical-align: 0.1em; }
      .dci-dg-mb { background: #2e7d4f; }
      .dci-dg-staged { background: #736dab; }
      .dci-dg-open { background: #8a8a8a; }
      .dci-dg-skip { background: #c4c4c4; color: #333; }
      .dci-dg-unmapped { background: #e0a800; }
      .dci-dg-pending { background: #c0392b; }
      #dci-artwork { position: fixed; top: 72px; right: 12px; z-index: 2147483000; display: flex; flex-direction: column; align-items: flex-end; gap: 4px;
        padding: 4px; background: #fff; border: 1px solid #c8c5d6; border-radius: 4px; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2); }
      #dci-artwork { cursor: grab; touch-action: none; user-select: none; }
      #dci-artwork.dci-art-moving, #dci-artwork.dci-art-moving * { cursor: grabbing !important; }
      #dci-artwork .dci-art-img { display: block; padding: 0; border: 0; background: none; cursor: zoom-in; }
      #dci-artwork .dci-art-img img { pointer-events: none; -webkit-user-drag: none; }
      #dci-artwork .dci-art-img img { display: block; width: 120px; max-height: 120px; object-fit: contain; }
      #dci-artwork .dci-art-toggle { border: 1px solid #c8c5d6; border-radius: 3px; background: #f7f6fb; color: #262430; font: 12px/1.4 sans-serif; padding: 0 6px; cursor: pointer; }
      #dci-artwork.dci-art-collapsed .dci-art-img { display: none; }
      .dci-dg-unmapped-line { background-color: #fff3c4 !important; }`;
    document.head.appendChild(style);
  }

  function highlight(el) {
    document.querySelectorAll(`.${HIGHLIGHT}`).forEach((x) => x.classList.remove(HIGHLIGHT));
    el.classList.add(HIGHLIGHT);
    el.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }

  function trackRows(position) {
    const p = norm(position);
    if (!p) return [];
    const byAttr = [...document.querySelectorAll('[data-track-position]')]
      .filter((el) => norm(el.getAttribute('data-track-position')) === p);
    if (byAttr.length) return byAttr;
    const rows = [];
    for (const row of document.querySelectorAll('tr')) {
      const first = row.querySelector('td, th');
      if (first && norm(first.textContent) === p) rows.push(row);
    }
    return rows;
  }

  /** Smallest ancestor (up to 5 levels) whose text also contains the role; otherwise the list item or row. */
  function lineOf(el, role) {
    let cur = el;
    for (let i = 0; i < 5 && cur && cur !== document.body; i++) {
      const text = norm(cur.textContent);
      if (text.length > 400) break; // do not climb into whole sections
      if (role && text.includes(role)) return cur;
      cur = cur.parentElement;
    }
    return el.closest('li, tr') || el;
  }

  const inTracklist = (el) => !!el.closest('[data-track-position], #release-tracklist, [id*="tracklist" i]');

  // --- Cover miniature: stays at the top of the Discogs tab while it is connected with MusicBrainz ----

  /** The cover of the release page: the page's preview image (og:image), else its first Discogs image. */
  function artworkUrl() {
    const og = document.querySelector('meta[property="og:image"]');
    if (og && og.content) return og.content;
    const img = [...document.querySelectorAll('img[src*="discogs.com"]')].find((i) => !i.closest('#dci-artwork'));
    return img ? img.src : '';
  }

  /** Opens Discogs' own image view: the image link of the page, else its main image; else the image itself. */
  function openDiscogsImages() {
    const link = [...document.querySelectorAll('a[href*="/image/"], a[href$="/images"], a[href*="/images?"]')].find((a) => !a.closest('#dci-artwork'));
    if (link) {
      link.click();
      return;
    }
    const img = [...document.querySelectorAll('img[src*="discogs.com"]')].find((i) => !i.closest('#dci-artwork'));
    if (img) {
      (img.closest('a, button, [role="button"]') || img).click();
      return;
    }
    const url = artworkUrl();
    if (url) window.open(url, '_blank', 'noopener');
  }

  function renderArtwork(map) {
    let box = document.getElementById('dci-artwork');
    const url = map ? artworkUrl() : '';
    if (!url) {
      if (box) box.remove();
      return;
    }
    ensureStyle();
    const labels = map.labels || {};
    if (!box) {
      box = document.createElement('div');
      box.id = 'dci-artwork';
      box.innerHTML = '<button type="button" class="dci-art-img"><img alt=""></button><button type="button" class="dci-art-toggle"></button>';
      document.body.appendChild(box);
      box.querySelector('.dci-art-img').addEventListener('click', (e) => {
        e.preventDefault();
        // The end of a move is not a click on the cover
        if (box.dataset.moved === '1') {
          box.dataset.moved = '';
          return;
        }
        openDiscogsImages();
      });
      makeArtMovable(box);
      box.querySelector('.dci-art-toggle').addEventListener('click', () => {
        const collapsed = !box.classList.contains('dci-art-collapsed');
        box.classList.toggle('dci-art-collapsed', collapsed);
        try {
          localStorage.setItem('dci-art-collapsed', collapsed ? '1' : '');
        } catch (e) { /* only for this tab */ }
        artLabels(box);
      });
      try {
        box.classList.toggle('dci-art-collapsed', localStorage.getItem('dci-art-collapsed') === '1');
      } catch (e) { /* expanded */ }
    }
    box.dataset.labels = JSON.stringify(labels);
    const img = box.querySelector('img');
    if (img.getAttribute('src') !== url) img.src = url;
    box.querySelector('.dci-art-img').title = labels.artwork || '';
    img.alt = labels.artwork || '';
    artLabels(box);
  }

  /** The cover box can be dragged anywhere in the window; its place is remembered for Discogs. */
  function placeArt(box, x, y) {
    const w = box.offsetWidth || 130;
    const h = box.offsetHeight || 40;
    const left = Math.max(0, Math.min(window.innerWidth - w, x));
    const top = Math.max(0, Math.min(window.innerHeight - Math.min(h, 40), y));
    Object.assign(box.style, { left: `${left}px`, top: `${top}px`, right: 'auto' });
    return { x: left, y: top };
  }

  function makeArtMovable(box) {
    try {
      const saved = JSON.parse(localStorage.getItem('dci-art-pos') || 'null');
      if (saved && Number.isFinite(saved.x) && Number.isFinite(saved.y)) requestAnimationFrame(() => placeArt(box, saved.x, saved.y));
    } catch (e) { /* default place */ }
    box.addEventListener('pointerdown', (e) => {
      if (e.button !== 0 || e.target.closest('.dci-art-toggle')) return;
      const r = box.getBoundingClientRect();
      const dx = e.clientX - r.left;
      const dy = e.clientY - r.top;
      const sx = e.clientX;
      const sy = e.clientY;
      let moving = false;
      const move = (ev) => {
        if (!moving && Math.abs(ev.clientX - sx) + Math.abs(ev.clientY - sy) < 5) return;
        if (!moving) {
          moving = true;
          box.classList.add('dci-art-moving');
          box.setPointerCapture(e.pointerId);
        }
        ev.preventDefault();
        placeArt(box, ev.clientX - dx, ev.clientY - dy);
      };
      const end = () => {
        box.removeEventListener('pointermove', move);
        box.removeEventListener('pointerup', end);
        box.removeEventListener('pointercancel', end);
        if (!moving) return;
        box.classList.remove('dci-art-moving');
        box.dataset.moved = '1';
        setTimeout(() => { box.dataset.moved = ''; }, 400);
        const p = box.getBoundingClientRect();
        try {
          localStorage.setItem('dci-art-pos', JSON.stringify({ x: Math.round(p.left), y: Math.round(p.top) }));
        } catch (err) { /* only for now */ }
      };
      box.addEventListener('pointermove', move);
      box.addEventListener('pointerup', end);
      box.addEventListener('pointercancel', end);
    });
    window.addEventListener('resize', () => {
      if (box.isConnected && box.style.left) placeArt(box, parseFloat(box.style.left), parseFloat(box.style.top));
    });
  }

  function artLabels(box) {
    let labels = {};
    try {
      labels = JSON.parse(box.dataset.labels || '{}');
    } catch (e) { /* none */ }
    const collapsed = box.classList.contains('dci-art-collapsed');
    const t = box.querySelector('.dci-art-toggle');
    t.textContent = collapsed ? '🖼' : '–';
    t.title = (collapsed ? labels.artworkShow : labels.artworkHide) || '';
    t.setAttribute('aria-label', t.title);
  }

  // --- Status marks: which Discogs credits are in MusicBrainz, staged, open, skipped or not mapped ----

  const MARK_SYMBOL = { mb: '✓', staged: '●', open: '○', skip: '–', unmapped: '!', pending: '✗' };

  function renderStatus(map) {
    ensureStyle();
    document.querySelectorAll('.dci-dg-mark').forEach((m) => m.remove());
    document.querySelectorAll('.dci-dg-unmapped-line').forEach((m) => m.classList.remove('dci-dg-unmapped-line'));
    if (!map || !map.enabled) return;
    expandCredits();
    const labels = map.labels || {};
    for (const item of map.items || []) {
      const found = findCredit(item);
      if (!found || found.score < 3) continue;
      const status = item.unmapped ? 'unmapped' : item.status;
      const mark = document.createElement('button');
      mark.type = 'button';
      mark.className = `dci-dg-mark dci-dg-${status}`;
      mark.dataset.row = item.row;
      mark.textContent = MARK_SYMBOL[status] || '?';
      const checked = map.checked && (status === 'mb' || status === 'pending') ? ` (${labels.checked || ''})` : '';
      mark.title = `${labels[status] || status}${item.note ? ` ${item.note}` : ''}${checked} – ${labels.click || ''}`.trim();
      found.el.insertBefore(mark, found.el.firstChild);
      if (item.unmapped) found.el.classList.add('dci-dg-unmapped-line');
    }
  }

  /** The best matching credit line for an artist (or label) and a role, without highlighting it. */
  function findCredit(cmd) {
    const role = norm(cmd.base || cmd.role);
    const positions = (cmd.positions || []).filter(Boolean);
    const rowsForTrack = positions.flatMap(trackRows);
    const kind = cmd.labelId ? 'label' : 'artist';
    const entityId = cmd.labelId || cmd.artistId;
    if (!entityId) return null;
    const re = new RegExp(`/${kind}/${entityId}(?:[-/?#]|$)`);
    let best = null;
    for (const a of document.querySelectorAll(`a[href*="/${kind}/"]`)) {
      if (!re.test(a.getAttribute('href') || '')) continue;
      const line = lineOf(a, role);
      let score = 0;
      if (role && norm(line.textContent).includes(role)) score += 3;
      if (positions.length && rowsForTrack.some((r) => r.contains(a))) score += 1;
      if (!positions.length && !inTracklist(a)) score += 1;
      if (!best || score > best.score) best = { el: line, score };
    }
    return best;
  }

  function locate(cmd) {
    const role = norm(cmd.base || cmd.role);
    const positions = (cmd.positions || []).filter(Boolean);
    const rowsForTrack = positions.flatMap(trackRows);

    let anchors = [];
    // Artists link to /artist/<id>; companies ("Companies, etc.") link to /label/<id>.
    const kind = cmd.labelId ? 'label' : 'artist';
    const entityId = cmd.labelId || cmd.artistId;
    if (entityId) {
      const re = new RegExp(`/${kind}/${entityId}(?:[-/?#]|$)`);
      anchors = [...document.querySelectorAll(`a[href*="/${kind}/"]`)].filter((a) => re.test(a.getAttribute('href') || ''));
    }
    if (!anchors.length && (cmd.anv || cmd.artistName)) {
      // Credits without a Discogs artist ID: match the name (Discogs marks name variations with "*").
      const names = [cmd.anv, cmd.artistName].map(norm).filter(Boolean);
      anchors = [...document.querySelectorAll('a, span')]
        .filter((el) => !el.children.length && names.includes(norm(el.textContent).replace(/\*$/, '')));
    }

    let best = null;
    for (const a of anchors) {
      const line = lineOf(a, role);
      let score = 0;
      if (role && norm(line.textContent).includes(role)) score += 3;
      if (positions.length && rowsForTrack.some((r) => r.contains(a))) score += 3;
      if (!positions.length && !inTracklist(a)) score += 2;
      if (!best || score > best.score) best = { el: line, score };
    }
    if (best && (best.score > 0 || !role)) {
      highlight(best.el);
      return role && best.score >= 3 ? 'credit' : 'artist';
    }
    if (rowsForTrack.length) {
      highlight(rowsForTrack[0]);
      return 'track';
    }
    return 'none';
  }

  function expandCredits() {
    const buttons = document.querySelectorAll('#release-credits button, [id*="credits" i] button');
    for (const b of buttons) {
      if (b.getAttribute('aria-expanded') !== 'true' && /(show|more|mehr|alle|all)/i.test(b.textContent)) b.click();
    }
  }

  async function locateWithRetry(cmd) {
    ensureStyle();
    let result = 'none';
    // The page may still be rendering after a navigation, so try a few times.
    for (let attempt = 0; attempt < 5; attempt++) {
      result = locate(cmd);
      if (result === 'credit' || (!cmd.role && result !== 'none')) return result;
      if (attempt === 1) expandCredits();
      await new Promise((resolve) => setTimeout(resolve, 600));
    }
    return result;
  }

  // Start only after all declarations above are initialized.
  /** The release page of MusicBrainz keeps the Discogs status marks of its release alive (if switched on). */
  /**
   * MusicBrainz release page: the status marks of this release (as the dashboard last sent them) are
   * checked against what MusicBrainz now has – e.g. after "Enter edit" – and shown on Discogs while
   * this page is open. ✓ = in MusicBrainz, ✗ = staged in the editor but not (yet) in MusicBrainz.
   */
  function initReleasePage() {
    const mbRelease = (location.pathname.match(/[0-9a-f-]{36}/) || [])[0] || '';
    if (!mbRelease) return;
    const pageId = `release-${mbRelease}`;
    const stored = () => {
      const own = GM_getValue(`statusMap:${mbRelease}`);
      const current = GM_getValue('statusMap');
      const map = own || (current && current.mbRelease === mbRelease ? current : null);
      return map && map.enabled && map.keepOnRelease ? map : null;
    };
    const beat = () => {
      if (stored()) GM_setValue('statusBeat', { pageId, release: mbRelease, ts: Date.now() });
    };
    const relKeys = (ws) => {
      const keys = new Set();
      const add = (target, rels) => (rels || []).forEach((r) => {
        const et = r['target-type'];
        const e = et && (r[et] || r[et.replace('_', '-')]);
        if (e && e.id) keys.add(`${target}|${e.id}|${r['type-id']}`);
      });
      add(ws.id, ws.relations);
      if (ws['release-group']) add(ws['release-group'].id, ws['release-group'].relations);
      (ws.media || []).forEach((m) => (m.tracks || []).forEach((t) => {
        const rec = t.recording;
        if (!rec) return;
        add(rec.id, rec.relations);
        (rec.relations || []).forEach((r) => { if (r['target-type'] === 'work' && r.work) add(r.work.id, r.work.relations); });
      }));
      return keys;
    };
    const check = async () => {
      const map = stored();
      if (!map) return;
      let ws = null;
      try {
        const inc = 'artist-rels+label-rels+place-rels+series-rels+recordings+recording-level-rels+work-rels+work-level-rels+release-groups+release-group-level-rels';
        const res = await fetch(`/ws/2/release/${mbRelease}?inc=${inc}&fmt=json`, { headers: { Accept: 'application/json' } });
        if (res.ok) ws = await res.json();
      } catch (e) { /* the marks stay as the dashboard sent them */ }
      const keys = ws ? relKeys(ws) : null;
      const items = (map.items || []).map((item) => {
        if (!keys || !item.mb || !item.mb.t || !item.mb.t.length) return item;
        const targets = item.mb.t.map((i) => (map.targets || [])[i]).filter(Boolean);
        const found = targets.filter((g) => keys.has(`${g}|${item.mb.e}|${item.mb.lt}`)).length;
        if (found === targets.length) return { ...item, status: 'mb', note: '' };
        if (item.status === 'staged' || item.status === 'mb') return { ...item, status: 'pending', note: `${found}/${targets.length}` };
        return item;
      });
      GM_setValue('statusMap', { ...map, items, pageId, checked: ws ? Date.now() : 0, ts: Date.now() });
      beat();
    };
    beat();
    setInterval(beat, 2000);
    check();
    // Edits can take a moment to be applied: look again a little later
    setTimeout(check, 20000);
    setTimeout(check, 60000);
    // Closed: the marks on Discogs go at once (unless the edit page of this release is still open)
    window.addEventListener('pagehide', () => {
      const b = GM_getValue('statusBeat');
      if (b && b.pageId === pageId) GM_setValue('statusBeat', { pageId, release: mbRelease, ts: 0 });
    });
  }

  if (isMusicBrainz && /\/edit-relationships/.test(location.pathname)) initMusicBrainzSide();
  else if (isMusicBrainz) initReleasePage();
  else initDiscogsSide();
})();
