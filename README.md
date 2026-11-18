# BM FUTUROMIND AI — Academy + SMTP Mail Server OTP

## Deploy Free on Render.com with Real Email OTP
1. Push this folder to GitHub.
2. Create a free Web Service on Render (`pip install -r requirements.txt` / `gunicorn app:app`).
3. Add Environment Variables in Render:
   - `SMTP_HOST` = `smtp.gmail.com`
   - `SMTP_PORT` = `465`
   - `SMTP_USER` = your Gmail address
   - `SMTP_APP_PASS` = your 16-char Gmail App Password
