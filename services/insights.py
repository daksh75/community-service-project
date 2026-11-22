import os

def build_insights(data):
    aqi = data.get('ow_aqi', 0)
    labels = {1:'Good', 2:'Fair', 3:'Moderate', 4:'Poor', 5:'Very Poor'}
    tips = {
        1: 'Air quality is currently good. Normal outdoor activities are generally suitable.',
        2: 'Air quality is fair. Most people can continue normal outdoor activities.',
        3: 'Sensitive people may wish to reduce prolonged or heavy outdoor exertion if they notice symptoms.',
        4: 'Consider reducing prolonged outdoor exertion. Sensitive groups should take extra care.',
        5: 'Avoid or reduce outdoor exertion, especially for children, older adults and people with respiratory or heart conditions.'
    }
    weather = data.get('weather', {})
    return {'category': labels.get(aqi, 'Unavailable'), 'advice': tips.get(aqi, 'No advice available.'),
            'summary': f"The reported OpenWeather air-quality index is {labels.get(aqi, 'unavailable')} (level {aqi}). "
                       f"Temperature is {weather.get('temperature', 'N/A')}°C with {weather.get('humidity', 'N/A')}% humidity."
                       , 'note': 'This is OpenWeather’s 1–5 air-quality scale, not India’s CPCB AQI scale.'}

def answer_with_gemini(question, data):
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        raise RuntimeError('Gemini is not configured. Add GEMINI_API_KEY to .env to enable the AI assistant.')
    from google import genai
    client = genai.Client(api_key=key)
    prompt = (
        'You are an air-quality information assistant. Explain the supplied live data clearly, '
        'do not claim to diagnose or guarantee safety, and do not invent pollution sources. '
        'Mention that OpenWeather AQI is a 1–5 scale when relevant. Give cautious, practical guidance.\n\n'
        f'Current location data: {data}\nUser question: {question}'
    )
    response = client.models.generate_content(model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'), contents=prompt)
    return response.text or 'The assistant could not generate a response.'
