#!/usr/bin/python

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado.options import define, options
import RPi.GPIO as GPIO


define("port", default=8080, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('New connection was opened')

    def on_message(self, message):
        print('Incoming message: ' + message)
        for color in message.split('\n'):
            color = color.lower().strip()
            print(color)
            if (color == "red"):
                GPIO.output(22, 1 - GPIO.input(22))

            if (color == "yellow"):
                GPIO.output(27, 1 - GPIO.input(27))

            if (color == "green"):
                GPIO.output(17, 1 - GPIO.input(17))

        self.write_message('{ "red": ' + str(GPIO.input(22)) + ', "yellow": ' +
                           str(GPIO.input(27)) + ', "green": ' +
                           str(GPIO.input(17)) + ' }')

    def on_close(self):
        print 'Connection was closed...'


APP = tornado.web.Application(handlers=[ (r"/", IndexHandler),
                                                 (r"/ws", WebSocketHandler)],
                                      autoreload=True)

if __name__ == "__main__":

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(22, GPIO.OUT)
    GPIO.setup(27, GPIO.OUT)

    http_server = tornado.httpserver.HTTPServer(APP)
    http_server.listen(options.port)
    print("Listening on port: " + str(options.port))
    tornado.ioloop.IOLoop.instance().start()
