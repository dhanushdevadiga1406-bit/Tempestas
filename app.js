const map = L.map('map', { worldCopyJump: true }).setView([20, 0], 2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

L.control.scale({ metric: true, imperial: false }).addTo(map);

let marker = null;

const elSummary = document.getElementById('summary');
const elResults = document.getElementById('results');

document.getElementById('searchForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const q = document.getElementById('placeInput').value.trim();
  if (!q) return;

  elSummary.textContent = 'Loading…';
  elResults.innerHTML = '';

  try {
    const res = await fetch(`/api/weather?place=${encodeURIComponent(q)}`);
    const data = await res.json();
    if (!res.ok) {
      elSummary.textContent = data.error || 'Error fetching data';
      return;
    }

    if (marker) map.removeLayer(marker);
    marker = L.marker([data.lat, data.lon])
      .addTo(map)
      .bindPopup(`<b>${data.place}</b><br>${data.summary || ''}`)
      .openPopup();

    map.setView([data.lat, data.lon], 8);

    elSummary.textContent = data.summary || '';

    // Render structured HTML instead of raw JSON
    const cw = data.weather.current_weather || {};
    const daily = data.weather.daily || {};

    const maxTemp = daily.temperature_2m_max ? daily.temperature_2m_max[0] : 'N/A';
    const minTemp = daily.temperature_2m_min ? daily.temperature_2m_min[0] : 'N/A';
    const precip = daily.precipitation_sum ? daily.precipitation_sum[0] : 'N/A';

    elResults.innerHTML = `
      <div style="font-family: inherit; line-height: 1.6;">
        <p style="margin: 4px 0;"><strong>Temperature:</strong> ${cw.temperature ?? 'N/A'} °C</p>
        <p style="margin: 4px 0;"><strong>Wind Speed:</strong> ${cw.windspeed ?? 'N/A'} km/h</p>
        <p style="margin: 4px 0;"><strong>High / Low:</strong> ${maxTemp} °C / ${minTemp} °C</p>
        <p style="margin: 4px 0;"><strong>Precipitation:</strong> ${precip} mm</p>
      </div>
    `;
  } catch (err) {
    elSummary.textContent = 'Network error';
  }
});