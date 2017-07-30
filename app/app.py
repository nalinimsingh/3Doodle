from collections import deque
from datetime import datetime
import logging
import os

from tornado import gen, web
from tornado.ioloop import IOLoop
from tornado.tcpclient import TCPClient

xy_imgs = deque()
z_imgs = deque()
clients = []

# TODO:
# - make consumer/producer queue work
# - add in pairing algorithm of images
# - add in image processing of paired images
# - add websocket layer that broadcasts coordinates to clients


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render('index.html')

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
    # Preliminary version: pick closest point up to the greater of the 2 pts
    pop_a = True
    pop_b = True
    a_last = None
    b_last = None
    prev_larger = None
    while len(queue_a) > 0 and len(queue_b) > 0:
          if pop_a:
              a = queue_a.popleft()
          if pop_b:
              b = queue_b.popleft()
          if a[0] == b[0]:
              print "match! will return {} and {}".format(a, b)
              # TODO: pass a and b to open cv module
              pop_a = True
              pop_b = True
              prev_larger = None
          if a[0] < b[0]:
              a_last = a
              if prev_larger == 'a':
                  print "would return {} and {}".format(a, b_last)
                  # TODO: pass b_last and a to open cv module
                  pop_b = False
                  pop_a = True
                  prev_larger = None
              else:
                  prev_larger = 'b'
                  pop_a = True
                  pop_b = False
          elif b[0] < a[0]:
              b_last = b
              if prev_larger == 'b':
                  print "would return {} and {}".format(a_last, b)
                  # TODO: pass a_last and b to open cv module
                  pop_a = False
                  pop_b = True
                  prev_larger = None
              else:
                  prev_larger = 'a'
                  pop_a = False
                  pop_b = True

@gen.coroutine
def setup_phone(port, queue):
    """Listen to a socket streaming binary image data

    Args:
        port - the TCP port to listen on
        queue - a queue to append tuples of (image blob, datetime)
    """
    stream = yield TCPClient().connect('localhost', port)

    # Process the image data
    def read_stream(data):
        queue.append((data, datetime.now()))
        logging.info('{}: queue length {}'.format(port, len(queue)))
        stream.read_until(b'\n', callback=read_stream)

    read_stream('')


# web application
def make_app():
    settings = {
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    }
    return web.Application([
        (r'/', IndexHandler),
    ], **settings)


# main
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    setup_phone(8888, z_imgs)
    setup_phone(8889, xy_imgs)
    # pair_images(z_imgs, xy_imgs)  # this doesn't work for some reason hmm
    app = make_app()
    app.listen(5000)
    IOLoop.current().start()
