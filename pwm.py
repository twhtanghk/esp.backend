import gpio
import machine
import system

class Config(system.Config):
  def factory(self):
    ret = super().factory()
    ret.update({
      'pwm': {
        '2': {
          'freq': 50,
          'duty': 100,
          'range': [50, 100]
        }
      }
    })
    return ret
        
  def boot(self):
    super().boot()
    config = self.load()['pwm']
    for pin in config:
      data = {key: config[pin][key] for key in ['duty', 'freq']}
      machine.PWM(gpio.validPin(int(pin)), **data)

def get(req, res):
  try:
    id, pin = gpio.parse(req)
    pin = machine.PWM(pin)
    yield from res.ok({
      'freq': pin.freq(),
      'duty': pin.duty(),
      'range': Config.getInstance().load()['pwm'][str(id)]['range']
    })
  except gpio.PinError as e:
    yield from res.err(500, 'Invalid pin')

def duty(req, res):
  try:
    id, pin = gpio.parse(req)
    machine.PWM(pin).duty(int(req.body['duty']))
    yield from res.ok()
  except gpio.PinError as e:
    yield from res.err(500, 'Invalid pin')
  except ValueError:
    yield from res.err(500, 'Invalid duty value')

def getConfig(req, res):
  try:
    id, pin = gpio.parse(req)
    res.ok(Config.getInstance().load()['pwm'][str(id)])
  except gpio.PinError as e:
    yield from res.err(500, 'Invalid pin')

def setConfig(req, res):
  try:
    id, pin = gpio.parse(req)
    config = Config.getInstance().load()
    config['pwm'][str(id)] = {key: req.body[key] for key in ['duty', 'freq', 'range']}
    Config.getInstance().save(config)
    yield from res.ok()
  except gpio.PinError as e:
    yield from res.err(500, 'Invalid pin')

routes = {
  'get /pwm/(\d+)': get,
  'put /pwm/(\d+)': duty,
  'get /pwm/init/(\d+)': getConfig,
  'put /pwm/init/(\d+)': setConfig
}
