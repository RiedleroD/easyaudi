#!/usr/bin/python3.7
import ctypes,sys,random, math,asyncio, time, struct

PA_STREAM_PLAYBACK = 1

PA_SAMPLE_U8		= 0
PA_SAMPLE_S16LE		= 1	#these two
PA_SAMPLE_S16BE		= 2 #don't work very good, for some reason. It crackles.
PA_SAMPLE_FLOAT32LE	= 3
PA_SAMPLE_FLOAT32BE	= 4
PA_SAMPLE_ALAW		= 5	#these break
PA_SAMPLE_ULAW		= 6 #everything
PA_SAMPLE_S32LE		= 7
PA_SAMPLE_S32BE		= 8
PA_SAMPLE_S24_32LE	= 9
PA_SAMPLE_S24_32BE	= 10

PA_SAMPLE_FORM  = PA_SAMPLE_S32LE

BIGGEST_SAMPLES=[255,65535,65535,4294967295,4294967295,None,None,2147483647,2147483647,16777215,16777215,16777215,16777215]
BIGGEST_SAMPLE= BIGGEST_SAMPLES[PA_SAMPLE_FORM]

NEUTRAL_SAMPLES = [128,0,0,0.0,0.0,None,None,0,0,0,0]
NEUTRAL_SAMPLE = NEUTRAL_SAMPLES[PA_SAMPLE_FORM]

BYTE_COUNTS=[1,2,2,4,4,1,1,4,4,4,4]
BYTE_COUNT=BYTE_COUNTS[PA_SAMPLE_FORM]

PA_BASERATES=[44100,48000,96000,192000]
PA_BASERATE=PA_BASERATES[1]

class struct_pa_sample_spec(ctypes.Structure):
    __slots__ = ['format','rate','channels']
struct_pa_sample_spec._fields_ = [
	('format', ctypes.c_int),
	('rate', ctypes.c_uint32),
	('channels', ctypes.c_uint8)]

class Audi():
	def __init__(self,name:str,rate:int=PA_BASERATE,form:int=PA_SAMPLE_FORM,realtime:bool=False):
		print("""
		RIEDLER'S
		
		EasyAudi
		""")
		self.pa = ctypes.cdll.LoadLibrary('libpulse-simple.so.0')
		self.ss = struct_pa_sample_spec()
		self.ss.rate = rate
		self.ss.channels = 1
		self.ss.format = form
		self.error = ctypes.c_int(0)
		self._stop=False
		self.wg=WaveGen()
		self.wfs=[]
		self.isreal=realtime
		pa_sample_spec = struct_pa_sample_spec
		self.s = self.pa.pa_simple_new(None,"EasyAudi - "+name,PA_STREAM_PLAYBACK,None,'playback',ctypes.byref(self.ss),None,None,ctypes.byref(self.error))
	async def audioloop(self):
		try:
			startt=time.time()
			while True:
				#print("0.00\r",round(time.time()-startt,2),"\033[6G",self.wfs,sep='')
				#latency = self.pa.pa_simple_get_latency(self.s, self.error)
				#if latency == -1:
				#	raise Exception('Getting latency failed!')
				buf=await self.getchunk()
				if buf == '':
					return
				if self.pa.pa_simple_write(self.s, buf, len(buf), self.error):
					raise Exception('Could not play!')
				if self._stop:
					break
				#print(latency)
		finally:
			self.pa.pa_simple_free(self.s)
	def stop(self,wav=None):
		if wav==None:
			self._stop=True
		else:
			del self.wfs[self.wfs.index(wav)]
	async def getchunk(self):
		s=b""
		for x in range(256):
			sample=NEUTRAL_SAMPLE
			for wf in self.wfs:
				if wf.dur!=0 and wf.delay<=0:
					sample+=wf.construct()
				elif wf.delay>0:
					wf.delay-=1
				else:
					del self.wfs[self.wfs.index(wf)]
			s+=samp2bytes(int(sample))
		if not self.isreal:
			await asyncio.sleep(0)
		return s
	def add(self,waveform):
		self.wfs.append(waveform)
		return waveform
		#print("added",waveform)

def samp2bytes(samp:int,meth:int=PA_SAMPLE_FORM):
	if meth==0:
		return struct.pack("<B",samp)
	elif meth==1:
		return struct.pack("<h",samp)
	elif meth==2:
		return struct.pack(">h",samp)
	elif meth==3:
		return struct.pack("<f",samp)
	elif meth==4:
		return struct.pack(">f",samp)
	elif meth==7:
		if samp<-2147483648:
			samp=-2147483648
		elif samp>2147483647:
			samp=2147483647
		return struct.pack("<i",samp)
	elif meth==8:
		if samp<-2147483648:
			samp=-2147483648
		elif samp>2147483647:
			samp=2147483647
		return struct.pack(">i",samp)
	else:
		raise ValueError("Meth has an invalid Value: "+str(meth))

class WaveGen():
	def __init__(self):
		pass
	def sin(self,dur:float,freq:float=1,vol:float=0.5,init_delay:float=0):
		return Sine(dur,freq,vol,init_delay)
class WaveForm():
	typ="Empty Wave"
	def __init__(self,dur:float,freq:float,vol:float,init_delay:float):
		self.delay=init_delay*PA_BASERATE
		self.dur=dur*PA_BASERATE
		self.dur2=dur*PA_BASERATE
		self.freq=freq/PA_BASERATE
		self.vol=vol*BIGGEST_SAMPLE
	def construct(self):
		if self.delay>0:
			self.delay-=1
		self.dur-=1
		return self.magicfunc()
	def stop(self):
		self.dur=0
	def magicfunc(self):
		return 0
	def __str__(self):
		return "<"+self.typ+" Object [delay="+str(self.delay/PA_BASERATE)+",time2live="+str((self.dur)/PA_BASERATE)+",freq="+str(self.freq*PA_BASERATE)+",vol="+str(self.vol/BIGGEST_SAMPLE)+"]>"
class Sine(WaveForm):
	typ="Sine"
	def magicfunc(self):
		return math.sin((self.dur2-self.dur)*6.283*self.freq)*self.vol

def note(n:str):
	freq=440 #A4
	a=n[0].lower()
	try:
		m=n[2]
		if not m in ("b","#"):
			raise ValueError("Don't worry, it'll get catched by the except below.")
	except:
		m=None
		try:
			i=int(n[1:])
		except:
			i=4
	else:
		try:
			i=int(n[1:-1])
		except:
			i=4
	
	if a=="a":
		if m==None:
			pass
		elif m=="b":
			freq=415.305
		elif m=="#":
			freq=466.164
	elif a=="b" or a=="h":
		if m==None:
			freq=493.883
		elif m=="b":
			freq=466.164
		elif m=="#":
			freq=523.251
	elif a=="c":
		if m==None:
			freq=261.626
		elif m=="b":
			freq=246.942
		elif m=="#":
			freq=277.183
	elif a=="d":
		if m==None:
			freq=293.665
		elif m=="b":
			freq=277.183
		elif m=="#":
			freq=311.127
	elif a=="e":
		if m==None:
			freq=329.628
		elif m=="b":
			freq=311.127
		elif m=="#":
			freq=349.228
	elif a=="f":
		if m==None:
			freq=349.228
		elif m=="b":
			freq=329.628
		elif m=="#":
			freq=369.994
	elif a=="g":
		if m==None:
			freq=391.995
		elif m=="b":
			freq=369.994
		elif m=="#":
			freq=415.305
	
	i-=4
	if i>0:
		freq*=2**i
	if i<0:
		freq/=2**abs(i)
	
	
	
	return freq
