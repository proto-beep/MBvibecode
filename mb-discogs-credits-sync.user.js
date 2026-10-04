// ==UserScript==
// @name         MB x Vibecode: Import Discogs credits COMPANION
// @namespace    https://github.com/proto-beep/MBvibecode
// @version      0.3.0
// @date         2026-10-01
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

  function initMusicBrainzSide() {
    const send = (msg) => document.dispatchEvent(new CustomEvent('dci:from-discogs', { detail: JSON.stringify(msg) }));

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

    const pickTab = (tabs) => [...tabs].sort((a, b) => (Number(b.visible) - Number(a.visible)) || (b.lastVisible - a.lastVisible))[0] || null;

    const status = () => {
      const tabs = liveTabs();
      const target = pickTab(tabs);
      send({
        type: 'status',
        tabs: tabs.length,
        target: target && { id: target.id, visible: target.visible, releaseId: target.releaseId },
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
      } else if (msg.type === 'show') {
        const target = pickTab(liveTabs());
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
      if (String(cmd.releaseId) !== currentReleaseId()) {
        // Load the release first; the command is picked up again after the navigation.
        sessionStorage.setItem('dci-pending', JSON.stringify(cmd));
        report(cmd, 'loading');
        location.assign(`${location.origin}/release/${cmd.releaseId}`);
        return;
      }
      report(cmd, await locateWithRetry(cmd));
    };

    GM_addValueChangeListener('cmd', (name, oldValue, cmd) => {
      if (cmd && cmd.target === tabId) handle(cmd);
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
      }`;
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
  if (isMusicBrainz) initMusicBrainzSide();
  else initDiscogsSide();
})();
