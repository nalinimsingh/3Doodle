from collections import deque
import logging

from tornado import gen
from tornado.ioloop import IOLoop

import config
from web import make_app, send_socket_msg

points = deque()


@gen.coroutine
def start_point_worker():
    while True:
        point = points.popleft()
        msg = dict(x=point[0], y=point[1], z=point[2])
        send_socket_msg(msg)
        points.append(point)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    for i in range(10):
        points.append((i, i, i*i))
    start_point_worker()
    app = make_app()
    app.listen(config.web_port)
    IOLoop.current().start()