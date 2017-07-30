from collections import deque
from datetime import datetime, timedelta
import logging
import os
import sys
from random import random

from PIL import Image
import numpy as np
import cv2

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.tcpclient import TCPClient

import json
import time

import config
from web import start_app, send_socket_msg

from klt_tracking import KLTTracker

TIME_THRESHOLD = timedelta(milliseconds=500)
MOCK = True  # be sure to change this for real data!
MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), '../mock/green_pen_manual/trial1')

# TODO: initialize KLT tracking here
xy_imgs = deque()
z_imgs = deque()
xy_tracker = KLTTracker()
z_tracker = KLTTracker()

class Item(object):
    def __init__(self, data, ts):
        self.data = data
        self.ts = ts

    def within_threshold(self, other):
        """Check if this item and another item are within TIME_THRESHOLD

        Args:
            other (Item) - another Item to check

        Returns:
            True if within threshold, False otherwise
        """
        if abs(other.ts - self.ts) < TIME_THRESHOLD:
            return True
        return False

    def closest_to(self, a, b):
        """Out of two other Items, pick the closer of the two

        Args:
            a (Item) - another Item
            b (Item) - another Item

        Returns:
            the closer Item of a and b or None if neither is within the time threshold
        """
        diff_a = abs(a.ts - self.ts)
        diff_b = abs(b.ts - self.ts)
        if diff_a < diff_b and diff_a < TIME_THRESHOLD:
            return a
        elif diff_b < TIME_THRESHOLD:
            return b
        return None


@gen.coroutine
def process_images(img_xy, img_z):
    """Process a matched pair of xy and z images, obtain the 3d point, and broadcast a websocket with that point

    Args:
        img_xy (Item) - the xy image
        img_z (Item) - the z image
    """
    logging.info("paired {} and {}".format(img_xy.ts, img_z.ts))
    for item in xy_imgs:
        assert(item.ts >= img_xy.ts)
    for item in z_imgs:
        assert(item.ts >= img_z.ts)

    xy_data = np.asarray(img_xy.data, dtype='uint8')
    z_data = np.asarray(img_z.data, dtype='uint8')

    xy_tracker.run_tracking(xy_data)
    z_tracker.run_tracking(z_data)

    try:
        x, y1 = xy_tracker.get_avg().astype(float)
        z, y2 = z_tracker.get_avg().astype(float)
        msg = dict(x=x,y=y1,z=z)
        msg = json.dumps(msg)
        send_socket_msg(msg)
        time.sleep(3)
    except Exception as e:
        pass


@gen.coroutine
def pair_images():
    """Attempt to pair images off the xy and z image queues

    If either of the queues is empty, this returns immediately
    This then picks the first image off each queue and performs a matching procedure
    If, for example, the xy image has an earlier timestamp than the z image:
        - Keep peeking at the next xy image (and popping the previous one off the queue)
          until the next xy image's timestamp is greater than the z image's timestamp
        - If at any time there is no next xy image, check if the previous xy image is within
          TIME_THRESHOLD. If so, process that image pair. Return regardless of whether we
          processed an image.
        - When we have crossed the z image timestamp, we have three images: an older xy image,
          a newer xy image, and a z image. Compare the two xy images to the z image to determine
          which one is closer in time to the z image, then process the resulting image pair
    """
    # TODO: maybe implement some way to skip frames if queue is too long
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
    """Worker that attempts to generate an image pair off the queues

    If successfully paired, we'll call process_image on the image pair
    """
    while True:
        yield pair_images()
        yield gen.sleep(0.1)


@gen.coroutine
def stream_mock_data(port, queue):
    """Mock out phone image stream

    Args:
        port (int) - the TCP port to listen on
        queue (collections.deque) - a queue to append mock Item objects to (with roughly real timestamps)
    """
    img_files = [os.path.join(MOCK_DATA_PATH, f) for f in os.listdir(MOCK_DATA_PATH)
                 if os.path.isfile(os.path.join(MOCK_DATA_PATH, f)) and not f.startswith('.')]
    cur = 0
    while True:
        #with open(img_files[cur], 'r') as f:
        #    data = f.read()
        data = Image.open(img_files[cur])
        yield queue.append(Item(data, datetime.now()))
        logging.info('{}: queue length {}'.format(port, len(queue)))
        yield gen.sleep(random()/5)
        cur = (cur + 1) % len(img_files)


@gen.coroutine
def setup_phone(port, queue):
    """Listen to a socket streaming binary image data

    Args:
        port (int) - the TCP port to listen on
        queue (collections.deque) - a queue to append Item objects to
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
