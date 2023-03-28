from flask import Flask, request, jsonify
from flask_cors import CORS
from summarizer import Summarizer

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

if __name__ == '__main__':
    app.run(debug=True)
