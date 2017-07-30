from collections import deque
from datetime import datetime, timedelta
import logging
import os
from random import random

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.tcpclient import TCPClient

import config
from web import start_app, send_socket_msg

xy_imgs = deque()
z_imgs = deque()
TIME_THRESHOLD = timedelta(milliseconds=500)
MOCK = True  # be sure to change this for real data!
MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), '../mock/green_pen_manual/trial1')

# TODO: initialize KLT tracking here


class Item(object):
    def __init__(self, data, ts):
        self.data = data
        self.ts = ts

    def within_threshold(self, other):
        if abs(other.ts - self.ts) < TIME_THRESHOLD:
            return True
        return False

    def closest_to(self, a, b):
        diff_a = abs(a.ts - self.ts)
        diff_b = abs(b.ts - self.ts)
        if diff_a < diff_b and diff_a < TIME_THRESHOLD:
            return a
        elif diff_b < TIME_THRESHOLD:
            return b
        return None


@gen.coroutine
def process_images(img_xy, img_z):
    logging.info("paired {} and {}".format(img_xy.ts, img_z.ts))
    for item in xy_imgs:
        assert(item.ts >= img_xy.ts)
    for item in z_imgs:
        assert(item.ts >= img_z.ts)
    # TODO: call KLT tracking here
    # TODO: send results of KLT tracking here to clients with send_socket_msg


@gen.coroutine
def pair_images():
    queue_a = xy_imgs
    queue_b = z_imgs
    if len(queue_a) == 0 or len(queue_b) == 0:
        return
    a_prev = None
    b_prev = None
    a = queue_a[0]
    b = queue_b[0]
    if a.ts < b.ts:
        while a.ts < b.ts:
            a_prev = queue_a.popleft()
            if len(queue_a) == 0:
                if b.within_threshold(a_prev):
                    yield process_images(a_prev, b)
                return
            a = queue_a[0]
        closest_a = b.closest_to(a, a_prev)
        if closest_a is not None:
            yield process_images(closest_a, b)
    else:
        while b.ts < a.ts:
            b_prev = queue_b.popleft()
            if len(queue_b) == 0:
                if a.within_threshold(b_prev):
                    yield process_images(a, b_prev)
                return
            b = queue_b[0]
        closest_b = a.closest_to(b, b_prev)
        if closest_b is not None:
            yield process_images(a, closest_b)


@gen.coroutine
def pairing_worker():
    while True:
        yield pair_images()
        yield gen.sleep(0.1)


@gen.coroutine
def stream_mock_data(port, queue):
    img_files = [os.path.join(MOCK_DATA_PATH, f) for f in os.listdir(MOCK_DATA_PATH)
                 if os.path.isfile(os.path.join(MOCK_DATA_PATH, f))]
    cur = 0
    while True:
        with open(img_files[cur], 'r') as f:
            data = f.read()
        yield queue.append(Item(data, datetime.now()))
        logging.info('{}: queue length {}'.format(port, len(queue)))
        yield gen.sleep(random())
        cur = (cur + 1) % len(img_files)


@gen.coroutine
def setup_phone(port, queue):
    """Listen to a socket streaming binary image data

    Args:
        port - the TCP port to listen on
        queue - a queue to append dicts containing image blob and datetime
    """
    if not MOCK:
        stream = yield TCPClient().connect('localhost', port)

        # Process the image data
        def read_stream(data):
            if len(queue) < 50:
                queue.append(Item(data, datetime.now()))
                logging.info('{}: queue length {}'.format(port, len(queue)))
            stream.read_until(b'\n', callback=read_stream)

        read_stream('')
    else:
        yield stream_mock_data(port, queue)


# main
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    setup_phone(config.phone_z_port, z_imgs)
    setup_phone(config.phone_xy_port, xy_imgs)
    start_app()
    IOLoop.current().spawn_callback(pairing_worker)
    IOLoop.current().start()
