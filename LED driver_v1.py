from machine import Pin, ADC, PWM
from utime import sleep_ms, ticks_ms


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
class PID:
    def __init__(self, input_fun, output_fun, P=3., I=0.01, D=0.0, ui_max=100., ui_min=0., Ts=1.):
        self.Kp=P
        self.Ki=I
        self.Kd=D

        self.I_value = 0
        self.P_value = 0
        self.D_value = 0

        self.set_point=0.0
        self.prev_value = 0
        self.output = 0

        self.output_fun = output_fun
        self.input_fun = input_fun

        self.ui_max = ui_max
        self.ui_min = ui_min

        self.e0i = 0
        self.e1i = 0
        self.e2i = 0
        self.u0i = 0
        self.u1i = 0
        self.delta_ui = 0
        self.Ts = Ts  # Sample time

        self.last_update_time = ticks_ms()

    def update(self):

        if ticks_ms() - self.last_update_time > 500:

            self.e0i = self.set_point - self.input_fun()

            #anti-windup
            e_integration = self.e0i
            if self.u1i >= self.ui_max or self.u1i <= self.ui_min:
                e_integration = 0

            self.delta_ui = self.Kp * (self.e0i - self.e1i) + self.Ki * self.Ts * e_integration + self.Kd / self.Ts * (self.e0i - 2 * self.e1i + self.e2i)

            self.u0i = self.u1i + self.delta_ui  #this time's control output

            #output limitation
            self.u0i = max(min(self.u0i, self.ui_max), self.ui_min)
            
            self.u1i = self.u0i  # update last time's control output
            self.e2i = self.e1i  # update last last time's error
            self.e1i = self.e0i  # update last time's error

            self.output_fun(self.u0i / 100.0)

            self.last_update_time = ticks_ms()




def read_v():
    vmeas = vout_pin.read_u16() - vret_pin.read_u16()
    vref =  39719 # ~2V 
    return vref - vmeas
   

def read_i():
    imeas = vret_pin.read_u16() / 1.02
    write_v = PIDvoltage
    return write_v - imeas
    pass


def write_v(value):
    global PIDvoltage
    PIDvoltage = value
    return PIDvoltage

def write_i(value):
    duty = value  # 假设 value 的范围是 0 到 1
    duty = saturate(duty)  # 限制 duty 在合理的范围内
    pwm.duty_u16(duty)  # 设置 PWM 的占空比
    pass

pid_v = PID(read_v, write_v, P=0.05024, I=15.78, D=0)

pid_i = PID(read_i, write_i, P=0.02512, I=39, D=0)

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

    pid_v.update()
    pid_i.update()
   
    sleep_ms(50)

    if count > 2000:
        print("Vin = {:.0f}".format(vin))
        print("Vout = {:.0f}".format(vout))
        print("Vret = {:.0f}".format(vret))
        print("Duty = {:.0f}".format(pwm_out))

        count = 0

