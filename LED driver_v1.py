from machine import Pin, ADC, PWM

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

  def pidv(pid_input):
    e_integration = e0v = pid_input
    
    # anti-windup, if last-time pid output reaches the limitation, this time there won't be any integrations.
    if u1v >= uv_max or u1v <= uv_min:
        e_integration = 0

    delta_uv = kpv * (e0v - e1v) + kiv * Ts * e_integration + kdv / Ts * (e0v - 2 * e1v + e2v)
    u0v = u1v + delta_uv

    # output limitation
    u0v = saturation(u0v, uv_max, uv_min)
    
    u1v = u0v # update last time's control output
    e2v = e1v # update last last time's error
    e1v = e0v # update last time's error
    return u0v
# e0i, e1i, e2i, u0i, u1i, kpi, kii, kdi, Ts, ui_max, ui_min are all defined before

  def pidi(pid_input):
    e_integration = e0i = pid_input
    
    # anti-windup
    if u1i >= ui_max or u1i <= ui_min:
        e_integration = 0

    delta_ui = kpi * (e0i - e1i) + kii * Ts * e_integration + kdi / Ts * (e0i - 2 * e1i + e2i)
    u0i = u1i + delta_ui

    # output limitation
    u0i = saturation(u0i, ui_max, ui_min)
    
    u1i = u0i # update last time's control output
    e2i = e1i # update last last time's error
    e1i = e0i # update last time's error
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

    
    pwm_ref = 25000
    pwm_out = saturate(pwm_ref)
    pwm.duty_u16(pwm_out)
    
    Iout = vret/1.02
    
    if count > 2000:
        print("Vin = {:.0f}".format(vin))
        print("Vout = {:.0f}".format(vout))
        print("Vret = {:.0f}".format(vret))
        print("Duty = {:.0f}".format(pwm_out))
        
        count = 0
