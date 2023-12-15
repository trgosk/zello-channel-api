import asyncio

from zellortlstreamer import databuffer
from zellortlstreamer.logger import log


class Callback:
    def __init__(self, func):
        self.func = func


cb = Callback(None)


# https://medium.com/@denismakogon/python-3-fight-for-nonblocking-pipe-68f92429d18e
class MyProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        log.logger.info('pipe opened')
        # super(MyProtocol, self).connection_made(transport=transport)

    def data_received(self, data):
        # print('received: {!r}'.format(data), file=sys.stderr, flush=True)
        log.logger.debug(f'recieved\t{len(data)} B')

        if databuffer.isEnabled():
            if databuffer.flush:
                log.logger.debug('flushing buffer...')
                databuffer.flush = False
            else:
                databuffer.buffer.write(data, bytes)
        else:
            pass

        log.logger.debug(f'databuffer size\t{databuffer.GetSizeInBytes()} B (DR)')

        if databuffer.watch and int(len(databuffer.buffer)/8) > 10000:
            cb.func()
            databuffer.watch = False

        # print(data.decode(), file=sys.stderr, flush=True)
        # super(MyProtocol, self).data_received(data)

    def connection_lost(self, exc):
        log.logger.info('pipe closed')
        log.logger.debug(f'databuffer size\t{int(len(databuffer.buffer)/8)} B (CL)')
        # super(MyProtocol, self).connection_lost(exc)
