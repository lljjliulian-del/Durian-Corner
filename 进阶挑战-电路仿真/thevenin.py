# -*- coding: utf-8 -*-
"""
电路② 戴维南定理验证
含源二端网络：V1=5V --R1=1k-- A --R2=2k--> 地，A --R3=1k--> 端口B
端口：B(+) 与 地(-)
理论值：V_oc = 3.333 V，I_sc = 2.0 mA，R_th = 1666.7 ohm
"""
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *


def build_original(load_ohm):
    """原网络，端口接负载电阻 load_ohm"""
    ckt = Circuit('Thevenin - original network')
    ckt.V('1', 'n1', ckt.gnd, 5@u_V)
    ckt.R('1', 'n1', 'A', 1@u_kOhm)
    ckt.R('2', 'A', ckt.gnd, 2@u_kOhm)
    ckt.R('3', 'A', 'B', 1@u_kOhm)
    ckt.R('L', 'B', ckt.gnd, load_ohm)
    return ckt


def build_equivalent(load_ohm):
    """戴维南等效电路：V_th 串 R_th 再接负载"""
    ckt = Circuit('Thevenin - equivalent circuit')
    ckt.V('th', 'T', ckt.gnd, 3.3333@u_V)
    ckt.R('th', 'T', 'B', 1666.67@u_Ohm)
    ckt.R('L', 'B', ckt.gnd, load_ohm)
    return ckt


def node_v(ckt, node='B'):
    op = ckt.simulator().operating_point()
    return float(op[node][0])


print('=========== 电路② 戴维南定理验证 ===========')
print('理论值: V_oc = 3.3333 V, I_sc = 2.000 mA, R_th = 1666.7 ohm')
print()

# --- 仿真1：端口近似开路，测开路电压 ---
V_oc_sim = node_v(build_original(1e9@u_Ohm))
print('仿真1 开路:      V_oc = %.4f V' % V_oc_sim)

# --- 仿真2：端口近似短路，测短路电流 ---
R_SHORT = 0.1
V_short = node_v(build_original(R_SHORT@u_Ohm))
I_sc_sim = V_short / R_SHORT
print('仿真2 短路:      V_B = %.6f V  ->  I_sc = %.4f mA' % (V_short, I_sc_sim*1e3))

# --- 由两次仿真推算等效电阻 ---
R_th_sim = V_oc_sim / I_sc_sim
print('          推算:   R_th = V_oc/I_sc = %.1f ohm' % R_th_sim)
print()

# --- 仿真3：接不同负载，比较原电路与等效电路 ---
for RL in (1e3, 2e3):
    v_orig = node_v(build_original(RL@u_Ohm))
    v_equi = node_v(build_equivalent(RL@u_Ohm))
    print('R_L = %.0f ohm:' % RL)
    print('    原电路  : V_L = %.4f V, I_L = %.4f mA' % (v_orig, v_orig/RL*1e3))
    print('    等效电路: V_L = %.4f V, I_L = %.4f mA' % (v_equi, v_equi/RL*1e3))
