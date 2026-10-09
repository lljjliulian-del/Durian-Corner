# -*- coding: utf-8 -*-
"""
电路③ NMOS 共源放大电路
VDD = 5 V, Rg1 = 60 kΩ, Rg2 = 40 kΩ, Rd = 2 kΩ, Cb1 = 1 µF（足够大）
NMOS: K = 0.8 mA/V², V_th = 1 V, λ = 0.02 /V
输入: Vi = 10 mV / 1 kHz 正弦

生成 figures/mos_cs_tran.png（输入/输出波形，体现反相放大）
并打印静态工作点、小信号参数与增益的仿真值，供 README 对比表使用
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

os.makedirs('figures', exist_ok=True)

# ==================== 1. 参数与理论值 ====================
VDD, Rg1, Rg2, Rd = 5.0, 60e3, 40e3, 2e3
K, VTH, LAM = 0.8e-3, 1.0, 0.02
FREQ = 1e3

V_G  = VDD*Rg2/(Rg1+Rg2)
V_GS = V_G
V_OV = V_GS - VTH
a    = 0.5*K*V_OV**2
I_D  = a*(1 + LAM*VDD)/(1 + a*LAM*Rd)      # 联立 I_D = a(1+λV_DS)、V_DS = VDD - I_D*Rd
V_DS = VDD - I_D*Rd
gm   = K*V_OV*(1 + LAM*V_DS)
ro   = (1 + LAM*V_DS)/(LAM*I_D)
Av   = -gm*(Rd*ro)/(Rd+ro)

print('=========== 电路③ NMOS 共源放大 ===========')
print('理论静态工作点: V_GS = %.4f V, I_D = %.4f mA, V_DS = %.4f V' % (V_GS, I_D*1e3, V_DS))
print('饱和区判断: V_DS = %.3f V > V_ov = %.3f V  ->  工作在饱和区' % (V_DS, V_OV))
print('理论小信号: gm = %.4f mA/V, ro = %.1f kohm, Av = %.4f' % (gm*1e3, ro/1e3, Av))
print()

# ==================== 2. 建电路 ====================
ckt = Circuit('NMOS common-source amplifier')
# 题目给的是 K，SPICE level-1 用 KP：
#   I_D = ½·KP·(W/L)·Vov² 与 I_D = ½·K·Vov² 相等  =>  KP·(W/L) = K
# 取 w = l（宽长比 1），则 KP = K = 0.8 mA/V²
ckt.model('NMOS1', 'NMOS', LEVEL=1, VTO=VTH, KP=K, LAMBDA=LAM)

ckt.V('dd', 'vdd', ckt.gnd, 5@u_V)
ckt.V('vi', 'vin', ckt.gnd, 'DC 0 AC 1 SIN(0 10m 1k)')
ckt.R('g1', 'vdd', 'g', 60@u_kOhm)
ckt.R('g2', 'g', ckt.gnd, 40@u_kOhm)
ckt.R('d', 'vdd', 'out', 2@u_kOhm)
ckt.C('b1', 'vin', 'g', 1@u_uF)
ckt.M(1, 'out', 'g', ckt.gnd, ckt.gnd, model='NMOS1', w=100@u_um, l=100@u_um)

sim = ckt.simulator()

# ==================== 3. 静态工作点 ====================
op = sim.operating_point()
V_GS_sim = float(op['g'][0])
V_DS_sim = float(op['out'][0])
I_D_sim  = (VDD - V_DS_sim)/Rd
print('仿真静态工作点: V_GS = %.4f V, I_D = %.4f mA, V_DS = %.4f V'
      % (V_GS_sim, I_D_sim*1e3, V_DS_sim))
print('                相对误差: I_D = %.3f%%, V_DS = %.3f%%'
      % (abs(I_D_sim-I_D)/I_D*100, abs(V_DS_sim-V_DS)/V_DS*100))
print()

# ==================== 4. 瞬态：输入输出波形 ====================
tran = sim.transient(step_time=2@u_us, end_time=5@u_ms)
t    = np.array(tran.time)
vin  = np.array(tran['vin'])
vout = np.array(tran['out'])

# 仿真会用直流工作点作为瞬态初始条件，Cb1 一开始就已经充好电，
# 所以不需要等待建立过程，直接取后 3 ms 做测量即可
mask = t >= 2e-3
tw, viw, voutw = t[mask], vin[mask], vout[mask]

vi_pp    = viw.max() - viw.min()
vo_pp    = voutw.max() - voutw.min()
gain_abs = vo_pp/vi_pp
# 判反相：输入处于最大值时，输出处在自身均值以下
gain_sim = -gain_abs if voutw[np.argmax(viw)] < voutw.mean() else gain_abs

print('仿真瞬态: Vi_pp = %.2f mV, Vo_pp = %.2f mV  ->  实测增益 Av = %.4f'
      % (vi_pp*1e3, vo_pp*1e3, gain_sim))
print('          与理论值 %.4f 的相对误差: %.2f%%' % (Av, abs(gain_sim-Av)/abs(Av)*100))
print()

# ==================== 5. 交流分析（交叉验证） ====================
ac = sim.ac(start_frequency=10@u_Hz, stop_frequency=1@u_MHz,
            number_of_points=10, variation='dec')
f = np.array(ac.frequency)
h = np.array(ac['out'])
k = int(np.argmin(np.abs(f-FREQ)))
print('仿真 AC @1 kHz: |Av| = %.4f, 相位 = %.1f 度（180 度即反相）'
      % (abs(h[k]), np.angle(h[k], deg=True)))
print()

# ==================== 6. 画图 ====================
tt = (tw - tw[0])*1e3
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
ax1.plot(tt, viw*1e3, color='tab:blue')
ax1.set_ylabel('Vin (mV)')
ax1.grid(alpha=0.3)
ax1.set_title('NMOS common-source amplifier - inverting amplification')

ax2.plot(tt, voutw*1e3, color='tab:red')
ax2.set_ylabel('Vout (mV)')
ax2.set_xlabel('Time (ms)')
ax2.grid(alpha=0.3)
ax2.text(0.02, 0.08, 'measured gain = %.3f' % gain_sim, transform=ax2.transAxes)

fig.tight_layout()
fig.savefig('figures/mos_cs_tran.png', dpi=150)
print('已保存 figures/mos_cs_tran.png')
