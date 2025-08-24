document.addEventListener('DOMContentLoaded', function () {
  const coordXInput = document.getElementById('coordinateX');
  const coordYInput = document.getElementById('coordinateY');

  const startLat = parseFloat(coordXInput.value) || 42.6977;
  const startLng = parseFloat(coordYInput.value) || 23.3219;
  
  const map = L.map('map').setView([startLat, startLng], 13);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
  }).addTo(map);

  const marker = L.marker([startLat, startLng], {
    draggable: true
  }).addTo(map);

  function updateInputs(latlng) {
    coordXInput.value = latlng.lat.toFixed(6);
    coordYInput.value = latlng.lng.toFixed(6);
  }

  marker.on('dragend', function (e) {
    updateInputs(e.target.getLatLng());
  });
});

document.addEventListener('DOMContentLoaded', function () {
  const mapDiv = document.getElementById('map-display-details');
  
  if (mapDiv) {
    const lat = parseFloat(mapDiv.dataset.lat);
    const lng = parseFloat(mapDiv.dataset.lng);
    const map = L.map('map-display-details').setView([lat, lng], 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
    }).addTo(map);
    L.marker([lat, lng], { draggable: false }).addTo(map);
  }
});