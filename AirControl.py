import machine
import time

class SRControl:
    def __init__(self, data_pin, clock_pin, latch_pin,oe_pin, num_chips=1):
        """
        Initialize the 74HC595 shift register class.

        Args:
            data_pin (int): GPIO pin connected to the Data Input (DS) pin.
            clock_pin (int): GPIO pin connected to the Clock (SHCP) pin.
            latch_pin (int): GPIO pin connected to the Latch (STCP) pin.
            num_chips (int): Number of daisy-chained 74HC595 chips.
        """
        self.data = machine.Pin(data_pin, machine.Pin.OUT)
        self.clock = machine.Pin(clock_pin, machine.Pin.OUT)
        self.latch = machine.Pin(latch_pin, machine.Pin.OUT)
        self.oepin= machine.Pin(oe_pin, machine.Pin.OUT)

        # Initialize pins to low state
        self.data.value(0)
        self.clock.value(0)
        self.latch.value(0)
        self.oepin.value(1)

        self.num_chips = num_chips
        self.state = [0x00] * num_chips  # Current state of all shift registers

    def _pulse(self, pin):
        """Generate a pulse on the specified pin."""
        pin.value(0)
        time.sleep_ms(1)
        pin.value(1)
        time.sleep_ms(1)  # Small delay for stability
        pin.value(0)
        time.sleep_ms(1)

    def _shift_out(self):
        """
        Shift out the states of all daisy-chained 74HC595 chips.
        """
        for byte in reversed(self.state):
            for i in range(8):
                bit = (byte >> (7 - i)) & 1
                self.data.value(bit)
                self._pulse(self.clock)

    def update(self):
        """
        Latch and update the outputs of the shift register.
        """
        print(self.state)
        self.oepin.value(1)
        self._shift_out()
        self._pulse(self.latch)
        self.oepin.value(0)

    def set_relays(self, chip_index, low_nibble, duration=None):
        """
        Update the relays connected to a specific chip's low nibble.

        Args:
            chip_index (int): The index of the chip to update (0-based).
            low_nibble (int): The lower 4 bits (0-15) controlling relays.
                Bits 0 and 1 will turn on together and are mutually exclusive to bits 2 and 3.
            duration (int, optional): Time in seconds to keep the relays on. If None, relays remain on indefinitely.
        """
        if chip_index < 0 or chip_index >= self.num_chips:
            raise ValueError("Invalid chip index.")

        if low_nibble & 0b0011 and low_nibble & 0b1100:
            raise ValueError("Bits 0 and 1 cannot be active simultaneously with bits 2 and 3.")

        # Ensure only the lower nibble is considered
        low_nibble &= 0x0F

        # Update the state for the specified chip
        self.state[chip_index] = (self.state[chip_index] & 0xF0) | low_nibble
        
        self.update()

        if duration:
            time.sleep(duration)
            self.hold(chip_index)  # Turn off all relays for the specified chip after the duration

    def inflate(self, chip_index):
        """
        Activate relays 0 and 1 on the specified chip to turn on inflation for 15 seconds.
        """
        self.set_relays(chip_index, 0b0011)

    def deflate(self, chip_index):
        """
        Activate relays 2 and 3 on the specified chip to turn on deflation for 15 seconds.
        """
        self.set_relays(chip_index, 0b1100)

    def hold(self, chip_index=None):
        """
        Turn off all relays for a specific chip or all chips.

        Args:
            chip_index (int, optional): The index of the chip to hold. If None, all chips are held.
        """
        if chip_index is None:
            self.state = [0x00] * self.num_chips
        else:
            if chip_index < 0 or chip_index >= self.num_chips:
                raise ValueError("Invalid chip index.")
            self.state[chip_index] = 0x00
        self.update()# Write your code here :-)



# Sample Cod
# Connections
DIN  to D15
CLK to D2
LCH Pin to D4
OE to D5

#src=SRControl(15,2,4,5)
#while(True):
#    src.inflate(0)
#    time.sleep(1)
#    src.hold(0)
#    time.sleep(1)
#    src.deflate(0)
#    time.sleep(1)
#    src.hold(0)
#    time.sleep(1)
