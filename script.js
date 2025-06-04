window.addEventListener('load', function() {
    const numCoins = 20;
    for (let i = 0; i < numCoins; i++) {
        const coin = document.createElement('div');
        coin.classList.add('coin');
        coin.style.left = Math.random() * 100 + 'vw';
        coin.style.animationDelay = Math.random() * 2 + 's';
        document.body.appendChild(coin);
    }
    setTimeout(() => {
        document.querySelectorAll('.coin').forEach(c => c.remove());
    }, 5000);
});