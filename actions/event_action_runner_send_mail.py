import os
from st2common.runners.base_action import Action
from smtplib import SMTP
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EventActionRunnerSendMail(Action):
    def run(self, alert_sendto, alert_subject, alert_message, account, mime="plain", attachments=None):

        if mime not in ['plain', 'html']:
            raise ValueError('Invalid mime provided: ' + mime)

        accounts = self.config.get('smtp_accounts', None)
        if accounts is None:
            raise ValueError('"smtp_accounts" config value is required to send email.')
        if len(accounts) == 0:
            raise ValueError('at least one account is required to send email.')

        try:
            kv = {}
            for a in accounts:
                kv[a['name']] = a
            account_data = kv[account]
        except KeyError:
            raise KeyError('The account "{}" does not seem to appear in the configuration. '
                           'Available accounts are: {}'.format(account, ",".join(kv.keys())))

        msg = MIMEMultipart()
        msg['Subject'] = Header(alert_subject, 'utf-8')
        msg['From'] = alert_sendto
        msg['To'] = ", ".join(alert_sendto)
        msg.attach(MIMEText(alert_message, mime, 'utf-8'))

        attachments = attachments or tuple()
        for filepath in attachments:
            filename = os.path.basename(filepath)
            with open(filepath, 'rb') as f:
                part = MIMEApplication(f.read(), Name=filename)
            part['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
            msg.attach(part)

        s = SMTP(account_data['server'], int(account_data['port']), timeout=20)
        s.ehlo()
        if account_data.get('secure', True) is True:
            s.starttls()
        if account_data.get('smtp_auth', True) is True:
            s.login(account_data['username'], account_data['password'])
        s.sendmail(alert_sendto, alert_sendto, msg.as_string())
        s.quit()
        return
