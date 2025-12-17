import requests

tests = [
    'I love this product! It is amazing!',
    'This is terrible. I am very disappointed.',
    'The best purchase I have ever made!',
    'Waste of money. Do not buy it.',
    'It is okay, nothing special.'
]

print('=' * 60)
print('RESULTATS DES TESTS - Sentiment Analysis FHE')
print('=' * 60)

for text in tests:
    r = requests.post('http://localhost:8000/analyze', json={'text': text})
    data = r.json()
    emoji = '[+]' if data['sentiment'] == 'Positive' else '[-]'
    print(f'\n{emoji} Texte: "{text}"')
    print(f'   Sentiment: {data["sentiment"]}')
    print(f'   Confiance: {data["confidence"]:.1f}%')
    print(f'   Proba Positive: {data["proba_positive"]*100:.1f}%')
    print(f'   Proba Negative: {data["proba_negative"]*100:.1f}%')
    print(f'   Temps: {data["processing_time"]*1000:.0f}ms')

print('\n' + '=' * 60)
print('Tests termines avec succes!')

