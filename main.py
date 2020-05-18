import http
import system
import pwm

app = http.App()
app.apply([system.routes, pwm.routes])
app.get('(.*)', http.static)

import uasyncio as asyncio
loop = asyncio.get_event_loop()
loop.create_task(asyncio.start_server(app.handle, '0.0.0.0', 80))
loop.run_forever()
