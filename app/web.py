import logging
import os

from tornado import web, websocket

import config

clients = set()


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render('index.html')


class SocketHandler(websocket.WebSocketHandler):
    def open(self):
        clients.add(self)
        logging.info("WebSocket opened")

    def on_close(self):
        clients.remove(self)
        logging.info("WebSocket closed")


def start_app():
    settings = {
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    }
    app = web.Application([
        (r'/', IndexHandler),
        (r'/ws', SocketHandler),
    ], **settings)
    app.listen(config.web_port)


def num_clients():
    return len(clients)


def send_socket_msg(msg):
    logging.info("broadcasting to {} clients: {}".format(num_clients(), msg))
    to_remove = set()
    for c in clients:
        if not c.ws_connection or not c.ws_connection.stream.socket:
            to_remove.add(c)
        else:
            c.write_message(msg)
    clients.difference_update(to_remove)
