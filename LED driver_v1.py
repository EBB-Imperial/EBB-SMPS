from machine import Pin, ADC, PWM
from pid import PID

vret_pin = ADC(Pin(26))
vout_pin = ADC(Pin(28))
vin_pin = ADC(Pin(27))
pwm = PWM(Pin(0))
pwm.freq(100000)
pwm_en = Pin(1, Pin.OUT)
Iout=0

count = 0
pwm_out = 0
pwm_ref = 0
setpoint = 0.0
delta = 0.05


read_v = vref - vmeas
read_i = write_v - imeas


pid_i = PID(read_i, write_i, P=0.05024, I=15.78, D=0)
pid_v = PID(read_v, write_v, P=0.02512, I=39.4, D=0)



def saturate(duty):
    if duty > 62500:
        duty = 62500
    if duty < 100:
        duty = 100
    return duty

while True:
    
    pwm_en.value(1)

    vin = vin_pin.read_u16()
    vout = vout_pin.read_u16()
    vret = vret_pin.read_u16()
    count = count + 1

    
    pwm_ref = 25000
    pwm_out = saturate(pwm_ref)
    pwm.duty_u16(pwm_out)
    
    Iout = vret/1.02
    
    pid_i.update()
    pid_v.update()
    pyb.delay(50)

    if count > 2000:
        print("Vin = {:.0f}".format(vin))
        print("Vout = {:.0f}".format(vout))
        print("Vret = {:.0f}".format(vret))
        print("Duty = {:.0f}".format(pwm_out))
        
        count = 0
