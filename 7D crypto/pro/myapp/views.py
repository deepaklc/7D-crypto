from django.shortcuts import render
from django.http import HttpResponse
from .forms import EmailForm
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import email.encoders
from datetime import datetime
import pandas as pd
import requests

def get_crypto_data():
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    param = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 250,
        'page': 1
    }
    response = requests.get(url, params=param)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df = df[[
            'id', 'symbol', 'name', 'current_price', 'market_cap', 
            'price_change_percentage_24h', 'high_24h', 'low_24h',
            'ath', 'atl'
        ]].rename(columns={
            'id': 'ID',
            'symbol': 'Symbol',
            'name': 'Name',
            'current_price': 'Current Price ($)',
            'market_cap': 'Market Cap ($)',
            'price_change_percentage_24h': '24h Change (%)',
            'high_24h': '24h High ($)',
            'low_24h': '24h Low ($)',
            'ath': 'All Time High ($)',
            'atl': 'All Time Low ($)'
        })
        today = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f'crypto_data_{today}.csv'
        df.to_csv(file_name, index=False)

        top_gainers = df.nlargest(10, '24h Change (%)')
        top_losers = df.nsmallest(10, '24h Change (%)')

        html_content = f"""
        <html>
        <body>
            <h1>Crypto Currency Market Update - {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}</h1>
            
            <h2>Top 10 Gainers (Last 24 Hours)</h2>
            {top_gainers.to_html(index=False)}
            
            <h2>Top 10 Losers (Last 24 Hours)</h2>
            {top_losers.to_html(index=False)}
        </body>
        </html>
        """
        return html_content, file_name
    else:
        return None, None

def send_email(smtp_server, smtp_port, sender_email, sender_password, receiver_email, subject, html_content, filename):
    message = MIMEMultipart('alternative')
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    message.attach(MIMEText(html_content, 'html'))

    with open(filename, 'rb') as file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(file.read())
        email.encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        message.attach(part)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

def email_view(request):
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            smtp_server = form.cleaned_data['smtp_server']
            smtp_port = form.cleaned_data['smtp_port']
            sender_email = form.cleaned_data['sender_email']
            sender_password = form.cleaned_data['sender_password']
            receiver_email = form.cleaned_data['receiver_email']
            subject = form.cleaned_data['subject']

            html_content, filename = get_crypto_data()
            if html_content and filename:
                try:
                    send_email(smtp_server, smtp_port, sender_email, sender_password, receiver_email, subject, html_content, filename)
                    return HttpResponse("Email sent successfully!")
                except Exception as e:
                    return HttpResponse(f"Failed to send email: {e}", status=500)
            else:
                return HttpResponse("Failed to fetch crypto data.", status=500)
    else:
        form = EmailForm()
    return render(request, 'crypto_app/email_form.html', {'form': form})
