# -*- coding: utf-8 -*-
"""
电路① RC 低通滤波电路
参数：R = 1 kΩ, C = 100 nF

生成：
    figures/rc_tran.png   方波输入 / 输出瞬态波形
    figures/rc_bode.png   幅频 + 相频波特图
并打印仿真测得的 tau 与 fc，供 README 对比表使用
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')                      # WSL 无图形界面，图片直接存盘
import matplotlib.pyplot as plt

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

os.makedirs('figures', exist_ok=True)

# ==================== 1. 参数与理论值 ====================
R_OHM, C_FARAD = 1e3, 100e-9
TAU_TH = R_OHM * C_FARAD
FC_TH = 1.0 / (2 * np.pi * TAU_TH)
print('理论值:  tau = %.1f us   fc = %.2f Hz' % (TAU_TH * 1e6, FC_TH))

# ==================== 2. 瞬态：方波响应 ====================
ckt = Circuit('RC low-pass filter')
ckt.PulseVoltageSource('pulse', 'vin', ckt.gnd,
                       initial_value=0@u_V, pulsed_value=1@u_V,
                       delay_time=0@u_s, rise_time=1@u_ns, fall_time=1@u_ns,
                       pulse_width=0.5@u_ms, period=1@u_ms)
ckt.R(1, 'vin', 'vout', 1@u_kOhm)
ckt.C(1, 'vout', ckt.gnd, 100@u_nF)

tran = ckt.simulator().transient(step_time=1@u_us, end_time=5@u_ms)
t    = np.array(tran.time)
vin  = np.array(tran['vin'])
vout = np.array(tran['vout'])

# 第一个高电平半周期内，输出从 v0 向 v1 指数充电：到 63.2% 的时刻差即为 tau
half = t <= 0.5e-3
tw, vw = t[half], vout[half]
v0, v1 = vw[0], vw[-1]
target = v0 + 0.632 * (v1 - v0)
TAU_SIM = tw[np.argmax(vw >= target)]
print('仿真 tau = %.1f us' % (TAU_SIM * 1e6))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
ax1.plot(t * 1e3, vin, color='tab:blue')
ax1.set_ylabel('Vin (V)')
ax1.grid(alpha=0.3)
ax1.set_title('RC low-pass filter - square wave response')

ax2.plot(t * 1e3, vout, color='tab:red')
ax2.axhline(target, color='gray', ls='--', lw=1)
ax2.plot(TAU_SIM * 1e3, target, 'ko')
ax2.annotate('63.2%% -> tau = %.0f us' % (TAU_SIM * 1e6),
             xy=(TAU_SIM * 1e3, target), xytext=(1.2, 0.7),
             arrowprops=dict(arrowstyle='->'))
ax2.set_xlabel('Time (ms)')
ax2.set_ylabel('Vout (V)')
ax2.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('figures/rc_tran.png', dpi=150)
print('已保存 figures/rc_tran.png')

# ==================== 3. 交流扫描：波特图 ====================
ckt_ac = Circuit('RC low-pass filter (AC)')
ckt_ac.V('ac', 'vin', ckt_ac.gnd, 'DC 0 AC 1')
ckt_ac.R(1, 'vin', 'vout', 1@u_kOhm)
ckt_ac.C(1, 'vout', ckt_ac.gnd, 100@u_nF)

ac  = ckt_ac.simulator().ac(start_frequency=10@u_Hz, stop_frequency=1@u_MHz,
                            number_of_points=100, variation='dec')
f   = np.array(ac.frequency)
h   = np.array(ac['vout'])
mag = 20 * np.log10(np.abs(h))
pha = np.angle(h, deg=True)

# -3 dB 点：幅频单调下降，反转后用线性插值找交点，比直接取点更准
FC_SIM = np.interp(-3.0103, mag[::-1], f[::-1])
print('仿真 fc  = %.2f Hz' % FC_SIM)

fig2, (bx1, bx2) = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
bx1.semilogx(f, mag, color='tab:blue')
bx1.axhline(-3.0103, color='gray', ls='--', lw=1)
bx1.plot(FC_SIM, -3.0103, 'ko')
bx1.annotate('fc = %.1f Hz' % FC_SIM, xy=(FC_SIM, -3.0103), xytext=(1e4, -1),
             arrowprops=dict(arrowstyle='->'))
bx1.set_ylabel('Magnitude (dB)')
bx1.grid(which='both', alpha=0.3)
bx1.set_title('RC low-pass filter - Bode plot')

bx2.semilogx(f, pha, color='tab:red')
bx2.set_xlabel('Frequency (Hz)')
bx2.set_ylabel('Phase (deg)')
bx2.grid(which='both', alpha=0.3)
fig2.tight_layout()
fig2.savefig('figures/rc_bode.png', dpi=150)
print('已保存 figures/rc_bode.png')

print('-------- 对比表数据 --------')
print('tau: 理论 %.1f us | 仿真 %.1f us' % (TAU_TH * 1e6, TAU_SIM * 1e6))
print('fc : 理论 %.2f Hz | 仿真 %.2f Hz' % (FC_TH, FC_SIM))
