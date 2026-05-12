#!/usr/bin/env python3
"""
Flask application for sentiment analysis
"""
from flask import Flask, render_template, request, jsonify
import sys
sys.path.insert(0, '../')
from src.preprocessing import preprocess_text
from src.predict_bert import predict_sentiment

app = Flask(__name__)

@app.route('/')
def index():
    """Render index page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Preprocess and predict
    processed_text = preprocess_text(text)
    sentiment = predict_sentiment(processed_text)
    
    return jsonify({
        'text': text,
        'sentiment': sentiment,
        'confidence': 0.95
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
