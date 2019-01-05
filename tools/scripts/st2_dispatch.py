#!/usr/bin/env python

from st2client.base import BaseCLIApp


from optparse import OptionParser


class ZabbixDispatcher(BaseCLIApp):
    def __init__(self, options):
        self.options = options

        # make a client object to connect st2api
        self.client = self.get_client(args=options)
        self.client.token = self._get_auth_token(client=self.client,
                                                 username=options.st2_userid,
                                                 password=options.st2_passwd,
                                                 cache_token=False)

    def dispatch_trigger(self, args, trigger='zabbix.event_handler'):
        body = {
            'trigger': trigger,
            'payload': {
                'alert_sendto': self.options.alert_sendto,
                'alert_subject': self.options.alert_subject,
                'alert_message': self.options.alert_message,
                'extra_args': args,
            },
        }

        # send request to st2api to dispatch trigger of Zabbix
        return self.client.managers['Webhook'].client.post('/webhooks/st2', body, headers={
            'Content-Type': 'application/json',
            'X-Auth-Token': self.client.token,
        })


    def dispatch_trigger_mail(self, args, trigger='zabbix.send_mail'):
        body = {
            'trigger': trigger,
            'payload': {
                'alert_sendto': self.options.alert_sendto,
                'alert_subject': self.options.alert_subject,
                'alert_message': self.options.alert_message,
                'extra_args': args,
            },
        }

        # send request to st2api to dispatch trigger of Zabbix
        return self.client.managers['Webhook'].client.post('/webhooks/st2', body, headers={
            'Content-Type': 'application/json',
            'X-Auth-Token': self.client.token,
        })
    

def get_options():
    parser = OptionParser()

    parser.add_option('--st2-userid', dest="st2_userid", default="st2admin",
                      help="Login username of StackStorm")
    parser.add_option('--st2-passwd', dest="st2_passwd", default="",
                      help="Login password associated with the user")
    parser.add_option('--st2-api-url', dest="api_url", default="https://localhost/api/v1",
                      help="Endpoint URL for API")
    parser.add_option('--st2-auth-url', dest="auth_url", default="https://localhost/auth/v1",
                      help="Endpoint URL for auth")
    parser.add_option('--alert-sendto', dest="alert_sendto", default="",
                      help="'Send to' value from user media configuration of Zabbix")
    parser.add_option('--alert-subject', dest="alert_subject", default="",
                      help="'Default subject' value from action configuration of Zabbix")
    parser.add_option('--alert-message', dest="alert_message", default="",
                      help="'Default message' value from action configuration of Zabbix")
    parser.add_option('--skip-config', dest="skip_config", default=False, action='store_true',
                      help='Do NOT parse and use the CLI config file')
    parser.add_option('--config-file', dest="config_file",
                      help='Path to the CLI config file')

    # Zabbix send argument as one string even though it includes whitespace
    # (like $ st2_dispatch.py "foo bar" "hoge fuga" ...).
    # And we can't specify keyward argument, we can only specify args.
    #
    # So it's hard for us to parse the argument of zabbix mediatype using optparse.
    # Then, I decided to fix the order of the CLI arguemnts.
    arg_list = ['api_url', 'auth_url', 'st2_userid', 'st2_passwd',
                'alert_sendto', 'alert_subject', 'alert_message']

    (options, args) = parser.parse_args()

    for index, param in enumerate(arg_list):
        if len(args) > index and args[index]:
            setattr(options, param, args[index])

    return (options, args[len(arg_list):])


def main():
    # parse and get arguemnts
    (options, args) = get_options()

    # make client to dispatch trigger
    dispatcher = ZabbixDispatcher(options)

    # dispatch trigger of zabbix.event_handler
    dispatcher.dispatch_trigger(args)

     # dispatch trigger of zabbix.send_mail
    dispatcher.dispatch_trigger_mail(args)


if __name__ == '__main__':
    main()
