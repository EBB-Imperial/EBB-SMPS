from machine import Pin, ADC, PWM

vret_pin = ADC(Pin(26)) # Initializing ADC objects for measuring voltages vret on pin 26
vout_pin = ADC(Pin(28)) # Initializing ADC objects for measuring voltages vout on pin 28
vin_pin = ADC(Pin(27)) # Initializing ADC objects for measuring voltages vin on pin 27
pwm = PWM(Pin(0)) # Initializing a PWM object on pin 0
pwm.freq(100000) # Setting the PWM frequency to 100 kHz
pwm_en = Pin(1, Pin.OUT) # Initializing a digital output pin to enable PWM 

# Initializing variables to store intermediate values and states
count = 0
pid_input = 0
pwm_out = 0
pwm_ref = 0
setpoint = 0.0
delta = 0.05

current_limit = 0.07 # Current limit in amperes, 0.07A is the lower current limit to achieve the most stable brightness

# A function to limit the PWM duty cycle to a safe range
def saturate(duty):
    if duty > 62500:
        duty = 62500
    if duty < 100:
        duty = 100
    return duty

while True:
    
    pwm_en.value(1)  # Enabling the PWM by setting the enable pin high
    
    # Reading 16-bit ADC values (0-65535) from the pins
    vin = vin_pin.read_u16()
    vout = vout_pin.read_u16()
    vret = vret_pin.read_u16()
    count = count + 1 # Incrementing the counter for debugging (print statements) purposes

    # Converting raw ADC values to voltages (3.3V reference)
    vinV = vin_pin.read_u16()*3.3/65536
    voutV = vout_pin.read_u16()*3.3/65536
    vretV = vret_pin.read_u16()*3.3/65536

    Iout=vretV/1.02  # reading the output current based on the current sensor.

    # Checking if the output current is too high
    if Iout > 2 * current_limit:
        pid_input /= 2
    # If output current is greater than limit, decrease the pid_input
    if Iout > current_limit:
       pid_input -= 2000
       pid_input = int(pid_input)
    # If output current is within the limit, increase the pid_input
    elif Iout <= current_limit:
       pid_input += 1000


     
    pwm_out = saturate(pid_input) # Making sure that the PWM output is within the safe range
    pwm.duty_u16(pwm_out) # Set the duty cycle of the PWM output
    
    
    # Scaling and converting the raw ADC values to meaningful voltage levels, which is useful for testing
    Vin = 5*vin*3.3/65535
    Vout = 5*vout*3.3/65535
    Vret = 5*vret*3.3/65535
    Pwm_out =pwm_out*100/65535 # Converting the raw PWM duty cycle to a percentage, which is useful for testing
    
    
    # for debugging
    if count > 2000:
        print("Vin = {:.2f}".format(Vin))
        print("Vout = {:.2f}".format(Vout))
        print("Vret = {:.2f}".format(Vret))
        print("Duty = {:.2f}".format(Pwm_out))
        print('Iout = {:.2f}'.format(Iout))
        count = 0
