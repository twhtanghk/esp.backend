from uasyncio import StreamReader, StreamWriter, get_event_loop, start_server
from machine import UART
import system

uart = UART(0)
uartReader = None
uartWriter = None

class Config(system.Config):
  def factory(self):
    ret = super().factory()
    ret.update({
      'uart': {
        'baudrate': 4800,
        'bits': 8,
        'parity': None,
        'stop': 1
      }
    })
    return ret

  def boot(self):
    super().boot()
    uart.init(**self.load()['uart'])
    loop = get_event_loop()
    loop.create_task(start_server(Serial.getInstance().handle, '0.0.0.0', 23))
    loop.create_task(Serial.getInstance().readln())
 
def valid(data):
  if data['baudrate'] not in [300, 600, 1200, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 250000, 460800]:
    raise ValueError('baudrate')
  if data['bits'] not in [7, 8]:
    raise ValueError('bits')
  if data['parity'] not in [None, 0, 1]:
    raise ValueError('parity')
  if data['stop'] not in [1, 2]:
    raise ValueError('stop')

def set(req, res):
  try:
    valid(req.body)
    system.save(req.body)
    uart.init(**req.body)
    uartReader = StreamReader(uart)
    uartWriter = StreamWriter(uart, {})
    yield from res.ok()
  except ValueError as err:
    yield from res.err(500, "Invalid {}".format(str(err)))

def get(req, res):
  yield from res.ok(system.config.load())

class Serial:
  __instance = None

  def __init__(self):
    self.uart = {
      'reader': StreamReader(uart),
      'writer': StreamWriter(uart, {})
    }
    self.net = []

  @staticmethod
  def getInstance():
    if Serial.__instance == None:
      Serial.__instance = Serial()
    return Serial.__instance

  async def handle(self, reader, writer):
    self.net.append({
      'reader': reader,
      'writer': writer
    })
    while True:
      line = await reader.readline()
      if len(line) == 0:
        return
      await self.writeln(line)

  async def writeln(self, line):
    await self.uart['writer'].awrite(line)

  async def readln(self):
    while True:
      line = await self.uart['reader'].readline()
      for stream in self.net:
        try:
          await stream['writer'].awrite(line)
        except OSError:
          self.net.remove(stream)

routes = {
  'get /uart': get,
  'put /uart': set
}
