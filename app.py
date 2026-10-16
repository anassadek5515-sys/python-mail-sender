from flask import Flask, render_template_string, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>B2B Python Mail Server</title>
    <style>
        body { font-family: Tahoma, Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px; margin: 0; }
        .container { max-width: 600px; margin: 0 auto; background: #1e293b; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h2 { text-align: center; color: #38bdf8; margin-top: 0; }
        label { display: block; margin-top: 15px; font-weight: bold; color: #94a3b8; }
        input, textarea { width: 100%; padding: 12px; margin-top: 5px; border-radius: 8px; border: 1px solid #334155; background-color: #0f172a; color: #fff; box-sizing: border-box; font-size: 14px; }
        button { width: 100%; padding: 14px; background-color: #2563eb; color: white; border: none; border-radius: 8px; margin-top: 20px; font-size: 16px; font-weight: bold; cursor: pointer; transition: background 0.3s; }
        button:hover { background-color: #1d4ed8; }
        .status { margin-top: 15px; padding: 12px; border-radius: 8px; display: none; text-align: center; font-weight: bold; }
        .success { background-color: #065f46; color: #34d399; }
        .error { background-color: #991b1b; color: #fca5a5; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🚀 Python B2B Mail Server</h2>
        <form id="emailForm">
            <label>مضيف SMTP (Host):</label>
            <input type="text" id="smtpHost" value="smtp.gmail.com" required>

            <label>المنفذ (Port):</label>
            <input type="number" id="smtpPort" value="587" required>

            <label>البريد المُرسِل (Username):</label>
            <input type="email" id="smtpUser" placeholder="your-email@gmail.com" required>

            <label>كلمة المرور / App Password:</label>
            <input type="password" id="smtpPass" placeholder="******" required>

            <hr style="border: 0.5px solid #334155; margin-top: 20px;">

            <label>إيميل المستلم (Recipient):</label>
            <input type="email" id="toEmail" placeholder="client@company.com" required>

            <label>عنوان الرسالة (Subject):</label>
            <input type="text" id="subject" placeholder="عروض B2B" required>

            <label>محتوى الرسالة (Body):</label>
            <textarea id="body" rows="6" placeholder="اكتب نص الرسالة هنا..." required></textarea>

            <button type="submit" id="sendBtn">إرسال عبر السيرفر 📤</button>
        </form>
        <div id="statusBox" class="status"></div>
    </div>

    <script>
        document.getElementById('emailForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const statusBox = document.getElementById('statusBox');
            statusBox.style.display = 'block';
            statusBox.className = 'status';
            statusBox.style.background = '#334155';
            statusBox.style.color = '#38bdf8';
            statusBox.innerText = 'جاري الإرسال عبر السيرفر... ⏳';

            const data = {
                host: document.getElementById('smtpHost').value,
                port: document.getElementById('smtpPort').value,
                user: document.getElementById('smtpUser').value,
                pass: document.getElementById('smtpPass').value,
                to: document.getElementById('toEmail').value,
                subject: document.getElementById('subject').value,
                body: document.getElementById('body').value
            };

            try {
                const response = await fetch('/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                if (result.success) {
                    statusBox.className = 'status success';
                    statusBox.innerText = '✅ ' + result.message;
                } else {
                    statusBox.className = 'status error';
                    statusBox.innerText = '❌ خطأ: ' + result.message;
                }
            } catch (err) {
                statusBox.className = 'status error';
                statusBox.innerText = '❌ حدث خطأ في الاتصال بالسيرفر.';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/send', methods=['POST'])
def send_email():
    req = request.json
    try:
        msg = MIMEMultipart()
        msg['From'] = req['user']
        msg['To'] = req['to']
        msg['Subject'] = req['subject']
        msg.attach(MIMEText(req['body'], 'plain', 'utf-8'))

        server = smtplib.SMTP(req['host'], int(req['port']))
        server.starttls()
        server.login(req['user'], req['pass'])
        server.send_message(msg)
        server.quit()

        return jsonify({'success': True, 'message': 'تم إرسال الرسالة بنجاح تام!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
