"""SMTP server and HTTP server to fetch received emails

Uses aiosmtpd and http.server

"""

import json
from aiosmtpd.controller import Controller
from http.server import HTTPServer, BaseHTTPRequestHandler, HTTPStatus


MESSAGES = []


class EmailHandler:
    async def handle_DATA(self, server, session, envelope):
        MESSAGES.append({
            "from": envelope.mail_from,
            "to": envelope.rcpt_tos,
            "message": envelope.content.decode("utf8", errors="replace"),
        })

        print('Message from %s' % envelope.mail_from)
        print('Message for %s' % envelope.rcpt_tos)
        print('Message data:\n')
        for ln in envelope.content.decode('utf8', errors='replace').splitlines():
            print(f'> {ln}'.strip())
        print()
        print('End of message')
        return '250 Message accepted for delivery'


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(MESSAGES, indent=2).encode()

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)


def main():
    print("Starting SMTP server:", controller.hostname, controller.port)
    controller = Controller(EmailHandler(), "0.0.0.0", 8025)
    controller.start()

    print("Starting HTTP server: http://0.0.0.0:8000")
    server = HTTPServer(('', 8000), HttpHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
