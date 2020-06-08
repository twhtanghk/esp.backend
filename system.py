import network
import ujson

ap_if = network.WLAN(network.AP_IF)
sta_if = network.WLAN(network.STA_IF)
setting = None

# class to define factory config
# load and save configuration
# initialize during boot
class Config:
  __instance = None

  def __init__(self):
    self.filename = '/config.json'

  def exists(self):
    try:
      import os
      os.stat(self.filename)
      return True
    except OSError:
      return False

  def factory(self):
    import ubinascii
    mac = ap_if.config('mac')
    mac = ubinascii.hexlify(mac).decode('utf-8')[6:]
    return {
      'name': 'TT{}'.format(mac),
    }

  def load(self):
    f = open(self.filename)
    data = ujson.load(f)
    f.close()
    return data

  def save(self, data):
    f = open(self.filename, 'w')
    ujson.dump(data, f)
    f.close()
 
  def boot(self):
    setting = self
    if not self.exists():
      self.save(self.factory())
    ap_if.active(True)
    sta_if.active(True)

def factory(req, res):
  ap_if.config(essid=setting.factory()['name'], password='password')
  sta_if.config(dhcp_hostname=setting.factory()['name'])
  setting.save(setting.factory())
  yield from res.ok()
  
async def reboot(req, res):
  await res.ok()
  from uasyncio import sleep
  await sleep(1)
  import machine
  machine.reset()

def getAP(req, res):
  yield from res.ok({
    'essid': ap_if.config('essid'),
    'config': ap_if.ifconfig()
  })

def configAP(req, res):
  config = load()
  config['name'] = req.body['essid']
  setting.save(config)
  ap_if.config(essid=req.body['essid'], password=req.body['password'])
  yield from res.ok()

def getSTA(req, res):
  yield from res.ok({
    'essid': sta_if.config('essid'),
    'isconnected': sta_if.isconnected(),
    'curr': sta_if.ifconfig()
  })

def configSTA(req, res):
  config = load()
  sta_if.active(True)
  sta_if.config(dhcp_hostname=config['name'])
  sta_if.connect(req.body['ssid'], req.body['password'])
  yield from res.ok()

def hotspot(req, res):
  sta_if.active(True)
  nets = []
  for net in sta_if.scan():
    if net[0] not in nets:
      nets.append(net[0])
  nets.sort()
  skip = req.body['skip']
  yield from res.ok(nets[skip:skip + 10])

import http

routes = {
  'options .*': http.preflight,
  'get /factory': factory,
  'get /reboot': reboot,
  'get /ap': getAP,
  'put /ap': configAP,
  'get /sta': getSTA,
  'get /sta/scan': hotspot,
  'put /sta': configSTA
}
