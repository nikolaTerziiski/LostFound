document.addEventListener('DOMContentLoaded', function () {
  const map = L.map('map').setView([42.6977, 23.3219], 13);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
  }).addTo(map);

  const marker = L.marker([42.6977, 23.3219], {
    draggable: true
  }).addTo(map);
  
  const coordXInput = document.getElementById('coordinateX');
  const coordYInput = document.getElementById('coordinateY');

  function updateInputs(latlng) {
    coordXInput.value = latlng.lat.toFixed(6);
    coordYInput.value = latlng.lng.toFixed(6);
  }

  updateInputs(marker.getLatLng());
  
  marker.on('dragend', function(e) {
    updateInputs(e.target.getLatLng());
  });
});