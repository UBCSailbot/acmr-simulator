import zmq
import time

def main():

    try:
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.SUB)
        frontend.bind("tcp://*:5551")

        frontend.setsockopt(zmq.SUBSCRIBE, "")

        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind("tcp://*:5552")

        print 'Virtual Bus Starting.'
        zmq.device(zmq.FORWARDER, frontend, backend)

    except Exception, e:
        print e
        print "Bringing down ZMQ device"

    finally:
        pass
        frontend.close()
        backend.close()
        context.term()


if __name__ == "__main__":
    main()