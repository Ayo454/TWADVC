from flask import Flask, jsonify, request, send_from_directory
import time
import json
import os
from flask_cors import CORS

app = Flask(__name__, static_folder='')

CORS(app)

LIVE_STATE_FILE = 'live_state.json'
SIGNALING_FILE = 'signaling_data.json'

def load_live_state():
    if os.path.exists(LIVE_STATE_FILE):
        with open(LIVE_STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        'live': False,
        'started_at': None,
        'viewers': 0,
        'video_url': 'https://www.youtube.com/embed/YOUR_LIVE_VIDEO_ID?autoplay=1&mute=0'
    }

def save_live_state(state):
    with open(LIVE_STATE_FILE, 'w') as f:
        json.dump(state, f)

def load_signaling_data():
    if os.path.exists(SIGNALING_FILE):
        with open(SIGNALING_FILE, 'r') as f:
            return json.load(f)
    return {
        'offer': None,
        'answer': None,
        'candidates': [],
        'viewer_candidates': []
    }

def save_signaling_data(data):
    with open(SIGNALING_FILE, 'w') as f:
        json.dump(data, f)

live_state = load_live_state()

# WebRTC signaling
signaling_data = load_signaling_data()

@app.route('/')
def homepage():
    return send_from_directory('.', 'index.html')

@app.route('/live')
def watch_live():
    return send_from_directory('.', 'live.html')

@app.route('/media-panel/go-live')
def go_live_panel():
    return send_from_directory('media-panel', 'go-live.html')

@app.route('/status')
def status():
    if live_state['live'] and live_state['started_at']:
        elapsed = int(time.time() - live_state['started_at'])
        viewers = max(1, int(elapsed / 5) + 1)
        live_state['viewers'] = viewers
        return jsonify(
            live=True,
            viewers=viewers,
            duration=elapsed,
            video_url=live_state['video_url']
        )

    return jsonify(live=False, viewers=0, duration=0, video_url='')

@app.route('/start-live', methods=['POST'])
def start_live():
    if not live_state['live']:
        live_state['live'] = True
        live_state['started_at'] = time.time()
        live_state['viewers'] = 1
        save_live_state(live_state)
    return jsonify(
        live=True,
        viewers=live_state['viewers'],
        video_url=live_state['video_url']
    )

@app.route('/stop-live', methods=['POST'])
def stop_live():
    live_state['live'] = False
    live_state['started_at'] = None
    live_state['viewers'] = 0
    save_live_state(live_state)
    signaling_data['offer'] = None
    signaling_data['answer'] = None
    signaling_data['candidates'] = []
    signaling_data['viewer_candidates'] = []
    save_signaling_data(signaling_data)
    return jsonify(live=False)

# WebRTC signaling endpoints
@app.route('/webrtc/offer', methods=['POST', 'OPTIONS'])
def webrtc_offer():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    data = request.get_json()
    signaling_data['offer'] = data
    save_signaling_data(signaling_data)
    return jsonify({'status': 'ok'})

@app.route('/webrtc/answer', methods=['POST', 'OPTIONS'])
def webrtc_answer():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    data = request.get_json()
    signaling_data['answer'] = data
    save_signaling_data(signaling_data)
    return jsonify({'status': 'ok'})

@app.route('/webrtc/candidate', methods=['POST', 'OPTIONS'])
def webrtc_candidate():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    data = request.get_json()
    signaling_data['candidates'].append(data)
    save_signaling_data(signaling_data)
    return jsonify({'status': 'ok'})

@app.route('/webrtc/viewer-candidate', methods=['POST', 'OPTIONS'])
def webrtc_viewer_candidate():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    data = request.get_json()
    signaling_data['viewer_candidates'].append(data)
    save_signaling_data(signaling_data)
    return jsonify({'status': 'ok'})

@app.route('/webrtc/viewer-candidates')
def get_viewer_candidates():
    return jsonify(signaling_data['viewer_candidates'])

@app.route('/webrtc/offer')
def get_offer():
    return jsonify(signaling_data['offer'] or {})

@app.route('/webrtc/answer')
def get_answer():
    return jsonify(signaling_data['answer'] or {})

@app.route('/webrtc/candidates')
def get_candidates():
    return jsonify(signaling_data['candidates'])

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=5000, debug=True)

    # For production deployment with gunicorn, use:
    # gunicorn app:app -b 0.0.0.0:$PORT
