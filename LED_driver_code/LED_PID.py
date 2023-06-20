from machine import Pin, ADC, PWM


vret_pin = ADC(Pin(26))
vout_pin = ADC(Pin(28))
vin_pin = ADC(Pin(27))
pwm = PWM(Pin(0))
pwm.freq(100000)
pwm_en = Pin(1, Pin.OUT)

count = 0
pwm_ref = 0
setpoint = 0.0
delta = 0.05

PIDvoltage = 0

Kp = 10
Ki = 10
Kd = 0.0
ui_max = 10000	#To be debugged HERE
ui_min = 0.0
Ts = 0.001
iref= 0.07 #0.2A
e0i = 0.0
e1i = 0.0
e2i = 0.0
u0i = 0.0
u1i = 0.0
delta_ui = 0.0

e_integration = 0.0

def pidi(pid_input):
    global e0i, e1i, e2i, u0i, u1i, delta_ui, e_integration

    e0i = pid_input

    # anti-windup
    e_integration += e0i
    if u1i >= ui_max or u1i <= ui_min:
        e_integration = 0


    delta_ui = Kp * (e0i) + Ki * Ts * e_integration

    u0i = u0i + delta_ui  # this time's control output

    # output limitation
    u0i = saturate(u0i)

    u1i = u0i  # update last time's control output
    e2i = e1i  # update last last time's error
    e1i = e0i  # update last time's error

    return u0i



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
    
    vinV = vin*3.3/65536
    voutV = vout_pin.read_u16()*3.3/65536
    vretV = vret_pin.read_u16()*3.3/65536
    
    iL = vretV/1.02
    
    ei=iref-iL
    pid_input = ei  # Replace with your actual PID input
    pwm_out = int(pidi(pid_input))
    pwm.duty_u16(pwm_out)
   

    

    if count > 2000:
        print("Vin = {:.2f}".format(vinV*5))
        print("Vout = {:.2f}".format(voutV*5))
        print("Vret = {:.2f}".format(vretV*5))
        print("Duty = {:.2f}".format(float(pwm_out/65536)))
        print('Iout = {:.2f}'.format(iL))
        print('Current Error = {:.2f}'.format(float(pid_input)))
        print('PID OUT = {:.2f}'.format(float(delta_ui/65536)))

        print (float(e_integration))

        count = 0

