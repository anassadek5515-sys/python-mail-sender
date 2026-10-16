from flask import Flask, render_template_string, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
from threading import Thread

app = Flask(__name__)

# متغيرات لحفظ حالة الإحصائيات البسيطة وربطها بالواجهة
stats = {
    "total_sent": 0,
    "success": 0,
    "failed": 0,
    "history": []
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>B2B Ultimate Mail Server & Analytics</title>
    <style>
        body { font-family: Tahoma, Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px; margin: 0; }
        .container { max-width: 800px; margin: 0 auto; background: #1e293b; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h2, h3 { text-align: center; color: #38bdf8; }
        .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px; }
        .stat-card { background: #0f172a; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #334155; }
        .stat-card h4 { margin: 0; color: #94a3b8; font-size: 14px; }
        .stat-card p { margin: 10px 0 0; font-size: 22px; font-weight: bold; color: #38bdf8; }
        label { display: block; margin-top: 15px; font-weight: bold; color: #94a3b8; }
        input, textarea { width: 100%; padding: 12px; margin-top: 5px; border-radius: 8px; border: 1px solid #334155; background-color: #0f172a; color: #fff; box-sizing: border-box; font-size: 14px; }
        button { width: 100%; padding: 14px; background-color: #2563eb; color: white; border: none; border-radius: 8px; margin-top: 20px; font-size: 16px; font-weight: bold; cursor: pointer; transition: background 0.3s; }
        button:hover { background-color: #1d4ed8; }
        .status { margin-top: 15px; padding: 12px; border-radius: 8px; display: none; text-align: center; font-weight: bold; }
        .success { background-color: #065f46; color: #34d399; }
        .error { background-color: #991b1b; color: #fca5a5; }
        .log-box { background: #0f172a; padding: 10px; border-radius: 8px; margin-top: 20px; max-height: 150px; overflow-y: auto; font-size: 13px; color: #cbd5e1; border: 1px solid #334155; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🚀 B2B Automated Mail & Analytics Center</h2>
        
        <!-- لوحة الإحصائيات والرسومات البيانية المبسطة -->
        <div class="stats-grid">
            <div class="stat-card">
                <h4>إجمالي المرسل</h4>
                <p id="statTotal">0</p>
            </div>
            <div class="stat-card">
                <h4>العمليات الناجحة</h4>
                <p id="statSuccess" style="color: #34d399;">0</p>
            </div>
            <div class="stat-card">
                <h4>العمليات الفاشلة</h4>
                <p id="statFailed" style="color: #fca5a5;">0</p>
            </div>
        </div>

        <form id="campaignForm">
            <label>مضيف SMTP (Host):</label>
            <input type="text" id="smtpHost" value="smtp.gmail.com" required>

            <label>المنفذ (Port):</label>
            <input type="number" id="smtpPort" value="587" required>

            <label>البريد المُرسِل (Username):</label>
            <input type="email" id="smtpUser" placeholder="your-email@gmail.com" required>

            <label>كلمة المرور (App Password):</label>
            <input type="password" id="smtpPass" placeholder="******" required>

            <hr style="border: 0.5px solid #334155; margin-top: 20px;">

            <label>قائمة الإيميلات (افصل بينهم بفاصلة أو سطر جديد - للحملة الذكية):</label>
            <textarea id="emailsList" rows="5" placeholder="client1@company.com&#10;client2@company.com" required></textarea>

            <label>عنوان الرسالة (Subject):</label>
            <input type="text" id="subject" placeholder="عروض B2B والتطوير" required>

            <label>محتوى الرسالة (Body):</label>
            <textarea id="body" rows="6" placeholder="اكتب نص الرسالة التسويقية هنا..." required></textarea>

            <button type="submit" id="sendBtn">بدء الحملة الذكية الآمنة (تسخين تدريجي) ⚙️📤</button>
        </form>

        <div id="statusBox" class="status"></div>
        
        <h3>📋 سجل الأنشطة والردود المباشرة</h3>
        <div id="logBox" class="log-box">جاري تحميل السجلات...</div>
    </div>

    <script>
        async function fetchStats() {
            try {
                const res = await fetch('/stats');
                const data = await res.json();
                document.getElementById('statTotal').innerText = data.total_sent;
                document.getElementById('statSuccess').innerText = data.success;
                document.getElementById('statFailed').innerText = data.failed;
                
                let logsHtml = "";
                data.history.forEach(item => {
                    logsHtml += `<div>• [${item.time}] ${item.msg}</div>`;
                });
                document.getElementById('logBox').innerHTML = logsHtml || "لا توجد نشاطات مسجلة حتى الآن.";
            } catch(e) {}
        }

        setInterval(fetchStats, 3000); // تحديث الإحصائيات كل 3 ثواني تلقائياً

        document.getElementById('campaignForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const statusBox = document.getElementById('statusBox');
            statusBox.style.display = 'block';
            statusBox.className = 'status';
            statusBox.style.background = '#334155';
            statusBox.style.color = '#38bdf8';
            statusBox.innerText = '🚀 تم جدولة وبدء الحملة الذكية في الخلفية بأمان!';

            const emails = document.getElementById('emailsList').value.split(/\\r?\\n|,/).map(e => e.trim()).filter(e => e);

            const data = {
                host: document.getElementById('smtpHost').value,
                port: document.getElementById('smtpPort').value,
                user: document.getElementById('smtpUser').value,
                pass: document.getElementById('smtpPass').value,
                emails: emails,
                subject: document.getElementById('subject').value,
                body: document.getElementById('body').value
            };

            await fetch('/start-campaign', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/stats')
def get_stats():
    return jsonify(stats)

def background_sender(data):
    # خوارزمية التسخين الآمن (الإرسال التدريجي المتباعد لتجنب السبام)
    emails = data['emails']
    for idx, email in enumerate(emails):
        try:
            msg = MIMEMultipart()
            msg['From'] = data['user']
            msg['To'] = email
            msg['Subject'] = data['subject']
            msg.attach(MIMEText(data['body'], 'plain', 'utf-8'))

            server = smtplib.SMTP(data['host'], int(data['port']))
            server.starttls()
            server.login(data['user'], data['pass'])
            server.send_message(msg)
            server.quit()

            stats['success'] += 1
            stats['history'].insert(0, {"time": time.strftime("%H:%M:%S"), "msg": f"تم الإرسال بنجاح إلى: {email}"})
        except Exception as e:
            stats['failed'] += 1
            stats['history'].insert(0, {"time": time.strftime("%H:%M:%S"), "msg": f"فشل الإرسال لـ {email} ({str(e)})"})
        
        stats['total_sent'] = stats['success'] + stats['failed']
        
        # فاصل زمني ذكي للتسخين (مثلاً الانتظار بين الرسائل لحماية الحساب من الحظر)
        if idx < len(emails) - 1:
            time.sleep(15) # مؤقتاً 15 ثانية للتجربة، وتقدر تخليه وقت أطول للتسخين الحقيقي

@app.route('/start-campaign', methods=['POST'])
def start_campaign():
    req = request.json
    # تشغيل الإرسال في الخلفية (Background Thread) عشان الموقع ما يعلقش معاك
    t = Thread(target=background_sender, args=(req,))
    t.start()
    return jsonify({'success': True, 'message': 'تم بدء الحملة في الخلفية'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
