from flask import Flask, request, jsonify
from flask_cors import CORS  # Installed via: pip install flask-cors
import os
import requests

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # Enables cross-origin requests from Live Server (:5500)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/weather')
def weather():
    place = request.args.get('place')
    if not place:
        return jsonify({'error': 'place query parameter required'}), 400

    # Geocode with Nominatim (OpenStreetMap)
    nom_url = 'https://nominatim.openstreetmap.org/search'
    try:
        r = requests.get(
            nom_url,
            params={'q': place, 'format': 'json', 'limit': 1},
            headers={'User-Agent': 'tempestas-app'}
        )
        r.raise_for_status()
    except Exception:
        return jsonify({'error': 'geocoding service error'}), 502

    results = r.json()
    if not results:
        return jsonify({'error': 'place not found'}), 404

    loc = results[0]
    lat = float(loc['lat'])
    lon = float(loc['lon'])
    display_name = loc.get('display_name', place)

    # Fetch weather from Open-Meteo
    om_url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        'latitude': lat,
        'longitude': lon,
        'current_weather': True,
        'hourly': 'temperature_2m,relativehumidity_2m,precipitation',
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
        'timezone': 'auto'
    }
    try:
        wr = requests.get(om_url, params=params)
        wr.raise_for_status()
    except Exception:
        return jsonify({'error': 'weather service error'}), 502

    weather_data = wr.json()

    # Generate summary using Gemini API if configured
    summary = None
    gemini_key = os.getenv('GEMINI_API_KEY')
    gemini_endpoint = os.getenv('GEMINI_ENDPOINT')

    if gemini_key and gemini_endpoint:
        try:
            prompt_text = f"Summarize the current weather briefly in 1 sentence for {display_name} using this data: {weather_data.get('current_weather')}"
            
            # Standard Gemini API Payload Format
            payload = {
                "contents": [
                    {
                        "parts": [{"text": prompt_text}]
                    }
                ]
            }

            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': gemini_key
            }

            gresp = requests.post(gemini_endpoint, headers=headers, json=payload, timeout=5)
            
            if gresp.status_code == 200:
                res_data = gresp.json()
                # Extract response text from standard Gemini JSON structure
                summary = res_data['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            summary = None

    # Fallback lightweight summary if Gemini call is unconfigured or fails
    if not summary:
        cw = weather_data.get('current_weather', {})
        if cw:
            summary = f"{cw.get('temperature')} °C, wind {cw.get('windspeed')} km/h"

    return jsonify({
        'place': display_name,
        'lat': lat,
        'lon': lon,
        'weather': weather_data,
        'summary': summary
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)