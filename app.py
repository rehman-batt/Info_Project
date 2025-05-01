from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_talisman import Talisman  # Secure HTTP headers
import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from kyber_py.kyber import Kyber512

app = Flask(__name__)

# csp = {
#     'default-src': ['\'self\''],
#     'img-src': ['\'self\'', 'https://img.icons8.com'],
#     'style-src': ['\'self\'', 'https://fonts.googleapis.com', '\'unsafe-inline\''], 
#     'font-src': ['\'self\'', 'https://fonts.gstatic.com'],
#     'script-src': ['\'self\'', '\'unsafe-inline\''],  
# }

csp = {
    'default-src': ['*'],
    'img-src': ['*'],
    'style-src': ['*'],
    'font-src': ['*'],
    'script-src': ['*'],
}


talisman = Talisman(app, content_security_policy=csp)

CORS(app, origins="http://localhost:5000")

# Store keys and ciphertexts temporarily in memory (for demo)
session_data = {
    'pk': None,
    'sk': None,
    'key': None,
    'nonce': None,
    'plain_text': None,
    'cipher': None,
}

@app.route('/generate_keys', methods=['POST'])
def generate_keys():
    pk, sk = Kyber512.keygen()
    session_data['pk'] = pk
    session_data['sk'] = sk

    # For demo, also generate a shared key immediately
    key, c = Kyber512.encaps(pk)
    _key = Kyber512.decaps(sk, c)

    assert key == _key  # Sanity check

    session_data['key'] = key

    # Return Base64 encoded keys (for readability)
    return jsonify({
        'public_key': base64.b64encode(pk).decode(),
        'private_key': base64.b64encode(sk).decode()
    })

@app.route('/encrypt', methods=['POST'])
def encrypt_text():
    data = request.get_json()
    plaintext = data.get('text', '').encode()

    if not session_data['key']:
        return jsonify({'error': 'Keys not generated yet.'}), 400

    nonce = os.urandom(12)
    aesgcm = AESGCM(session_data['key'])
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    # Save nonce for decryption
    session_data['nonce'] = nonce
    session_data['plain_text'] = plaintext
    session_data['cipher'] = ciphertext

    # Return Base64 encoded ciphertext
    return jsonify({
        'encrypted': base64.b64encode(ciphertext).decode()
    })

@app.route('/decrypt', methods=['POST'])
def decrypt_text():
    ciphertext = session_data['cipher']

    if not session_data['key'] or not session_data['nonce'] or not session_data['cipher']:
        return jsonify({'error': 'Encryption must be done first.'}), 400

    try:
        aesgcm = AESGCM(session_data['key'])
        decrypted = aesgcm.decrypt(session_data['nonce'], ciphertext, None)
        return jsonify({'decrypted': decrypted.decode()})
    except Exception as e:
        # Log the exception for internal use (don't expose it to users)
        app.logger.error(f"Decryption failed: {str(e)}")
        return jsonify({'error': 'Decryption failed. Please try again.'}), 400

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, ssl_context="adhoc")  
