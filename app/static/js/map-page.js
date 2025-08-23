document.addEventListener('DOMContentLoaded', async () => {

    const el = document.getElementById('map-page');

    const map = L.map('map-page').setView([42.6977, 23.3219], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19, attribution: '© OpenStreetMap'
    }).addTo(map);

    const res = await fetch('/api/listings');
    const data = await res.json();

    const pts = [];
    for (const listing of data) {
        const lat = Number(listing.lat), lng = Number(listing.lng);
        
        console.log(listing.picture)
        const html_for_hovering = listing.picture
        ? `<div class="listing-content" style="max-width:250px"><img src="${listing.picture}" width="100" style="border-radius:4px;display:block"><div class="lf-title">${listing.title ?? ''}</div>
      <div class="lf-date">Изгубено на: ${listing.date ?? ''}</div></div>`
        : `<div class="listing-content" style="max-width:250px"><div class="lf-title">${listing.title ?? ''}</div>
      <div class="lf-date">Изгубено на: ${listing.date ?? ''}</div></div>`;
        const m = L.marker([lat, lng]).addTo(map);
        m.bindTooltip(html_for_hovering, {direction: 'top', sticky:true, className:'listing-content'})

        if (listing.url)
             m.on('click', () => { location.href = listing.url; });

        pts.push([lat, lng]);
    }

    if (pts.length) map.fitBounds(L.latLngBounds(pts).pad(0.15));
})
