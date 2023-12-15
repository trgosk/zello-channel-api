import argparse
import asyncio
import configparser
import logging
import os
import signal
import subprocess
import threading

import uvloop
import zmq

import zellortlstreamer.logger
from zellortlstreamer import __version__ as version
from zellortlstreamer import databuffer
from zellortlstreamer.logger import log
from zellortlstreamer.myprotocol import MyProtocol, cb
from zellortlstreamer.thread_with_trace import Thread_with_trace
from zellortlstreamer.tokenmanager import (PrivateKeyFileNotFoundError,
                                           TokenManager)
from zellortlstreamer.zello import zello_stream_audio_to_channel


def start_zello():
    token = tokenman.getToken()
    event_loop_zello.create_task(zello_stream_audio_to_channel(
        username, password, token, channel, filename))
    if not event_loop_zello.is_running():
        log.logger.debug('Zello loop is not running, starting...')
        threading.Thread(target=lambda: run_zello_loop(event_loop_zello)).start()
    else:
        event_loop_zello.call_soon_threadsafe(lambda: log.logger.debug('Zello loop is already running'))


cb.func = start_zello


async def recv():
    global databuffer
    global event_loop_pipe, thread_pipe
    global zmq_address
    log.logger.info(f'Starting ZeroMQ Subscriber at {zmq_address}')

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(zmq_address)
    topicfilter = ""
    socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)

    while True:
        msg = socket.recv()
        msg_arr = msg.split()
        if len(msg_arr) == 4:
            topic, messagedata, d, t = msg_arr
            freq = ''
        elif len(msg_arr) == 5:
            topic, messagedata, d, t, freq = msg_arr
        else:
            log.logger.warning(f'[zeromq] received unknown {msg}')
            continue

        if messagedata == b'start':
            # todo check if already running
            log.logger.info(f'[zeromq] received {messagedata} {d} {t} {freq}')
            databuffer.Enable()
            databuffer.watch = True
            thread_pipe = Thread_with_trace(target=lambda x: run_pipe_loop(event_loop_pipe), args=(databuffer,))
            thread_pipe.name = "thread_pipe"
            thread_pipe.start()

        elif messagedata == b'stop' or messagedata == b'bye':
            log.logger.info(f'[zeromq] received {messagedata} {d} {t} {freq}')
            databuffer.Disable()
            await asyncio.sleep(0.5)
            # kill thread_pipe
            if thread_pipe:
                thread_pipe.kill()
                thread_pipe.join()
                if not thread_pipe.is_alive():
                    log.logger.debug('Pipe thread killed sucessfuly')
                else:
                    log.logger.error('Pipe thread kill failed')
            # empty buffer
            log.logger.debug(f'Emptying buffer of size {databuffer.GetSizeInBytes()} B')
            databuffer.ResetBuffer()
            log.logger.debug(f'databuffer size\t{databuffer.GetSizeInBytes()} B')
            # reset variables
            databuffer.flush = True
            databuffer.Enable()
            databuffer.watch = False
            # if messagedata == b'bye':
            #    break

        elif messagedata == b'hello2':
            log.logger.info(f'[zeromq] received {messagedata} {d} {t}')

        else:
            log.logger.info(f'[zeromq] received unknown {msg}')

        log.logger.debug(f'databuffer is now {databuffer.GetState()}')

    socket.close()


def run_zeromq_loop(loop):
    log.logger.debug('ZeroMQ loop starting')
    asyncio.set_event_loop(loop)
    try:
        zeromq_task = event_loop_zeromq.create_task(recv())
        loop.run_until_complete(zeromq_task)
    finally:
        log.logger.debug('ZeroMQ loop ended')


def run_zello_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
    log.logger.info('Zello loop ended')


def run_pipe_loop(loop):
    log.logger.info('Pipe reader loop starting')
    command = f"pacat --device={sink} --rate=48000 --record | opusenc --expect-loss=25 --max-delay=0 --framesize=20 --bitrate=256 --downmix-mono --raw - -"
    pro = subprocess.Popen(command, shell=True, stdin=None, stdout=subprocess.PIPE, preexec_fn=os.setsid)
    asyncio.set_event_loop(loop)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    try:
        stdin_pipe_reader = loop.connect_read_pipe(MyProtocol, pro.stdout)
        loop.run_until_complete(stdin_pipe_reader)
        loop.run_forever()
    finally:
        log.logger.debug('Pipe reader loop ended')
        os.killpg(os.getpgid(pro.pid), signal.SIGTERM)


def main():
    global username, password, channel, filename, sink, zmq_address
    global thread_pipe, thread_zeromq
    global event_loop_pipe, event_loop_zeromq, event_loop_zello
    global tokenman
    thread_pipe = None
    testrun = False

    # Config (arguments)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", help="Set debug level output.", action="store_true"
    )
    parser.add_argument(
        "-t", "--test", help="Play opus file", action="store_true"
    )

    args = parser.parse_args()
    if args.verbose:
        log.log_level = logging.DEBUG
    if args.test:
        testrun = True

    log.configure()

    # Config (file)
    try:
        config = configparser.ConfigParser()
        config.read('stream.conf')
        username = config['zello']['username']
        password = config['zello']['password']
        issuer = config['zello']['issuer']
        privatekeyfile = config['zello']['privatekeyfile']
        channel = config['zello']['channel']
        filename = config['media']['filename']
        sink = config['media']['sink']
        zmq_address = config['zmq']['address']
    except KeyError as error:
        log.logger.error(f'Check config file. Missing key: {error}')
        return

    # TokenManager init
    try:
        tokenman = TokenManager(privatekeyfile, issuer)
    except PrivateKeyFileNotFoundError:
        log.logger.error(f'Private key file "{privatekeyfile}" was not found')
        return

    # Eventloops
    event_loop_pipe = asyncio.new_event_loop()
    event_loop_zeromq = asyncio.new_event_loop()
    event_loop_zello = asyncio.new_event_loop()

    log.logger.info(f'Zello-rtl-streamer v{version}')

    if testrun:
        log.logger.info('Starting streaming test')
        start_zello()
    else:
        filename = ""

        # zeroMQ Thread
        thread_zeromq = Thread_with_trace(target=lambda: run_zeromq_loop(event_loop_zeromq))
        thread_zeromq.name = "thread_zeromq"
        # thread_zeromq.daemon = True
        thread_zeromq.start()


if __name__ == "__main__":
    main()
