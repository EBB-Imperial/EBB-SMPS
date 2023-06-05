from machine import Pin, ADC, PWM
from pid import PID
from  import pyb

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
   def __init__(self,input_fun,output_fun, P=3., I=0.01, D=0.0):

        self.Kp=P
        self.Ki=I
        self.Kd=D

        self.I_value = 0
        self.P_value = 0
        self.D_value = 0

        self.I_max=100.0
        self.I_min=0

        self.set_point=0.0

        self.prev_value = 0

        self.output = 0

        self.output_fun = output_fun
        self.input_fun = input_fun

        self.last_update_time = pyb.millis()


def update(self):

        if pyb.millis()-self.last_update_time > 500:
            """
            Calculate PID output value for given reference input and feedback
            """
            current_value = self.input_fun()
            self.error = self.set_point - current_value
            print ('temp '+str(current_value))
            print ('SP'+str(self.set_point))

            self.P_value = self.Kp * self.error
            self.D_value = self.Kd * ( current_value-self.prev_value)


            lapsed_time = pyb.millis()-self.last_update_time
            lapsed_time/=1000. #convert to seconds
            self.last_update_time = pyb.millis()


            self.I_value += self.error * self.Ki

            if self.I_value > self.I_max:
                self.I_value = self.I_max
            elif self.I_value < self.I_min:
                self.I_value = self.I_min

            self.output = self.P_value + self.I_value - self.D_value

            if self.output<0:
                self.output = 0.0
            if self.output>100:
                self.output = 100.0

            print("Setpoint: "+str(self.set_point))
            print("P: "+str(self.P_value))
            print("I: "+str(self.I_value))
            print("Output: "+str(self.output))
            print ()

            self.output_fun(self.output/100.0)

            self.last_update_time=pyb.millis()


def read_v():
    vmeas = vout_pin.read_u16() - vret_pin.read_u16()
    vref =  39719 # ~2V 
    return vref - vmeas
   

def read_i():
    imeas = vret_pin.read_u16() / 1.02
    write_v = PIDvoltage
    return write_v - imeas
    pass

# write_v 和 write_i 也应该是函数

#def write_v(value):
#    duty = value * 62500  # 假设 value 的范围是 0 到 1
#   duty = saturate(duty)  # 限制 duty 在合理的范围内
#    pwm.duty_u16(duty)  # 设置 PWM 的占空比


def write_v(value):
    global PIDvoltage
    PIDvoltage = value
    return PIDvoltage

def write_i(value):
    duty = value  # 假设 value 的范围是 0 到 1
    duty = saturate(duty)  # 限制 duty 在合理的范围内
    pwm.duty_u16(duty)  # 设置 PWM 的占空比
    pass

pid_v = PID(read_v, write_v, P=0.02512, I=39.4, D=0)

pid_i = PID(read_i, write_i, P=0.05024, I=15.78, D=0)

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

    
    pid_i.update()
    pid_v.update()
    pyb.delay(50)

    if count > 2000:
        print("Vin = {:.0f}".format(vin))
        print("Vout = {:.0f}".format(vout))
        print("Vret = {:.0f}".format(vret))
        print("Duty = {:.0f}".format(pwm_out))

        count = 0
