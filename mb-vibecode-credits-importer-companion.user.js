// ==UserScript==
// @name         MB x Vibecode: Credits Importer Companion
// @namespace    https://github.com/proto-beep/MBvibecode
// @version      1.8.3
// @date         2026-10-17
// @description  Companion for "MB x Vibecode: Credits Importer": connects the import dashboard with a Discogs or Bandcamp tab (e.g. the other half of a split view), loads the release there and highlights where each credit comes from.
// @description:de Ergänzung zu „MB x Vibecode: Credits Importer“: verbindet das Import-Dashboard mit einem Discogs- oder Bandcamp-Tab (z. B. der anderen Hälfte einer geteilten Ansicht), lädt dort das Release und markiert, woher jeder Credit stammt.
// @description:es Complemento de «MB x Vibecode: Credits Importer»: conecta el panel de importación con una pestaña de Discogs o Bandcamp (p. ej. la otra mitad de una vista dividida), carga allí la publicación y resalta de dónde viene cada crédito.
// @description:fr Complément de « MB x Vibecode: Credits Importer » : relie le tableau d'import à un onglet Discogs ou Bandcamp (p. ex. l'autre moitié d'un écran partagé), y charge la parution et met en évidence l'origine de chaque crédit.
// @author       proto-beep
// @license      CC0-1.0
// @homepageURL  https://github.com/proto-beep/MBvibecode
// @supportURL   https://github.com/proto-beep/MBvibecode/issues
// @downloadURL  https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-vibecode-credits-importer-companion.user.js
// @updateURL    https://raw.githubusercontent.com/proto-beep/MBvibecode/main/mb-vibecode-credits-importer-companion.user.js
// @match        *://musicbrainz.org/release/*/edit-relationships*
// @match        *://*.musicbrainz.org/release/*/edit-relationships*
// @match        *://musicbrainz.org/release/*
// @match        *://*.musicbrainz.org/release/*
// @match        *://www.discogs.com/*
// @match        *://discogs.com/*
// @match        *://*.bandcamp.com/*
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
  // - Every Discogs and Bandcamp tab with this script writes a heartbeat into the shared userscript storage (with its
  //   site: "discogs" or "bandcamp", since 1.8.0).
  // - On the MB relationship editor this script relays between the dashboard of the main script
  //   (DOM events carrying JSON strings, which cross the page/sandbox boundary safely) and that storage.
  // - Commands go to one tab of the site of the loaded source: a visible one first (e.g. in split view), else the most
  //   recently seen.
  // The main script never needs special permissions; only this companion does.

  const HEARTBEAT_MS = 2000;
  const STALE_MS = 7000;
  // [1.8.2] how long the status of an edit or release page in a background tab counts as alive without a new beat
  const BEAT_HIDDEN_MS = 75000;
  // [1.8.2] a check of the release page that could not read MusicBrainz is tried again after this long (at most 8 times)
  const RECHECK_MS = 15000;
  // [1.8.3] how long the pointer rests on a mark before the dashboard shows its row
  const MARK_HOVER_MS = 450;
  const norm = (s) => String(s == null ? '' : s).toLowerCase().replace(/\s+/g, ' ').trim();
  const isMusicBrainz = /(^|\.)musicbrainz\.org$/i.test(location.hostname);
  const isBandcamp = /(^|\.)bandcamp\.com$/i.test(location.hostname);
  /** [1.8.0] The sites the companion shows; a tab without a site (before 1.8.0) is a Discogs tab. */
  const SITES = ['discogs', 'bandcamp'];
  const siteOf = (x) => (x && SITES.includes(x.site) ? x.site : 'discogs');

  // Stored data of the companion has a generation; an update that raises it clears it once
  // (2: COMPANION 1.4.2, together with Import 2.11.0; 3: COMPANION 1.4.3, together with Import 2.13.0; 4: Companion
  // 1.7.0, together with Credits Importer 3.4.0, a fresh start): the shared storage and, on Discogs, the cover box
  // settings. Raised only after asking the maintainer.
  const STORE_EPOCH = 4;
  try {
    if ((Number(GM_getValue('storeEpoch')) || 0) < STORE_EPOCH) {
      GM_listValues().forEach((key) => GM_deleteValue(key));
      GM_setValue('storeEpoch', STORE_EPOCH);
    }
  } catch (e) { /* storage not available */ }
  if (!isMusicBrainz) {
    try {
      if ((Number(localStorage.getItem('dci-store-epoch')) || 0) < STORE_EPOCH) {
        Object.keys(localStorage).filter((key) => key.startsWith('dci-')).forEach((key) => localStorage.removeItem(key));
        localStorage.setItem('dci-store-epoch', String(STORE_EPOCH));
      }
    } catch (e) { /* storage blocked */ }
  }

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
    // [1.8.2] "hidden": a page in the background beats more slowly (the browser slows its timers down to once a minute)
    const statusBeat = () => GM_setValue('statusBeat', { pageId, release: mbRelease, ts: Date.now(), hidden: document.visibilityState === 'hidden' });
    document.addEventListener('visibilitychange', () => { if (beatTimer) statusBeat(); });
    window.addEventListener('pagehide', () => {
      // With "status on the release page" the release page (where "Enter edit" leads) keeps the marks;
      // otherwise they go now. Either way they disappear once no page of the release reports any more.
      const map = GM_getValue('statusMap');
      if (map && map.pageId === pageId && !map.keepOnRelease) GM_setValue('statusMap', { pageId, enabled: false, items: [], ts: Date.now() });
      // [1.8.2] closed: its last beat (maybe from going into the background) does not keep the marks for another 75 s
      const beat = GM_getValue('statusBeat');
      if (beat && beat.pageId === pageId) GM_setValue('statusBeat', { pageId, release: mbRelease, ts: 0 });
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

    const pickTab = (tabs, releaseId = null, site = 'discogs') => {
      // [1.8.0] Only tabs of the site (Discogs or Bandcamp) of the command
      const own = tabs.filter((t) => siteOf(t) === site);
      // A tab that already shows the release comes first, then a visible one, then the last viewed one
      const same = releaseId ? own.filter((t) => String(t.releaseId) === String(releaseId)) : [];
      return [...(same.length ? same : own)].sort((a, b) => (Number(b.visible) - Number(a.visible)) || (b.lastVisible - a.lastVisible))[0] || null;
    };

    const status = () => {
      const tabs = liveTabs();
      const ofSite = (site) => {
        const own = tabs.filter((t) => siteOf(t) === site);
        const target = pickTab(own, null, site);
        return {
          tabs: own.length,
          target: target && { id: target.id, visible: target.visible, releaseId: target.releaseId },
          // Releases shown in the open tabs of the site: "connected" means one of them is the dashboard's release
          releases: own.map((t) => String(t.releaseId || '')).filter(Boolean),
        };
      };
      const sites = Object.fromEntries(SITES.map((site) => [site, ofSite(site)]));
      // The Discogs tabs as before 1.8.0 (for older main scripts), and the tabs of each site
      send({ type: 'status', ...sites.discogs, sites });
    };

    // Other scripts on the page could send these events too, so only MusicBrainz, Discogs and Bandcamp pages are opened.
    const mayOpen = (url) => /^https:\/\/((beta|test)\.)?musicbrainz\.org\//.test(String(url)) || /^https:\/\/(www\.)?discogs\.com\//.test(String(url))
      || /^https:\/\/([a-z0-9-]+\.)?bandcamp\.com\//i.test(String(url));

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
        const target = pickTab(liveTabs(), msg.releaseId, siteOf(msg));
        if (target) GM_setValue('cmd', { type: 'reload', target: target.id, id: Date.now(), sent: Date.now() });
      } else if (msg.type === 'status-map') {
        // Status of every Discogs credit, shown on the Discogs page (all tabs of that release)
        const map = { ...msg, pageId, ts: Date.now() };
        // [1.8.3] the dashboard's switch "Keep marks", for the Discogs and Bandcamp tabs when no editor is open
        if (GM_getValue('keepMarks') !== !!msg.keepAfterClose) GM_setValue('keepMarks', !!msg.keepAfterClose);
        GM_setValue('statusMap', map);
        if (msg.mbRelease) keepPerRelease(map);
        statusBeat();
        if (!beatTimer) beatTimer = setInterval(statusBeat, 2000);
      } else if (msg.type === 'forget-release') {
        // "Delete stored import" in the dashboard (Credits Importer 3.4.0): the kept status of this release goes
        const id = String(msg.mbRelease || '');
        if (!id) return;
        GM_deleteValue(`statusMap:${id}`);
        GM_setValue('statusMapIndex', (GM_getValue('statusMapIndex') || []).filter((x) => x !== id));
        const map = GM_getValue('statusMap');
        if (map && map.mbRelease === id) GM_setValue('statusMap', { pageId, enabled: false, items: [], ts: Date.now() });
      } else if (msg.type === 'reset-settings') {
        // "Defaults" in the dashboard: every Discogs tab (now or when opened next) forgets the cover's place and folding
        GM_setValue('artReset', Date.now());
      } else if (msg.type === 'show') {
        const target = pickTab(liveTabs(), msg.releaseId, siteOf(msg));
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
      // [1.8.1] ⊘ on Bandcamp: a credit off or on again
      if (newValue && ['focus-row', 'hover-track', 'toggle-credit'].includes(newValue.type)) send(newValue);
    });

    status();
  }

  // ---------------------------------------------------------------------------
  // Discogs and Bandcamp side
  // ---------------------------------------------------------------------------
  // [1.8.0] The same for both sites (heartbeat, commands, status marks, back to the dashboard); what differs is in
  // DISCOGS_SIDE and BANDCAMP_SIDE: which release the page shows, which page a command needs, how a credit is found.

  function initSourceSide(side) {
    // sessionStorage survives navigation within the tab, so the tab keeps its id.
    let tabId = sessionStorage.getItem('dci-tab-id');
    if (!tabId) {
      tabId = Math.random().toString(36).slice(2, 10);
      sessionStorage.setItem('dci-tab-id', tabId);
    }
    let lastVisible = 0;
    const currentReleaseId = side.releaseId;

    const beat = () => {
      const visible = document.visibilityState === 'visible';
      if (visible) lastVisible = Date.now();
      GM_setValue(`tab:${tabId}`, { id: tabId, site: side.id, ts: Date.now(), visible, lastVisible, releaseId: currentReleaseId() });
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
      // The page the command needs: '' when this one, null when none can be loaded
      const go = side.pageFor(cmd);
      if (go === null) {
        report(cmd, 'none');
        return;
      }
      if (go) {
        // Load the release (or its page) first; the command is picked up again after the navigation.
        sessionStorage.setItem('dci-pending', JSON.stringify(cmd));
        report(cmd, 'loading');
        location.assign(go);
        return;
      }
      // "Load the release there": nothing to point at
      if (cmd.loadOnly) {
        report(cmd, 'loaded');
        return;
      }
      report(cmd, await side.locate(cmd));
    };

    GM_addValueChangeListener('cmd', (name, oldValue, cmd) => {
      if (cmd && cmd.target === tabId && siteOf(cmd) === side.id) handle(cmd);
    });

    // Status marks of the dashboard
    let lastMap = null;
    let shown = false;
    // The edit page that sent the status is still open (it reports every 3 seconds)
    const senderAlive = (map) => {
      const beat = GM_getValue('statusBeat');
      const same = beat && (beat.release && map && map.mbRelease ? beat.release === map.mbRelease : beat.pageId === (map && map.pageId));
      // [1.8.2] a page in the background may beat only once a minute
      return !!(map && same && Date.now() - beat.ts < (beat.hidden ? BEAT_HIDDEN_MS : 8000));
    };
    // A status map of this site and of the release this page shows
    const forHere = (map) => !!(map && siteOf(map) === side.id && String(map.releaseId) === currentReleaseId());
    const isHere = (map) => forHere(map) && senderAlive(map);
    /**
     * [1.8.3] "Keep marks" (switched on in the dashboard): with no editor or release page of the release open, its last
     * status as kept for its release page (the last 30 releases).
     */
    const keptMap = () => {
      if (!GM_getValue('keepMarks')) return null;
      for (const id of GM_getValue('statusMapIndex') || []) {
        const m = GM_getValue(`statusMap:${id}`);
        if (forHere(m) && m.enabled) return m;
      }
      return null;
    };
    let artShown = false;
    // the map shown and whether a page of MusicBrainz is open for it (a click on a mark reaches the dashboard only then)
    let shownMap = null;
    let live = false;
    let shownSig = '';
    const showMap = (map) => {
      lastMap = map;
      const here = isHere(map);
      const use = here ? map : keptMap();
      shown = !!(use && use.enabled);
      live = here;
      shownMap = shown ? use : null;
      shownSig = shownMap ? `${here}|${shownMap.ts}|${shownMap.pageId}` : '';
      artShown = here && !!map.artwork && !!side.artwork;
      side.renderStatus(shownMap);
      if (side.artwork) renderArtwork(artShown ? map : null);
    };
    GM_addValueChangeListener('statusMap', (name, oldValue, map) => showMap(map || null));
    if (side.artwork) {
      GM_addValueChangeListener('artReset', (name, oldValue, ts) => resetArt(ts));
      resetArt(GM_getValue('artReset'));
    }
    // [1.8.0] the newest map then (one that arrived meanwhile is not replaced by the one stored when the page opened)
    if (GM_getValue('statusMap')) setTimeout(() => showMap(lastMap || GM_getValue('statusMap') || null), 1500);
    // Discogs renders parts of the page later: mark again once the credits are there
    setTimeout(() => { if (lastMap) showMap(lastMap); }, 4000);
    // The edit page was closed (or crashed): remove the marks; they come back when it reports again ([1.8.3] or the kept
    // ones are shown)
    setInterval(() => {
      if (!lastMap && !GM_getValue('keepMarks')) return;
      const here = isHere(lastMap);
      const use = here ? lastMap : keptMap();
      const sig = use && use.enabled ? `${here}|${use.ts}|${use.pageId}` : '';
      if (sig !== shownSig || artShown !== (here && !!lastMap.artwork && !!side.artwork)) showMap(lastMap);
    }, 3000);
    document.addEventListener('click', (e) => {
      const mark = e.target.closest && e.target.closest('.dci-dg-mark');
      if (!mark) return;
      e.preventDefault();
      e.stopPropagation();
      // only kept marks (no editor open): nothing to show or switch
      if (!live) return;
      // [1.8.3] "Click switches" (dashboard): the credit off (its row "Skip") or on again; else its row in the dashboard
      if (shownMap && shownMap.toggle) {
        GM_setValue('fromDiscogs', { type: 'toggle-credit', row: mark.dataset.row, off: !mark.classList.contains('dci-mark-off'), releaseId: currentReleaseId(), ts: Date.now() });
      } else {
        GM_setValue('fromDiscogs', { type: 'focus-row', row: mark.dataset.row, releaseId: currentReleaseId(), ts: Date.now() });
      }
    }, true);
    // [1.8.3] the pointer resting on a mark: its row in the dashboard
    let markTimer = null;
    let markEl = null;
    document.addEventListener('mouseover', (e) => {
      const mark = e.target.closest && e.target.closest('.dci-dg-mark');
      if (mark === markEl) return;
      markEl = mark;
      clearTimeout(markTimer);
      if (mark && live && shownMap && shownMap.toggle) {
        markTimer = setTimeout(() => {
          if (markEl === mark) GM_setValue('fromDiscogs', { type: 'focus-row', hover: true, row: mark.dataset.row, releaseId: currentReleaseId(), ts: Date.now() });
        }, MARK_HOVER_MS);
      }
    });
    let hoverTimer = null;
    let lastPos = '';
    document.addEventListener('mouseover', (e) => {
      const pos = side.trackAt(e.target);
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

  /** The Discogs release page: its release id, the tracklist, the credits found by their artist links. */
  const DISCOGS_SIDE = {
    id: 'discogs',
    artwork: true,
    releaseId: () => (location.pathname.match(/\/release\/(\d+)/) || [])[1] || '',
    pageFor(cmd) {
      if (String(cmd.releaseId) === DISCOGS_SIDE.releaseId()) return '';
      return /^\d+$/.test(String(cmd.releaseId)) ? `${location.origin}/release/${cmd.releaseId}` : null;
    },
    locate: (cmd) => locateWithRetry(cmd),
    renderStatus: (map) => renderStatus(map),
    trackAt(target) {
      const row = target.closest && (target.closest('[data-track-position]') || target.closest('#release-tracklist tr, [id*="tracklist" i] tr'));
      if (!row) return '';
      return row.getAttribute('data-track-position') || ((row.querySelector('td, th') || {}).textContent || '').trim();
    },
  };

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
        padding: 4px; border-radius: 6px; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
        /* MusicBrainz colours: a frame from MB purple to MB orange */
        border: 3px solid transparent; background: linear-gradient(#fff, #fff) padding-box, linear-gradient(135deg, #ba478f, #eb743b) border-box; }
      #dci-artwork { cursor: grab; touch-action: none; user-select: none; }
      #dci-artwork.dci-art-moving, #dci-artwork.dci-art-moving * { cursor: grabbing !important; }
      #dci-artwork .dci-art-img { display: block; padding: 0; border: 0; background: none; cursor: zoom-in; }
      #dci-artwork .dci-art-img img { pointer-events: none; -webkit-user-drag: none; }
      #dci-artwork .dci-art-img img { display: block; width: 120px; max-height: 120px; object-fit: contain; }
      #dci-artwork .dci-art-toggle { border: 1px solid #c8c5d6; border-radius: 3px; background: #f7f6fb; color: #262430; font: 12px/1.4 sans-serif; padding: 0 6px; cursor: pointer; }
      #dci-artwork.dci-art-collapsed .dci-art-img { display: none; }
      .dci-dg-unmapped-line { background-color: #fff3c4 !important; }
      .dci-bc-hl { background-color: rgba(235, 116, 59, 0.22) !important; box-shadow: 0 0 0 2px rgba(235, 116, 59, 0.6); border-radius: 2px; scroll-margin: 120px; }
      .dci-dg-mark.dci-mark-off { opacity: 0.55; }
      .dci-dg-offline { opacity: 0.5; }
      .dci-bc-offtext { opacity: 0.45; text-decoration: line-through; }`;
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

  /** "Defaults" in the dashboard: the cover box goes back to its place, unfolded (once per reset). */
  function resetArt(ts) {
    try {
      if (!ts || Number(localStorage.getItem('dci-art-reset') || 0) >= ts) return;
      localStorage.removeItem('dci-art-pos');
      localStorage.removeItem('dci-art-collapsed');
      localStorage.setItem('dci-art-reset', String(ts));
    } catch (e) {
      return;
    }
    const box = document.getElementById('dci-artwork');
    if (!box) return;
    Object.assign(box.style, { left: '', top: '', right: '' });
    box.classList.remove('dci-art-collapsed');
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

  /**
   * The tooltip of a mark: where (track position or role), status, note, checked; [1.8.3] switched off, and what a click
   * does ("Click switches": skip / take again, resting the pointer shows the row; else: show the row).
   */
  function markTitle(map, item, status, note, where) {
    const labels = map.labels || {};
    const checked = map.checked && (status === 'mb' || status === 'pending') ? ` (${labels.checked || ''})` : '';
    const off = item.off ? ` (${labels.isOff || ''})` : '';
    const act = map.toggle ? `${(item.off ? labels.on : labels.off) || ''}; ${labels.hover || ''}` : labels.click || '';
    return `${where ? `${where}: ` : ''}${labels[status] || status}${note ? ` ${note}` : ''}${checked}${off} – ${act}`.trim();
  }

  function renderStatus(map) {
    ensureStyle();
    document.querySelectorAll('.dci-dg-mark').forEach((m) => m.remove());
    document.querySelectorAll('.dci-dg-unmapped-line').forEach((m) => m.classList.remove('dci-dg-unmapped-line'));
    document.querySelectorAll('.dci-dg-offline').forEach((m) => m.classList.remove('dci-dg-offline'));
    if (!map || !map.enabled) return;
    expandCredits();
    // [1.8.3] lines whose marks are all switched off are greyed
    const lines = new Map();
    const place = (item, found, status, note, pos = '') => {
      const mark = document.createElement('button');
      mark.type = 'button';
      mark.className = `dci-dg-mark dci-dg-${status}${item.off ? ' dci-mark-off' : ''}`;
      mark.dataset.row = item.row;
      if (pos) mark.dataset.pos = pos;
      mark.textContent = MARK_SYMBOL[status] || '?';
      mark.title = markTitle(map, item, status, note, pos);
      found.el.insertBefore(mark, found.el.firstChild);
      if (item.unmapped) found.el.classList.add('dci-dg-unmapped-line');
      // (the credit's list item; the element found may be only the name inside it)
      const line = found.el.closest('li') || found.el;
      lines.set(line, (lines.get(line) !== false) && !!item.off);
    };
    for (const item of map.items || []) {
      // A credit on Discogs track lines: a mark on each of its lines, with the status of that track
      if (item.byPos && item.byPos.length) {
        let any = false;
        for (const p of item.byPos) {
          const found = findCreditAt(item, p.pos);
          if (!found) continue;
          any = true;
          place(item, found, item.unmapped ? 'unmapped' : p.status, p.note || '', p.pos);
        }
        if (any) continue;
      }
      const found = findCredit(item);
      if (!found || found.score < 3) continue;
      place(item, found, item.unmapped ? 'unmapped' : item.status, item.note || '');
    }
    lines.forEach((allOff, el) => { if (allOff) el.classList.add('dci-dg-offline'); });
  }

  /** The credit line of an artist (or label) with a role inside the Discogs line of one track. */
  function findCreditAt(cmd, position) {
    const role = norm(cmd.base || cmd.role);
    const kind = cmd.labelId ? 'label' : 'artist';
    const entityId = cmd.labelId || cmd.artistId;
    if (!entityId) return null;
    const re = new RegExp(`/${kind}/${entityId}(?:[-/?#]|$)`);
    let best = null;
    for (const row of trackRows(position)) {
      for (const a of row.querySelectorAll(`a[href*="/${kind}/"]`)) {
        if (!re.test(a.getAttribute('href') || '')) continue;
        const line = lineOf(a, role);
        const score = role && norm(line.textContent).includes(role) ? 3 : 1;
        if (!best || score > best.score) best = { el: line, score };
      }
    }
    return best;
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

  // --- [1.8.0] Bandcamp: album and track pages of *.bandcamp.com --------------------------------------------------
  // The page's data ("data-tralbum") says which album it belongs to. The credits are lines of plain text (separated by
  // <br>), so a credit is found by the text of its line (and of the part of the line, "mixed by B" of "Written by A,
  // mixed by B"), as the dashboard read it. Marks go before each part, only into the credits; a credit from the "about"
  // text is shown by marking its sentence. Bandcamp shortens long texts ("more"): they are opened first.

  /** The album (its URL as the dashboard writes it), the track page (its path) and track number of this page. */
  function bandcampPage() {
    let data = null;
    const el = document.querySelector('[data-tralbum]');
    try {
      data = el ? JSON.parse(el.getAttribute('data-tralbum')) : null;
    } catch (e) { /* not an album or track page */ }
    const host = location.hostname.toLowerCase();
    const path = location.pathname.replace(/\/+$/, '');
    const slug = (u) => (String(u || '').match(/\/album\/([^/?#\s]+)/) || [])[1] || '';
    const isTrack = /^\/track\/[^/]+$/.test(path);
    const album = slug(path) || (isTrack && data ? slug(data.album_url) : '');
    const info = isTrack && data && (data.trackinfo || [])[0];
    return { album: album ? `https://${host}/album/${album}` : '', page: isTrack ? path : '', track: info ? String(info.track_num || '') : '' };
  }

  const bcCredits = () => document.querySelector('.tralbumData.tralbum-credits') || document.querySelector('.tralbum-credits');
  const bcAbout = () => document.querySelector('.tralbumData.tralbum-about') || document.querySelector('.tralbum-about');
  /** Lower case, one unit at a time (so the text and its places on the page stay aligned). */
  const bcLow = (t) => {
    let out = '';
    for (let i = 0; i < t.length; i++) out += t[i].toLowerCase();
    return out;
  };
  const bcNeedle = (t) => bcLow(String(t || '').replace(/\s+/g, ' ').trim());
  // Not part of the text: our marks, the "..." and the "more" link of a shortened text
  const BC_SKIP = '.dci-bc-markwrap, .dci-dg-mark, .bcTruncateEllipsis, .peekaboo-ellipsis, .peekaboo-link, script, style';

  /**
   * The text of an element as it reads: lines (at <br>) of single-spaced words in lower case, and for each character
   * its text node and offset (to put a mark there or to mark a stretch).
   */
  function bcStream(root) {
    const st = { s: '', at: [] };
    const add = (ch, node, off) => {
      st.s += ch;
      st.at.push([node, off]);
    };
    const walk = (el) => {
      for (const n of el.childNodes) {
        if (n.nodeType === 3) {
          const t = n.nodeValue;
          for (let i = 0; i < t.length; i++) {
            if (/\s/.test(t[i])) {
              if (st.s && !/[ \n]$/.test(st.s)) add(' ', n, i);
            } else {
              for (const c of t[i].toLowerCase()) add(c, n, i);
            }
          }
        } else if (n.nodeType === 1) {
          if (n.matches(BC_SKIP)) continue;
          // the "more" link right after the hidden rest of a shortened text
          if (n.previousElementSibling && n.previousElementSibling.classList.contains('bcTruncateMore')) continue;
          if (n.tagName === 'BR') {
            if (st.s.endsWith(' ')) {
              st.s = st.s.slice(0, -1);
              st.at.pop();
            }
            if (st.s && !st.s.endsWith('\n')) add('\n', n, -1);
          } else {
            walk(n);
          }
        }
      }
    };
    walk(root);
    return st;
  }

  /** Where a line of the dashboard starts in the text (the n-th line of the same text), -1 if not there. */
  function bcFindLine(st, line, n = 0) {
    const needle = bcNeedle(line);
    if (!needle) return -1;
    const whole = [];
    let loose = -1;
    for (let i = st.s.indexOf(needle); i >= 0; i = st.s.indexOf(needle, i + 1)) {
      const end = i + needle.length;
      if ((i === 0 || st.s[i - 1] === '\n') && (end === st.s.length || st.s[end] === '\n')) whole.push(i);
      else if (loose < 0) loose = i;
    }
    if (whole.length) return whole[Math.min(n || 0, whole.length - 1)];
    return loose;
  }

  /** The stretch of a part of a line: from its start (the first part: the line's) to its end, else the whole line. */
  function bcPartRange(st, at, ref) {
    const lineEnd = at + bcNeedle(ref.line).length;
    const part = bcNeedle(ref.part);
    const i = part ? st.s.indexOf(part, ref.pi ? at + 1 : at) : -1;
    if (i < 0 || i >= lineEnd) return [at, lineEnd];
    return [ref.pi ? i : at, Math.min(lineEnd, i + part.length)];
  }

  /** The sentence around a place of the text (up to ". ", "! ", "? " or the end of the line). */
  function bcSentence(st, pos) {
    const s = st.s;
    let a = pos;
    while (a > 0 && s[a - 1] !== '\n' && !(s[a - 1] === ' ' && /[.!?]/.test(s[a - 2] || ''))) a--;
    let b = pos;
    while (b < s.length && s[b] !== '\n' && !(/[.!?]/.test(s[b]) && (b + 1 === s.length || /[ \n]/.test(s[b + 1])))) b++;
    if (b < s.length && /[.!?]/.test(s[b])) b++;
    return [a, b];
  }

  /** Puts an element (or a fragment) before the character at a place of the text, not inside a marked stretch. */
  function bcInsert(st, pos, el) {
    const [node, off] = st.at[pos] || [];
    if (!node || off < 0) return false;
    let before = off ? node.splitText(off) : node;
    while (before.parentNode.matches && before.parentNode.matches(`.${BC_HL}, .${BC_OFF}`) && before.parentNode.firstChild === before) before = before.parentNode;
    before.parentNode.insertBefore(el, before);
    return true;
  }

  /** Marks a stretch of the text (each text node of it in a span of its own); returns the spans. */
  function bcWrap(st, from, to, cls) {
    const byNode = new Map();
    for (let i = from; i < to; i++) {
      const [node, off] = st.at[i] || [];
      if (!node || off < 0) continue;
      const r = byNode.get(node);
      byNode.set(node, r ? [Math.min(r[0], off), Math.max(r[1], off)] : [off, off]);
    }
    const spans = [];
    for (const [node, [a, b]] of [...byNode].reverse()) {
      const mid = a ? node.splitText(a) : node;
      if (b + 1 - a < mid.length) mid.splitText(b + 1 - a);
      const span = document.createElement('span');
      span.className = cls;
      mid.parentNode.insertBefore(span, mid);
      span.appendChild(mid);
      spans.unshift(span);
    }
    return spans;
  }

  function bcUnwrap(cls) {
    document.querySelectorAll(`.${cls}`).forEach((x) => {
      const parent = x.parentNode;
      x.replaceWith(...x.childNodes);
      parent.normalize();
    });
  }

  /** Opens the shortened credits and "about" text (Bandcamp's "more"), so marks and marked sentences can be seen. */
  function bcExpand() {
    for (const root of [bcCredits(), bcAbout()]) {
      if (!root) continue;
      root.querySelectorAll('.bcTruncateMore').forEach((more) => {
        if (more.style.display !== 'none') return;
        const link = more.nextElementSibling && more.nextElementSibling.querySelector('a');
        if (link) link.click();
        if (more.style.display !== 'none') return;
        // Bandcamp's own script did not open it: shown directly, the "..." and "more" hidden
        more.style.display = '';
        if (more.nextElementSibling) more.nextElementSibling.style.display = 'none';
        const dots = more.previousElementSibling;
        if (dots && dots.querySelector('.bcTruncateEllipsis')) dots.style.display = 'none';
      });
    }
  }

  const BC_HL = 'dci-bc-hl';
  // [1.8.1] the text of a part whose credits are all switched off
  const BC_OFF = 'dci-bc-offtext';

  function renderBandcampStatus(map) {
    ensureStyle();
    const root = bcCredits();
    if (!root) return;
    root.querySelectorAll('.dci-bc-markwrap, .dci-dg-mark').forEach((m) => m.remove());
    root.querySelectorAll(`.${BC_OFF}`).forEach((x) => x.replaceWith(...x.childNodes));
    root.normalize();
    if (!map || !map.enabled) return;
    const page = bandcampPage().page;
    const todo = [];
    (map.items || []).forEach((item, order) => (item.refs || []).forEach((r, k) => {
      if (r.about || (r.page || '') !== page) return;
      todo.push({ item, r, order: order * 1000 + k });
    }));
    if (!todo.length) return;
    bcExpand();
    const st = bcStream(root);
    const places = [];
    for (const t of todo) {
      const at = bcFindLine(st, t.r.line, t.r.n);
      if (at >= 0) places.push({ ...t, range: bcPartRange(st, at, t.r) });
    }
    places.forEach((x) => { x.pos = x.range[0]; });
    // From the end, so that the places before stay where they are; marks at the same place in their order, together
    places.sort((a, b) => b.pos - a.pos || a.order - b.order);
    const atPos = new Map();
    for (const { item, r, pos, range } of places) {
      const status = item.unmapped ? 'unmapped' : (r.status || item.status);
      const mark = document.createElement('button');
      mark.type = 'button';
      // [1.8.3] the mark itself switches the credit (no ⊘ any more); switched off: greyed
      mark.className = `dci-dg-mark dci-dg-${status} dci-bc-mark${item.off ? ' dci-mark-off' : ''}`;
      mark.dataset.row = item.row;
      mark.textContent = MARK_SYMBOL[status] || '?';
      mark.title = markTitle(map, item, status, r.note || item.note || '', item.role);
      if (!atPos.has(pos)) atPos.set(pos, { frag: document.createDocumentFragment(), range, allOff: true });
      const at = atPos.get(pos);
      at.frag.appendChild(mark);
      if (!item.off) at.allOff = false;
    }
    // From the end: a part whose credits are all off is greyed, then its marks go before it
    atPos.forEach(({ frag, range, allOff }, pos) => {
      if (allOff && range[1] > range[0]) bcWrap(st, range[0], range[1], BC_OFF);
      bcInsert(st, pos, frag);
    });
  }

  /** Shows a credit (its lines, or its sentence in the "about" text) or a track of the album. */
  function bandcampLocate(cmd) {
    ensureStyle();
    bcUnwrap(BC_HL);
    document.querySelectorAll(`.${HIGHLIGHT}`).forEach((x) => x.classList.remove(HIGHLIGHT));
    const here = bandcampPage();
    const refs = (cmd.refs || []).filter((r) => (r.page || '') === here.page);
    if (refs.length) bcExpand();
    const spans = [];
    for (const r of refs) {
      const root = r.about ? bcAbout() : bcCredits();
      if (!root) continue;
      const st = bcStream(root);
      const at = bcFindLine(st, r.line, r.n);
      if (at < 0) continue;
      const [a, b] = r.about ? bcSentence(st, bcPartRange(st, at, r)[0]) : bcPartRange(st, at, r);
      spans.push(...bcWrap(st, a, b, BC_HL));
    }
    if (spans.length) {
      spans[0].scrollIntoView({ block: 'center', behavior: 'smooth' });
      return 'credit';
    }
    const pos = String((cmd.positions || []).filter(Boolean)[0] || '');
    if (pos) {
      const row = !here.page && [...document.querySelectorAll('#track_table tr.track_row_view, tr.track_row_view')]
        .find((tr) => (String(tr.getAttribute('rel') || '').match(/tracknum=(\d+)/) || [])[1] === pos);
      const title = here.page && here.track === pos && document.querySelector('#name-section .trackTitle, h2.trackTitle');
      if (row || title) {
        highlight(row || title);
        return 'track';
      }
    }
    return 'none';
  }

  const BANDCAMP_SIDE = {
    id: 'bandcamp',
    artwork: false,
    releaseId: () => bandcampPage().album,
    /** The album page, or the track page a credit is on; null for a command that is no Bandcamp album. */
    pageFor(cmd) {
      const want = String(cmd.releaseId || '');
      const m = want.match(/^(https:\/\/[a-z0-9-]+\.bandcamp\.com)\/album\/[^/?#\s]+$/i);
      if (!m) return null;
      const here = bandcampPage();
      const onAlbum = here.album === want;
      if (cmd.loadOnly) return onAlbum ? '' : want;
      const pages = [...new Set((cmd.refs || []).map((r) => r.page || ''))];
      const pos = String((cmd.positions || []).filter(Boolean)[0] || '');
      if (onAlbum) {
        if (pages.length && pages.includes(here.page)) return '';
        if (!pages.length && (!pos || !here.page || here.track === pos)) return '';
      }
      // a credit only on track pages: the first of them; else the album page
      const page = pages.length && !pages.includes('') ? pages[0] : '';
      return page && /^\/track\/[^/?#\s]+$/.test(page) ? `${m[1]}${page}` : want;
    },
    async locate(cmd) {
      let result = 'none';
      // The page may still be getting ready after a navigation, so try a few times.
      for (let attempt = 0; attempt < 3; attempt++) {
        result = bandcampLocate(cmd);
        if (result !== 'none') return result;
        await new Promise((resolve) => setTimeout(resolve, 500));
      }
      return result;
    },
    renderStatus: (map) => renderBandcampStatus(map),
    trackAt(target) {
      const row = target.closest && target.closest('tr.track_row_view');
      return row ? (String(row.getAttribute('rel') || '').match(/tracknum=(\d+)/) || [])[1] || '' : '';
    },
  };

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
      if (stored()) GM_setValue('statusBeat', { pageId, release: mbRelease, ts: Date.now(), hidden: document.visibilityState === 'hidden' });
    };
    /**
     * "target|entry|type" of relationships; "seen" holds every entity the lookups returned, "works" the works
     * linked to each recording (for works that were new in the editor and had no MBID yet).
     */
    const addRels = (found, target, rels) => {
      found.seen.add(target);
      (rels || []).forEach((r) => {
        const et = r['target-type'];
        const e = et && (r[et] || r[et.replace('_', '-')]);
        if (e && e.id) found.keys.add(`${target}|${e.id}|${r['type-id']}`);
      });
    };
    const relKeys = (ws) => {
      const found = { keys: new Set(), seen: new Set(), works: new Map() };
      addRels(found, ws.id, ws.relations);
      if (ws['release-group']) addRels(found, ws['release-group'].id, ws['release-group'].relations);
      (ws.media || []).forEach((m) => (m.tracks || []).forEach((t) => {
        const rec = t.recording;
        if (!rec) return;
        addRels(found, rec.id, rec.relations);
        (rec.relations || []).forEach((r) => {
          if (r['target-type'] !== 'work' || !r.work) return;
          addRels(found, r.work.id, r.work.relations);
          found.works.set(rec.id, [...(found.works.get(rec.id) || []), r.work.id]);
        });
      }));
      return found;
    };
    /**
     * Composer, lyricist, publisher … are relationships of works. A work whose link to the recording is still an
     * open edit is not part of the release, and its credits are looked up on the work itself (one request per
     * second, at most 40 works).
     */
    const WORKS_MAX = 40;
    const addWorks = async (found, gids) => {
      for (const [n, gid] of gids.slice(0, WORKS_MAX).entries()) {
        if (n) await new Promise((resolve) => setTimeout(resolve, 1100));
        try {
          const res = await fetch(`/ws/2/work/${gid}?inc=artist-rels+label-rels&fmt=json`, { headers: { Accept: 'application/json' } });
          if (res.ok) addRels(found, gid, (await res.json()).relations);
        } catch (e) { /* stays as the release lookup has it */ }
      }
    };
    const targetsOf = (map, item) => item.mb.t.map((i) => (map.targets || [])[i]).filter(Boolean);
    const recordingsOf = (map, item) => (item.mb.r || []).map((i) => (map.targets || [])[i]).filter(Boolean);
    const has = (found, g, item) => found.keys.has(`${g}|${item.mb.e}|${item.mb.lt}`);
    /** A credit on the work of a recording (a work that was new in the editor): found on any work linked to it. */
    const onWorkOf = (found, rec, item) => (found.works.get(rec) || []).some((w) => has(found, w, item));
    let running = false;
    let retries = 0;
    let retryTimer = null;
    const check = async () => {
      if (running) return;
      running = true;
      let ok = true;
      try {
        ok = await checkOnce();
      } finally {
        running = false;
      }
      beat();
      // [1.8.2] MusicBrainz did not answer (e.g. too many requests): the last result stays, and it is tried again
      clearTimeout(retryTimer);
      if (ok === false && retries < 8) {
        retries++;
        retryTimer = setTimeout(check, RECHECK_MS);
      } else if (ok !== false) {
        retries = 0;
      }
    };
    const checkOnce = async () => {
      const map = stored();
      if (!map) return;
      let ws = null;
      try {
        const inc = 'artist-rels+label-rels+place-rels+series-rels+recordings+recording-level-rels+work-rels+work-level-rels+release-groups+release-group-level-rels';
        const res = await fetch(`/ws/2/release/${mbRelease}?inc=${inc}&fmt=json`, { headers: { Accept: 'application/json' } });
        if (res.ok) ws = await res.json();
      } catch (e) { /* not read: see below */ }
      // [1.8.2] Not read: the marks stay as they are – as the dashboard sent them, or as the last check found them
      // (before, a failed check later on put the unchecked marks back: ● instead of ✓)
      if (!ws) return false;
      const found = relKeys(ws);
      if (found) {
        // Work credits not found yet: their works (flagged by the dashboard, or not part of the release at all)
        const works = new Set();
        (map.items || []).forEach((item) => {
          if (!item.mb || !item.mb.t) return;
          targetsOf(map, item).forEach((g) => {
            if (!has(found, g, item) && (item.mb.w || !found.seen.has(g))) works.add(g);
          });
          recordingsOf(map, item).forEach((rec) => {
            if (!onWorkOf(found, rec, item)) (found.works.get(rec) || []).forEach((w) => works.add(w));
          });
        });
        await addWorks(found, [...works]);
      }
      const keys = found && found.keys;
      const items = (map.items || []).map((item) => {
        if (!keys || !item.mb || !item.mb.t) return item;
        const targets = targetsOf(map, item);
        const recs = recordingsOf(map, item);
        const total = targets.length + recs.length;
        if (!total) return item;
        const hits = targets.filter((g) => has(found, g, item)).length + recs.filter((rec) => onWorkOf(found, rec, item)).length;
        // Each Discogs track line on its own (its targets only); [1.8.0] so each place of a Bandcamp credit on a track page
        const each = (list) => list && list.map((p) => {
          const pt = (p.t || []).map((i) => (map.targets || [])[i]).filter(Boolean);
          const pr = (p.r || []).map((i) => (map.targets || [])[i]).filter(Boolean);
          const n = pt.length + pr.length;
          if (!n) return p;
          const h = pt.filter((g) => has(found, g, item)).length + pr.filter((rec) => onWorkOf(found, rec, item)).length;
          if (h === n) return { ...p, status: 'mb', note: '' };
          if (p.status === 'staged' || p.status === 'mb') return { ...p, status: 'pending', note: `${h}/${n}` };
          return p;
        });
        const byPos = each(item.byPos);
        // A Bandcamp place without targets of its own (album credits) takes the status of the whole credit
        const whole = hits === total ? { status: 'mb', note: '' }
          : item.status === 'staged' || item.status === 'mb' ? { status: 'pending', note: `${hits}/${total}` } : null;
        const refs = item.refs && each(item.refs).map((p) => (whole && !(p.t || []).length && !(p.r || []).length ? { ...p, ...whole } : p));
        const more = { byPos, ...(refs ? { refs } : {}) };
        if (hits === total) return { ...item, status: 'mb', note: '', ...more };
        if (item.status === 'staged' || item.status === 'mb') return { ...item, status: 'pending', note: `${hits}/${total}`, ...more };
        return { ...item, ...more };
      });
      // The dashboard may have sent a newer map meanwhile: only this release's marks are replaced
      const now = stored();
      if (now && now.ts === map.ts) {
        const checkedMap = { ...map, items, pageId, checked: Date.now(), ts: Date.now() };
        GM_setValue('statusMap', checkedMap);
        // [1.8.3] kept for the release too: "Keep marks" shows the checked state after the release page is closed
        GM_setValue(`statusMap:${mbRelease}`, checkedMap);
      }
      return true;
    };
    beat();
    setInterval(beat, 2000);
    document.addEventListener('visibilitychange', beat);
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
  else if (isBandcamp) initSourceSide(BANDCAMP_SIDE);
  else initSourceSide(DISCOGS_SIDE);
})();
