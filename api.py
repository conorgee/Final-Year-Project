# Import required libraries
import textwrap
from flask import Flask, request, jsonify
from flask_cors import CORS
from summarizer import Summarizer
from transformers import pipeline, AutoTokenizer
from textblob import TextBlob

# Load the summarization pipeline
app = Flask(__name__)
CORS(app)
abstractSum = pipeline("summarization", model="t5-base")

# Initialize an empty array to store summaries
summaries = []
noteOpen = False
summarizer = Summarizer()

# Define endpoint to summarize text
@app.route("/summarize", methods=["POST"])
def summarize():
    global summarizer
    # Get input text and number of sentences to summarize
    data = request.get_json()
    text = data["text"]
    # Default value for num sentences is 3 
    num_sentencess = int(request.args.get("num_sentences", 3))
    # Summarize the input text
    summary = summarizer(text, num_sentences=num_sentencess)
    # Return the summary in JSON format
    return jsonify({"summary": summary})

# Define endpoint to add input text to the list of summaries
@app.route("/summariess", methods=["POST"])
def summariess():
    # Get input text
    data = request.get_json()
    text = data["text"]
    # Append the input text to the list of summaries
    summaries.append("{}".format(str(text)) + "\r\n")
    # Return all the summaries in the summaries array in JSON format
    return jsonify({"summaries": summaries})

# Define endpoint to toggle the noteOpen variable
@app.route("/toggle_note", methods=["POST"])
def toggle_note():
    global noteOpen  # use global keyword to modify the global variable
    # Toggle the value of noteOpen
    noteOpen = not noteOpen
    # Return the updated value of noteOpen in JSON format
    return jsonify(noteOpen)

# Define endpoint to get the value of noteOpen
@app.route("/get_note", methods=["GET"])
def get_note():
    # Return the value of noteOpen in JSON format
    return jsonify(noteOpen)

# Define endpoint to get the list of summaries with their corresponding index numbers
@app.route("/get_summaries", methods=["GET"])
def get_summaries():
    summary_list = []
    # Loop through the list of summaries and add them with their index numbers to summary_list
    for i, summary in enumerate(summaries, start=1):
        summary_list.append("{} - {}".format(i, summary))
    # Return the list of summaries in summary_list in JSON format
    return jsonify(summary_list)


# Define a route to delete a summary
@app.route("/delete_summary", methods=["POST"])
def delete_summary():
    global summaries
    # Get the index of the summary to delete from the request data
    data = request.get_json()
    index = int(data["index"])
    # Check if the index is valid, then delete the corresponding summary
    if index >= 0 and index < len(summaries):
        del summaries[index]
        return jsonify({"message": "Summary deleted successfully"})
    else:
        return jsonify({"error": "Invalid index"})

# Define a route to generate an abstract summary
@app.route("/abstract", methods=["POST"])
def abstract():
    global abstractSum
    # Get the input text and the min/max length for the summary from the request data
    data = request.get_json()
    text = data["text"]
    word_count = len(text.split())
    min_lengthh = int(request.args.get("min_length", 1))
    max_lengthh = int(request.args.get("max_length", 30))
    # Load the T5 tokenizer
    tokenizer = AutoTokenizer.from_pretrained("t5-base")
    # Encode the input text using the tokenizer
    encoded = tokenizer.encode(data["text"], add_special_tokens=True)
    # Compute the length of the tokenized sequence
    seq_length = len(encoded)
    # Adjust the min/max length if they exceed the word count of the input text
    if min_lengthh > word_count:
        min_lengthh = word_count
        max_lengthh = word_count
    if max_lengthh > word_count:
        max_lengthh = word_count
    # Split the text into smaller sequences of length 500 if it exceeds sequence length 500
    # Split text into sequences of length 500
    text_sequences = [text[i:i+500] for i in range(0, len(text), 500)]
        # Initialize a list to store the summaries
    summariess = []
    # Loop through each sequence
    for sequence in text_sequences:
        # Tokenize the sequence using the T5 tokenizer
        encoded = tokenizer.encode(sequence, add_special_tokens=True)
        # Compute the min/max length for the summary
        max = round((2 + len(encoded)) * (max_lengthh / word_count))
        min = round((2 + len(encoded)) * (min_lengthh / word_count))
        # Generate the summary using the T5 summarization pipeline
        summary = abstractSum(sequence, min_length=min, max_length=max)[0][
            "summary_text"
        ]
        summariess.append(summary)

    # Concatenate the summaries
    summary = " ".join(summariess)
    # Return the summary as a JSON response
    return jsonify({"summary": summary})

# Define a route for the analysis endpoint that accepts a POST request
@app.route("/analysis", methods=["POST"])
def analysis():
    # Extract the text data from the request body
    data = request.get_json()
    text = data["text"]

    # Create a TextBlob object
    blob = TextBlob(text)

    # Get the sentiment polarity (-1 to +1)
    sentiment_polarity = blob.sentiment.polarity

    # Determine the emotion based on the sentiment polarity
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

    # Create a dictionary with the analysis results
    results = {
        "sentiment_polarity": sentiment_polarity,
        "emotion": emotion,
        "entities": entities,
        "pos_tags": pos_tags,
    }

    # Return the analysis results as JSON
    return jsonify(results)

# Start the Flask application if the script is executed directly
if __name__ == "__main__":
    app.run(debug=True)