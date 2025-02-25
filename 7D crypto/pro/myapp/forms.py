from django import forms

class EmailForm(forms.Form):
    smtp_server = forms.CharField(label="SMTP Server", max_length=255, initial="mail.zeroanalyst.com")
    smtp_port = forms.IntegerField(label="SMTP Port", initial=587)
    sender_email = forms.EmailField(label="Sender Email",initial="dev@zeroanalyst.com")
    sender_password = forms.CharField(label="Sender Password", widget=forms.PasswordInput)
    receiver_email = forms.EmailField(label="Receiver Email",initial="deepaklc17@gmail.com")
    subject = forms.CharField(label="Subject", max_length=255)
