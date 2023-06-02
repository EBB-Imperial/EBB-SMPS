#include "pico/stdlib.h"

from 
from machine import Pin, PWM

va, vb, vref, iL, current_mA
ev=0, cv=0,ei=0,oc=0
Ts=0.001
kpv=0.05024,kiv=15.78,kdv=0;
u0v,u1v,delta_ui,e0v,e1v,e2v;
kpi=0.02512,kii=39.4,kdi=0
u0i,u1i,delta_ui,e0i,e1i,e2i
uv_max=4,uv_min=0
ui_max=50,ui_min=0
current_limit=0.5 #GitHub中提供的LED driver的 current limite= 500mA



from machine import Pin, PWM

int main() { # 初始化代码放在这里 这里相当于void setup
    
    adc_gpio_init(GPIO_PIN1); # 配置GPIO_PIN1为ADC输入引脚
    adc_gpio_init(GPIO_PIN2); # 配置GPIO_PIN2为ADC输入引脚
    
    
    



while (1) {  # 主循环代码放在这里
     
     adc_select_input(0); # 选择ADC通道0，对应GPIO_PIN1
      uint16_t result1 = adc_read(); # 读取引脚1的ADC值

      adc_select_input(1); # 选择ADC通道1，对应GPIO_PIN2
      uint16_t result2 = adc_read(); # 读取引脚2的ADC值

      # Assuming e0v, e1v, e2v, u0v, u1v, kpv, kiv, kdv, Ts, uv_max, uv_min are all defined elsewhere

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
# Assuming e0i, e1i, e2i, u0i, u1i, kpi, kii, kdi, Ts, ui_max, ui_min are all defined elsewhere

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


 def saturation(saturation_input, upper_lim, lower_lim):
      if saturation_input > upper_lim:
         saturation_input = upper_lim
      elif saturation_input < lower_lim:
         saturation_input = lower_lim
      return saturation_input
      
# from machine import Pin, PWM

def pwm_modulate(pwm_input):
    pwm = PWM(Pin(?))  # create PWM object from a pin?  在Arduino中是Pin6 但是这里没懂是哪个PIN
    pwm.freq(625000)     # set frequency
    pwm.duty_u16(int((1 - pwm_input) * 65535)) # set duty cycle
    pass 

      cv = pidv(ev)  #voltage pid
      cv = saturation(cv, current_limit, 0) #current demand saturation

# Assuming iL is defined somewhere else
      ei = cv - iL #current error

      closed_loop = pidi(ei)  #current pid
      closed_loop = saturation(closed_loop, 0.99, 0.01)  #duty_cycle saturation

      pwm_modulate(closed_loop) #pwm modulation



    }

    return 0;
}
