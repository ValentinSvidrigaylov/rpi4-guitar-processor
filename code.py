import time

import supervisor
supervisor.runtime.autoreload = False

import board
import digitalio
import analogio
from analogio import AnalogIn
import busio
import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.program_change import ProgramChange

#pwm stuff
import pwmio

p=0
pwm_dir = True

cycle = range(0,65535,500)

pwm = pwmio.PWMOut(board.GP15)
pwm.duty_cycle = 0  

# Read analog pin voltage
def get_voltage(value):
    return (value * 3.3) / 65536

led = digitalio.DigitalInOut(board.GP22)
led.direction = digitalio.Direction.OUTPUT
usb_midi = adafruit_midi.MIDI(
    midi_out=usb_midi.ports[1],
    out_channel=15,
    debug=True
    )

def ledOn():
    led.value = True

def ledOff():
    led.value = False

MIDI_CC_BANKSEL_MSB = 0
MIDI_CC_BANKSEL_LSB = 32

MIDI_CC_MODWHEEL = 1
MIDI_CC_BRCONTROL = 2
MIDI_CC_UNDEFINED = 3

MIDI_CC_FOOT_CONTROLLER = 4

MIDI_CC_PORTAMENTO_TIME = 5
MIDI_CC_DATA_ENTRY = 6
MIDI_CC_VOLUME = 7
MIDI_CC_BALANCE = 8
MIDI_CC_UNDEFINED2 = 9
MIDI_CC_PAN = 10
MIDI_CC_EXPRESSION = 11
MIDI_CC_EFFECT_C1 = 12
MIDI_CC_EFFECT_C2 = 13
MIDI_CC_UNDEFINED3 = 14
MIDI_CC_UNDEFINED4 = 15
MIDI_CC_GENERAL_PURPOSE1 = 16
MIDI_CC_GENERAL_PURPOSE2 = 17
MIDI_CC_GENERAL_PURPOSE3 = 18
MIDI_CC_GENERAL_PURPOSE4 = 19
MIDI_CC_UNDEFINED5 = 20
MIDI_CC_UNDEFINED6 = 21
MIDI_CC_UNDEFINED7 = 22
MIDI_CC_UNDEFINED8 = 23
MIDI_CC_UNDEFINED9 = 24
MIDI_CC_UNDEFINED10 = 25
MIDI_CC_UNDEFINED11 = 26
MIDI_CC_UNDEFINED12 = 27
MIDI_CC_UNDEFINED13 = 28
MIDI_CC_UNDEFINED14 = 29
MIDI_CC_UNDEFINED15 = 30
MIDI_CC_UNDEFINED16 = 31
MIDI_CC_SOFT_PEDAL = 67
MIDI_CC_SOUND_CONTROLLER1 = 75
MIDI_CC_SOUND_CONTROLLER2 = 76

ledOn()

# Switch OFF will be HIGH (operating in PULL_UP mode), mapping below
btns = []
lastbtns = []
btn_pins = [board.GP6, board.GP7, board.GP16, board.GP14, board.GP17, board.GP18, board.GP19, board.GP20, board.GP21]
btn_controls = [MIDI_CC_BANKSEL_MSB, MIDI_CC_BANKSEL_LSB, MIDI_CC_FOOT_CONTROLLER, MIDI_CC_UNDEFINED12, MIDI_CC_UNDEFINED15, MIDI_CC_UNDEFINED16, MIDI_CC_SOFT_PEDAL, MIDI_CC_SOUND_CONTROLLER1, MIDI_CC_SOUND_CONTROLLER2]
numbtns = len(btn_pins)
btn_states_map = []
for bp in range(0, numbtns):
    btns.append(digitalio.DigitalInOut(btn_pins[bp]))
    btns[bp].switch_to_input(pull=digitalio.Pull.UP)
    lastbtns.append(True)
    btn_states_map.append(False)

footswchs = []
lastfootswchs = []
footswchs_pins = [board.GP8]
footswchs_controls = [MIDI_CC_UNDEFINED13]
numfootswchs = len(footswchs_pins)
footswchs_states_map = []
for fp in range(0, numfootswchs):
    footswchs.append(digitalio.DigitalInOut(footswchs_pins[fp]))
    footswchs[fp].switch_to_input(pull=digitalio.Pull.UP)
    lastfootswchs.append(True)
    footswchs_states_map.append(False)
    
#using mcp3008
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn as AnalogInMCP

# create the spi bus
spi = busio.SPI(clock=board.GP2, MISO=board.GP4, MOSI=board.GP3)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.GP5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)
    
# create the spi bus
spi1 = busio.SPI(clock=board.GP10, MISO=board.GP12, MOSI=board.GP11)

# create the cs (chip select)
cs1 = digitalio.DigitalInOut(board.GP13)

# create the mcp object
mcp1 = MCP.MCP3008(spi1, cs1)
    
