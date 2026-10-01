# -*- coding: utf-8 -*-
"""Pro A/B representation rule, Python2.7 compatible; never changes native time."""
from __future__ import print_function
import struct,math
def finite(x):return not math.isnan(x) and not math.isinf(x)
def q32(t):return struct.unpack('>f',struct.pack('>f',t))[0]
def ulp_positive(x,fmt,bitsfmt):
    bits=struct.unpack(bitsfmt,struct.pack(fmt,x))[0]
    return struct.unpack(fmt,struct.pack(bitsfmt,bits+1))[0]-x
def time_audit(tf,T):
    tf,T=float(tf),float(T)
    if not finite(tf) or not finite(T) or tf<0 or T<=0:raise ValueError('Nonfinite/invalid time identity')
    q=q32(T);u32=ulp_positive(q,'>f','>I');u64=ulp_positive(q,'>d','>Q')
    error=abs(tf-T);a=error<=1e-8*T;b=abs(tf-q)<=8*u64 and error<=.5*u32+8*u64
    return {'pass':a or b,'rule_A':a,'rule_B':b,'native_time_s':tf,'contract_duration_s':T,'q32_target_s':q,'abs_error_s':error,'ulp32_s':u32,'ulp64_s':u64,'raw_native_time_unchanged':True}
