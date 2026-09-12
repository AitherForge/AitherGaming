(() => {
  const PLAYER = 'cdn-player.html?game=';
  const toPlayer = (path) => {
    if (!path) return;
    location.href = PLAYER + encodeURIComponent(path);
  };

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