knobs = []
lastknobs = []
knobs_pins = [AnalogInMCP(mcp, MCP.P0), AnalogInMCP(mcp, MCP.P1), AnalogInMCP(mcp, MCP.P2), AnalogInMCP(mcp, MCP.P3), AnalogInMCP(mcp, MCP.P4), AnalogInMCP(mcp, MCP.P5), AnalogInMCP(mcp, MCP.P6), AnalogInMCP(mcp, MCP.P7), AnalogInMCP(mcp1, MCP.P0), AnalogInMCP(mcp1, MCP.P1), AnalogInMCP(mcp1, MCP.P2), AnalogInMCP(mcp1, MCP.P3), AnalogInMCP(mcp1, MCP.P4), AnalogInMCP(mcp1, MCP.P5), AnalogInMCP(mcp1, MCP.P6), AnalogInMCP(mcp1, MCP.P7), AnalogIn(board.GP26), AnalogIn(board.GP27), AnalogIn(board.GP28)]
knobs_controls = [MIDI_CC_PORTAMENTO_TIME, MIDI_CC_DATA_ENTRY, MIDI_CC_VOLUME, MIDI_CC_BALANCE, MIDI_CC_UNDEFINED2, MIDI_CC_PAN, MIDI_CC_EXPRESSION, MIDI_CC_EFFECT_C1, MIDI_CC_EFFECT_C2, MIDI_CC_UNDEFINED3, MIDI_CC_UNDEFINED4, MIDI_CC_UNDEFINED5, MIDI_CC_UNDEFINED6, MIDI_CC_UNDEFINED7, MIDI_CC_UNDEFINED8, MIDI_CC_UNDEFINED9, MIDI_CC_UNDEFINED10, MIDI_CC_UNDEFINED11, MIDI_CC_UNDEFINED14]
numknobs = len(knobs_pins)
knobs_states_map = []
for kp in range(0, numknobs):
    knobs.append(knobs_pins[kp])
    lastknobs.append(True)
    knobs_states_map.append(knobs[kp].value)
    
ledOff()
i = False
ff=0

def midiBankSelect(control, map_to_change, index):
    ledOn()
    print(control)
    if control == MIDI_CC_BANKSEL_MSB:
        usb_midi.send(ControlChange(0, 127))
        print(0)
    elif control == MIDI_CC_BANKSEL_LSB:
        usb_midi.send(ControlChange(0, 0))
        print(-0.0)
    elif control == MIDI_CC_FOOT_CONTROLLER:
        print(1)
        if map_to_change[index]:
            usb_midi.send(ProgramChange(0)) #ON
            map_to_change[index] = False
        elif not map_to_change[index]:
        	usb_midi.send(ProgramChange(1)) #OFF
        	map_to_change[index] = True
    elif map_to_change[index]:
        usb_midi.send(ControlChange(control, 127)) #ON
        map_to_change[index] = False
    elif not map_to_change[index]:
        usb_midi.send(ControlChange(control, 0)) #OFF
        map_to_change[index] = True
    ledOff()

def midiBankSelectCustomValue(control, map_to_change, index, value):
    ledOn()
    if map_to_change[index]:
        usb_midi.send(ControlChange(control, value)) #ON
        map_to_change[index] = False
    elif not map_to_change[index]:
        usb_midi.send(ControlChange(control, value)) #OFF
        map_to_change[index] = True
    ledOff()

while True:
    # Scan for buttons pressed on the rows
    # Any pressed buttons will be LOW
    for b in range(0, numbtns):
        if (btns[b].value == False) and (lastbtns[b] == True):
            # Button Pressed
            midiBankSelect(btn_controls[b], btn_states_map, b)
        lastbtns[b] = btns[b].value
        
    for f in range(0, numfootswchs):
        if (footswchs_states_map[f] != footswchs[f].value):
            #Footswitch Pressed
            midiBankSelect(footswchs_controls[f], footswchs_states_map, f)
            footswchs_states_map[f] = footswchs[f].value
            
        lastfootswchs[f] = footswchs[f].value
        
    for k in range(0, numknobs):
        if (knobs_states_map[k]*127/65535 <= knobs[k].value*127/65535 - 3 or knobs_states_map[k]*127/65535 >= knobs[k].value*127/65535 + 3):
            knob_val = int(knobs[k].value/65535*127)
            midiBankSelectCustomValue(knobs_controls[k], knobs_states_map, k, knob_val)
            print(knobs[k].value)
            knobs_states_map[k] = knobs[k].value
        lastknobs[k] = knobs[k].value
    pwm.duty_cycle = cycle[p]  # Cycles the LED pin duty cycle through the range of values
    p+=1
    if p >= len(cycle):
        p=0
        if pwm_dir:
            cycle = range(65534, 0, -500)
        elif not pwm_dir:
            cycle = range(0, 65535, 500)
        pwm_dir = not pwm_dir
        if cycle == range(0, 65535, 500):
            cycle = range(65534, 0, -500)
        elif cycle == range(65534, 0, -500):
            cycle = range(0, 65535, 500)
