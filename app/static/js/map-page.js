document.addEventListener('DOMContentLoaded', async function (){
    const mapDiv = document.getElementById('map-page');

    const map = L.map('map-page').setView([42.6977, 23.3219],11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
    }).addTo(map);

    const res = await fetch('/api/listings');
    const data = await res.json();
})