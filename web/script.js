/*
 * Projekt BitsCoin 2025
 * Autorzy: Grupa Siedemtrzy
 */
document.addEventListener('DOMContentLoaded', () => {
  const statsDiv = document.getElementById('stats-content');
  statsDiv.textContent = 'Ładuję dane z lokalnego eksplorera…';
  fetch('https://explorer.bitscoin.pl/api/blocks')
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(chain => {
      const latest = chain[chain.length - 1];
      statsDiv.innerHTML = `
        <ul>
          <li>Aktualny blok: ${latest.index}</li>
          <li>Hash: ${latest.hash}</li>
          <li>Czas: ${new Date(latest.timestamp * 1000).toLocaleString()}</li>
          <li>Podaż: ${(chain.length - 1) * 50 + 5000} BSC</li>
        </ul>
      `;
    })
    .catch(err => {
      statsDiv.textContent = 'Błąd ładowania statystyk: ' + err;
      console.error(err);
    });
});
