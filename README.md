# AI-Emotion-Detector
A web application that detects and quantifies emotions (anger, disgust, fear, joy, and sadness) expressed in a piece of text, built using IBM Watson NLP's Embeddable AI library. The application is packaged as a reusable Python module, deployed as a Flask web service, and includes error handling, unit tests, and static code analysis.




Project Overview

This project was built as part of a hands-on capstone on developing and deploying AI-powered applications. It demonstrates an end-to-end workflow:


Emotion detection – Calling the Watson NLP EmotionPredict function to analyze text and return scores for five emotions.
Output formatting – Parsing the raw API response into a clean, structured JSON output that also identifies the dominant emotion.
Packaging – Structuring the code as an installable Python package (EmotionDetection) with a proper __init__.py.
Unit testing – Verifying the emotion detector against known inputs using Python's unittest framework.
Web deployment – Exposing the emotion detector through a Flask web server with a simple front-end interface.
Error handling – Gracefully handling blank/invalid input with an appropriate HTTP status code (400) and user-facing message.
Static code analysis – Running pylint against the codebase to check code quality and maintainability.


Features


Detects five core emotions: anger, disgust, fear, joy, sadness
Returns the dominant emotion alongside individual emotion scores
Simple REST-style Flask endpoint for real-time text analysis
Input validation and error handling for blank/invalid text
Unit-tested core logic
Clean, pylint-verified codebase


Project Structure

Emotion_detection/
│
├── EmotionDetection/
│   ├── __init__.py              # Package initializer, imports emotion_detector
│   └── emotion_detection.py     # Core emotion detection logic (Watson NLP call + formatting + error handling)
│
├── test_emotion_detection.py    # Unit tests for the emotion detector
├── server.py                    # Flask application exposing the emotion detector as a web service
├── requirements.txt              # Python dependencies
└── README.md

Technologies Used


Python 3
IBM Watson NLP (Embeddable AI library / EmotionPredict function)
Flask – for web deployment
unittest – for unit testing
pylint – for static code analysis


How It Works


The user submits a piece of text through the web interface (or directly to the /emotionDetector endpoint).
The Flask server passes the text to the emotion_detector function in the EmotionDetection package.
emotion_detector sends the text to the Watson NLP EmotionPredict service and receives raw emotion scores.
The function formats the response into a clean JSON object containing:

anger
disgust
fear
joy
sadness
dominant_emotion



If the input text is blank, the function returns None values for all emotions and the server responds with a 400 Bad Request status and an appropriate error message.
The formatted result is returned to the user via the web interface.


Example Output

json{
  "anger": 0.006,
  "disgust": 0.006,
  "fear": 0.06,
  "joy": 0.944,
  "sadness": 0.002,
  "dominant_emotion": "joy"
}

Running the Application Locally


Clone the repository:


bash   git clone <your-repo-url>
   cd Emotion_detection


Install dependencies:


bash   pip install -r requirements.txt


Run the Flask server:


bash   python server.py


Open your browser and navigate to:


   http://localhost:5000

Running Unit Tests

bashpython -m unittest test_emotion_detection.py

Running Static Code Analysis

bashpylint server.py

Error Handling

Submitting blank text to the application returns:

json{
  "anger": null,
  "disgust": null,
  "fear": null,
  "joy": null,
  "sadness": null,
  "dominant_emotion": null
}

along with an HTTP 400 status code and the message:


"Invalid text! Please try again!"



Author

Developed as part of a final project on building AI-powered applications with IBM Watson NLP.

