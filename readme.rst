MicroPython I2C driver for the Focus LCDs FT6336U capacitive touch panel controller IC.

Basic usage
===============

The driver requires a MicroPython I2C object to be instantiated.

.. code-block:: python

    from machine import I2C, Pin

    I2C_SDA_PIN = const(21)
    I2C_SCL_PIN = const(22)
    I2C_FREQ = const(400000)
    i2c_bus = I2C(sda=Pin(I2C_SDA_PIN), scl=Pin(I2C_SCL_PIN), freq=I2C_FREQ)

The FT6336U can then be instantiated:

.. code-block:: python

    import uFT6336U
    touch = uFT6336U.FT6336U(i2c_bus)
    touch.get_points()

Used with interrupt
===============

For best results, use with the designated interrupt pin.

.. code-block:: python

    INTERRUPT_PIN = 39

    def handle_interrupt(pin):
        num_points = touch.get_points()
        if num_points > 0:
            print(touch.get_p1_x(), touch.get_p1_y())
        if num_points == 2:
            print(touch.get_p2_x(), touch.get_p2_y())

    pir = Pin(INTERRUPT_PIN, Pin.IN)

    pir.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)