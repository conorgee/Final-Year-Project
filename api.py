from flask import Flask, request, jsonify
from flask_cors import CORS
from summarizer import Summarizer
from transformers import pipeline
from textblob import TextBlob

# Load the summarization pipeline

app = Flask(__name__)
CORS(app)

# Initialize an empty array to store summaries
summaries = []
counter = 1
noteOpen = False

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data['text']
    num_sentencess = int(request.args.get('num_sentences', 3))  
    summarizer = Summarizer()
    summary = summarizer(text, num_sentences=num_sentencess)
    return jsonify({'summary': summary})

@app.route('/summariess', methods=['POST'])
def summariess():
    global counter
    data = request.get_json()
    text = data['text']
    summaries.append('{} - {}'.format(counter, str(text))+ '\r\n')
    counter += 1
    # Return all the summaries in the summaries array
    return jsonify({'summaries': summaries})

@app.route('/toggle_note', methods=['POST'])
def toggle_note():
    global noteOpen  # use global keyword to modify the global variable
    noteOpen = not noteOpen  # toggle the value of noteOpen
    return jsonify(noteOpen)

@app.route('/get_note', methods=['GET'])
def get_note():
    # Return all the summaries in the summaries array
    return jsonify(noteOpen)

@app.route('/get_summaries', methods=['GET'])
def get_summaries():
    # Return all the summaries in the summaries array
    return jsonify(summaries)

@app.route('/delete_summary', methods=['POST'])
def delete_summary():
    global summaries
    global counter
    counter = 1
    data = request.get_json()
    index = int(data['index'])
    if index >= 0 and index < len(summaries):
        del summaries[index]
        return jsonify({'message': 'Summary deleted successfully'})
    else:
        return jsonify({'error': 'Invalid index'})

@app.route('/abstract', methods=['POST'])
def abstract():
    data = request.get_json()
    text = data['text']
    word_count = len(text.split())
    min_lengthh = int(request.args.get('min_length', 1))  
    max_lengthh = int(request.args.get('max_length', 10))  
    if min_lengthh > word_count:
        min_lengthh = word_count
        max_lengthh = word_count
    if max_lengthh > word_count:
        max_lengthh = word_count
    abstractSum = pipeline("summarization")
    summarys = abstractSum(text, min_length=min_lengthh, max_length=max_lengthh)
    summary = summarys[0]['summary_text']
    return jsonify({'summary': summary})

@app.route('/analysis', methods=['POST'])
def analysis():
    data = request.get_json()
    text = data['text']
    # Create a TextBlob object
    blob = TextBlob(text)
    # Get the sentiment polarity (-1 to +1)
    sentiment_polarity = blob.sentiment.polarity
    # Get the emotion
    if sentiment_polarity > 0:
        emotion = "Positive"
    elif sentiment_polarity < 0:
        emotion = "Negative"
    else:
        emotion = "Neutral"
    # Get the noun phrases (entities)
    entities = [e.replace("`s", "") for e in blob.noun_phrases]
    # Get the part-of-speech tags
    pos_tags = blob.pos_tags

    results = {
        "sentiment_polarity": sentiment_polarity,
        "emotion": emotion,
        "entities": entities,
        "pos_tags": pos_tags
    }
    # Return the results as JSON
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
