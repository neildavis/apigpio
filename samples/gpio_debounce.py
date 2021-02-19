import asyncio
import apigpio
import functools

# This sample demonstrates both writing to gpio and listening to gpio changes.
# It also shows the Debounce decorator, which might be useful when registering
# a callback for a gpio connected to a button, for example.

BT_GPIO = 18
LED_GPIO = 21


class Blinker(object):
    """
    Led Blinker
    """
    def __init__(self, pi, gpio):
        self.pi = pi
        self.led_gpio = gpio
        self.blink = False

    async def start(self):
        self.blink = True
        print('Start Blinking')
        is_on = True
        while self.blink:
            if is_on:
                await self.pi.write(self.led_gpio, apigpio.ON)
            else:
                await self.pi.write(self.led_gpio, apigpio.OFF)

            is_on = not is_on
            await asyncio.sleep(0.2)
        await self.pi.write(self.led_gpio, apigpio.OFF)

    def stop(self):
        self.blink = False

    def toggle(self):
        if not self.blink:
            asyncio.async(self.start())
        else:
            print('Stop Blinking')
            self.blink = False

# The DeBounce can simply be applied to your callback.
# Optionnally, the threshold can be specified in milliseconds : @Debounce(200)


@apigpio.Debounce()
def on_bt(gpio, level, tick, blinker=None):
    print('on_input {} {} {}'.format(gpio, level, tick))
    blinker.toggle()


async def subscribe(pi):

    await pi.set_mode(BT_GPIO, apigpio.INPUT)
    await pi.set_mode(LED_GPIO, apigpio.OUTPUT)

    blinker = Blinker(pi, LED_GPIO)

    # functools.partial is usefull when your callback requires extra arguments:
    cb = functools.partial(on_bt, blinker=blinker)
    await pi.add_callback(BT_GPIO, edge=apigpio.RISING_EDGE,
                               func=cb)


async def main():
    address = ('192.168.1.3', 8888)
    pi = apigpio.Pi()
    await pi.connect(address)
    await subscribe(pi)
    asyncio.get_event_loop.run_forever()

if __name__ == '__main__':
    asyncio.run(main())