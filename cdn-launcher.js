(() => {
  const PLAYER_VERSION = 'b39ce5f';
  const PLAYER = 'cdn-player-v2.html?v=' + PLAYER_VERSION + '&game=';

  const playerUrl = (path) => PLAYER + encodeURIComponent(path || '');

  const prewarm = (path) => {
    if (!path) return;
    try {
      const link = document.createElement('link');
      link.rel = 'prefetch';
      link.href = playerUrl(path);
      document.head.appendChild(link);
    } catch (_) {}
  };

  const toPlayer = (path) => {
    if (!path) return;
    location.href = playerUrl(path);
  };

  document.addEventListener('pointerdown', (event) => {
    const play = event.target.closest('[data-play]');
    if (play) prewarm(play.dataset.play);
  }, { capture: true, passive: true });

  document.addEventListener('click', (event) => {
    const play = event.target.closest('[data-play]');
    if (play) {
      event.preventDefault();
      event.stopImmediatePropagation();
      toPlayer(play.dataset.play);
      return;
    }

    const spotlight = event.target.closest('#spotlightPlay');
    if (spotlight) {
      event.preventDefault();
      event.stopImmediatePropagation();
      const name = document.getElementById('spotlightName')?.textContent?.trim();
      if (!name || name.startsWith('Loading')) return;
      Promise.all([
        fetch('games.json', { cache: 'no-store' }).then(r => r.ok ? r.json() : []),
        fetch('ai-games.json', { cache: 'no-store' }).then(r => r.ok ? r.json() : []).catch(() => [])
      ]).then(([main, ai]) => {
        const game = [...main, ...ai].find(g => g.name === name);
        if (game) toPlayer(game.path);
      }).catch(() => {});
    }
  }, true);
})();
