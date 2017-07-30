from collections import deque
import logging

from tornado import gen
from tornado.ioloop import IOLoop

from web import start_app, send_socket_msg

points = deque()


@gen.coroutine
def send_point():
    point = points.popleft()
    msg = dict(x=point[0], y=point[1], z=point[2])
    send_socket_msg(msg)
    points.append(point)


@gen.coroutine
def point_worker():
    while True:
        yield send_point()
        yield gen.sleep(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    for i in range(10):
        points.append((i, i, i*i))
    start_app()
    IOLoop.current().spawn_callback(point_worker)
    IOLoop.current().start()
