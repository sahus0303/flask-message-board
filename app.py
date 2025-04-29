from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Store up to 488 messages with signature
normal_messages = []
vip_titles = ['DM', 'PS (D)', 'PS (DD)', 'CDF', 'COA', 'CAF', 'CNV', 'CDIS']
vip_messages = {}  # title -> message dict

@app.route('/')
def home():
    return '<h1>Welcome to the Message Board</h1><p>Go to /form_normal or /form_vip to submit, or /board to view the board.</p>'

@app.route('/form_normal')
def form_normal():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
      <title>Public Message</title>
      <script src="https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js"></script>
      <style>
        #signatureCanvas {
          border: 1px solid #ccc;
          width: 300px;
          height: 100px;
          touch-action: none;
        }
      </style>
    </head>
    <body>
    <h2>Submit a Public Message with Signature</h2>
    <form id="form">
      <input type="text" id="message" required maxlength="100" placeholder="Type your message"><br><br>
      <label>Sign below:</label><br>
      <canvas id="signatureCanvas" width="300" height="100"></canvas><br>
      <button type="button" onclick="clearSignature()">Clear Signature</button><br><br>
      <button type="submit">Send</button>
    </form>

    <script>
      const canvas = document.getElementById("signatureCanvas");
      const signaturePad = new SignaturePad(canvas);

      function clearSignature() {
        signaturePad.clear();
      }

      document.getElementById('form').addEventListener('submit', async (e) => {
        e.preventDefault();
        if (signaturePad.isEmpty()) {
          alert("Please provide a signature.");
          return;
        }

        const message = document.getElementById('message').value;
        const signatureDataURL = signaturePad.toDataURL();

        await fetch('/submit_normal', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message, signature: signatureDataURL })
        });

        alert('Submitted!');
        document.getElementById('message').value = '';
        signaturePad.clear();
      });
    </script>
    </body>
    </html>
    '''

@app.route('/form_vip')
def form_vip():
    title_options = ''.join(f'<option value="{t}">{t}</option>' for t in vip_titles)
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
      <title>VIP Message</title>
      <script src="https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js"></script>
      <style>
        #signatureCanvas {{
          border: 1px solid #ccc;
          width: 300px;
          height: 100px;
          touch-action: none;
        }}
      </style>
    </head>
    <body>
    <h2>Submit a VIP Message</h2>
    <form id="form">
      <label>Select VIP Title:</label><br>
      <select id="vipTitle">{title_options}</select><br><br>

      <label>Message:</label><br>
      <input type="text" id="message" required maxlength="100" placeholder="Type your message"><br><br>

      <label>Sign below:</label><br>
      <canvas id="signatureCanvas" width="300" height="100"></canvas><br>
      <button type="button" onclick="clearSignature()">Clear Signature</button><br><br>
      <button type="submit">Send</button>
    </form>

    <script>
      const canvas = document.getElementById("signatureCanvas");
      const signaturePad = new SignaturePad(canvas);

      function clearSignature() {{
        signaturePad.clear();
      }}

      document.getElementById('form').addEventListener('submit', async (e) => {{
        e.preventDefault();
        if (signaturePad.isEmpty()) {{
          alert("Please provide a signature.");
          return;
        }}

        const title = document.getElementById('vipTitle').value;
        const message = document.getElementById('message').value;
        const signatureDataURL = signaturePad.toDataURL();

        const response = await fetch('/submit_vip', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ title, message, signature: signatureDataURL }})
        }});

        const result = await response.json();
        if (result.status === 'success') {{
          alert('Submitted!');
          document.getElementById('message').value = '';
          signaturePad.clear();
        }} else {{
          alert('That VIP title already has a message or input is invalid.');
        }}
      }});
    </script>
    </body>
    </html>
    '''

@app.route('/submit_normal', methods=['POST'])
def submit_normal():
    data = request.get_json()
    message = data.get('message')
    signature = data.get('signature')

    if message and signature and len(normal_messages) < 488:
        normal_messages.append({'message': message, 'signature': signature})
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

@app.route('/submit_vip', methods=['POST'])
def submit_vip():
    data = request.get_json()
    title = data.get('title')
    message = data.get('message')
    signature = data.get('signature')

    if title in vip_titles and message and signature and title not in vip_messages:
        vip_messages[title] = {'message': message, 'signature': signature}
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

@app.route('/board')
def board():
    formatted = [f"{entry['signature']}|||{entry['message']}" for entry in normal_messages]
    return render_template('board_layout_488.html', messages=formatted, vip_messages=vip_messages)

if __name__ == '__main__':
    app.run(debug=True)
