import logging
import os

from tornado import web, websocket

import config


class WebApp(object):
    def __init__(self):
        self.clients = set()
        self.app = self.make_app()
        self.app.listen(config.web_port)

    class IndexHandler(web.RequestHandler):
        def get(self):
            self.render('index.html')

    class SocketHandler(websocket.WebSocketHandler):
        def open(self):
            self.clients.add(self)
            logging.info("WebSocket opened")

        def on_close(self):
            self.clients.remove(self)
            logging.info("WebSocket closed")

    def make_app(self):
        settings = {
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
        }
        return web.Application([
            (r'/', self.IndexHandler),
            (r'/ws', self.SocketHandler),
        ], **settings)

    def num_clients(self):
        return len(self.clients)

    def send_socket_msg(self, msg):
        logging.info("broadcasting to {} clients: {}".format(self.num_clients(), msg))
        to_remove = set()
        for c in self.clients:
            if not c.ws_connection or not c.ws_connection.stream.socket:
                to_remove.add(c)
            else:
                c.write_message(msg)
        self.clients.difference_update(to_remove)
