from collections import deque
from datetime import datetime
import logging

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.tcpclient import TCPClient

xy_imgs = deque()
z_imgs = deque()
clients = []

# TODO:
# - make consumer/producer queue work
# - add in pairing algorithm of images
# - add in image processing of paired images
# - add index handler
# - add websocket layer that broadcasts coordinates to clients

# class IndexHandler(web.RequestHandler):
#     def get(self):
#         self.render("index.html")

# class SocketHandler(websocket.WebSocketHandler):
#     def open(self):
#         if self not in clients:
#             clients.append(self)
#
#     def on_message(self, message):
#         print message
#
#     def on_close(self):
#         if self in clients:
#             clients.remove(self)


@gen.coroutine
def pair_images(queue_a, queue_b):
    while True:
        if len(queue_a) > 0:
            queue_a.popleft()
            print "popped item"


@gen.coroutine
def setup_phone(port, queue):
    """Listen to a socket streaming binary image data

    Args:
        port - the TCP port to listen on
        queue - a queue to append tuples of (image blob, datetime)
    """
    stream = yield TCPClient().connect("localhost", port)

    # Process the image data
    def read_stream(data):
        queue.append((data, datetime.now()))
        logging.info("{}: queue length {}".format(port, len(queue)))
        stream.read_until(b"\n", callback=read_stream)

    read_stream("")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    setup_phone(8888, z_imgs)
    setup_phone(8889, xy_imgs)
    # pair_images(z_imgs, xy_imgs)  # this doesn't work for some reason hmm
    IOLoop.current().start()
