from collections import deque
import logging

from tornado import gen
from tornado.ioloop import IOLoop

from web import WebApp

points = deque()


@gen.coroutine
def start_point_worker(app):
    while app.num_clients() == 0:
        pass

    point = points.popleft()
    msg = dict(x=point[0], y=point[1], z=point[2])
    app.send_socket_msg(msg)
    points.append(point)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    for i in range(10):
        points.append((i, i, i*i))
    app = WebApp()
    start_point_worker(app)
    IOLoop.current().start()
