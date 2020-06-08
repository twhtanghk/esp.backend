# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
#import webrepl
#webrepl.start()
import system
import pwm
system.setting = pwm.Config()
system.setting.boot()
import gc
gc.collect()
