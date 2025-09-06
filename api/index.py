from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def health_check():
    return {'status': 'ok', 'message': 'SynergySphere API'}

if __name__ == '__main__':
    app.run(debug=True)