"""Original rhythmic interface audio: crisp, minimal and quick. No copied music."""
import math
import random
import struct
import wave

def create_audio(path,seconds,sample_rate=32000):
    rng=random.Random(1616)
    # A tidy 120-BPM percussive bed with soft cues at four story beats.
    beat=.50
    transitions=[0.,seconds*.23,seconds*.485,seconds*.76]
    frames=bytearray()
    total=int(seconds*sample_rate)
    for i in range(total):
        t=i/sample_rate
        on=t%beat
        kick=(math.sin(2*math.pi*(103-52*min(on/.16,1))*on)*math.exp(-on*28)*.20
              if on<.20 else 0.)
        click_age=(t-beat*.5)%beat
        click=(rng.uniform(-1,1)*math.exp(-click_age*90)*.045
               if click_age<.055 else 0.)
        tick=0.
        for cue in transitions:
            age=t-cue
            if 0<=age<.27:
                tone=685+280*age
                tick+=math.sin(2*math.pi*tone*age)*math.exp(-age*25)*.077
        # Quiet harmonic pulse supports typography but never obscures speech.
        melody=(math.sin(2*math.pi*293.66*t)*.016+
                math.sin(2*math.pi*440*t)*.007)
        envelope=min(1.,t/.09,max(0.,(seconds-t)/.22))
        value=(kick+click+tick+melody)*envelope
        frames.extend(struct.pack("<h",int(max(-1.,min(1.,value))*32767)))
    with wave.open(str(path),"wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(frames)
