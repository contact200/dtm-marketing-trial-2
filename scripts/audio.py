"""Generative, original minimal electronic pulse soundtrack. No copyrighted recordings."""
import math
import random
import struct
import wave

def create_audio(path,seconds,sample_rate=32000):
    rng=random.Random(2026)
    beat_positions=[(0.2,196),(1.7,293.66),(3.3,246.94),(4.8,392),
                    (6.4,293.66),(8.2,369.99),(9.7,246.94),(11.1,196)]
    frames=bytearray()
    total=int(seconds*sample_rate)
    for i in range(total):
        t=i/sample_rate
        swell=min(1,t/.9,max(0,(seconds-t)/1.2))
        chord=(math.sin(2*math.pi*98*t)*.27+math.sin(2*math.pi*146.83*t)*.15+
               math.sin(2*math.pi*196*t)*.12)*.19
        bell=0.0
        for onset,freq in beat_positions:
            age=t-onset
            if 0<=age<2.3:
                env=(1-math.exp(-age*25))*math.exp(-age*2.0)
                bell+=env*(math.sin(2*math.pi*freq*age)+.18*math.sin(2*math.pi*freq*2.02*age))*.08
        wind=(rng.random()-.5)*.006
        value=(chord+bell+wind)*swell
        frames.extend(struct.pack('<h',int(max(-1,min(1,value))*32767)))
    with wave.open(str(path),'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(frames)
