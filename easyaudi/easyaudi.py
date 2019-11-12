#!/usr/bin/python3
import ctypes,sys,random, math, asyncio, time, struct

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
	__doc__="structure for pulsaudio output"
	__slots__ = ['format','rate','channels']
	_fields_ = [
	('format', ctypes.c_int),
	('rate', ctypes.c_uint32),
	('channels', ctypes.c_uint8)]

class Effect():
	typ="Empty"
	__doc__="Base class for Effects"
	def beforemagic(self,wavedict:dict)->dict:
		"""Takes the object dict from the WaveForm it's affecting and returns a dict with values to update"""
		return {}
	def aftermagic(self,sample:float)->float:
		"""Takes a sample and returns it"""
		return sample

class EffectGen():
	class SlowPass(Effect):
		typ="SlowPass"
		__doc__="Emulates a speaker that is slow at moving its membrane."
		def __init__(self,speed:float):
			"""Arguments:
	speed	->	The speed at which the emulated speaker can move (from 0-1 where 0 is no movement and 1 is normal speed)
Attributes:
	speed	->	The speed at which the emulated speaker can move (from 0-"""+str(PA_BASERATE)+""" where 0 is no movement and """+str(PA_BASERATE)+""" is normal speed)
	prevsamp->	The previously filtered sample"""
			self.speed=speed*PA_BASERATE
			self.prevsamp=0
		def aftermagic(self,sample:float)->float:
			"""Takes the sample and outputs the filtered one."""
			if sample>self.sample+self.speed:
				result=self.sample+self.speed
			elif sample<self.sample-self.speed:
				result=self.sample-self.speed
			else:
				result=sample
			self.sample=result
			return result

class WaveForm():
	typ="Empty"
	__doc__="Base class for waveforms"
	def __init__(self,dur:float,freq:float=None,vol:float=0.25,delay:float=0,att:float=0.01,fade:float=0.01,note:str=None,**kwargs):
		"""Initiates the waveform.

Argument explanations:
	DISCLAIMER:
		If a Waveform not packaged with easyaudi has a issue with any of these, please contact the creator of the waveform.
		Except for the delay, every other argument has to be properly supported by the waveform.
	freq	->	Frequency of the wave in Hz
	dur		->	Duration of the wave in seconds. Starts after delay.
	delay	->	Delay between the waveform being added to the audio loop and it actually producing sound in seconds.
	att		->	Attack (volume sweep from 0 to vol) in seconds.
	vol		->	Volume of the wave, where 0-1 is 0%-100%. (it's possible to go over 100%, it just sounds horrible)
	fade	->	Fadeout of the wave in seconds. The wave will fade out for the selected amount of seconds after it ended."""
		if freq==None:
			if note==None:
				raise ValueError("You can't have a Wave without frequncy. Please set either the note or freq attribute.")
			else:
				freq=Note(note)
		self.freq=freq
		self.delay=delay*PA_BASERATE	#The remaining delay
		self._dur=dur*PA_BASERATE		#The remaining duration
		self._dur2=self._dur			#[CONSTANT]	initial duration
		self.dur=self._dur2-self._dur	#The already played duration
		self.freq=freq/PA_BASERATE		#The frequency in Hz
		self._vol=vol*BIGGEST_SAMPLE	#The base volume
		self.vol=self._vol				#The true volume (affected by attack, fadeout and, after they got implemented, effects)
		self._fade=fade*PA_BASERATE		#The remaining fade
		self._fade2=self._fade			#[CONSTANT]	initial fadeout duration
		self.progress=self.get_progress()
		self._att=att*PA_BASERATE		#The remaining attack
		self.att=self.progress/self._att#The attack in percent
		self.fade=self._fade/self._fade2#The fade in percent
		self.__dict__.update(kwargs)
	def alive(self)->bool:
		"""Checks if the Wave hasn't ended yet"""
		if self.delay>0 or self._dur>0 or self._fade>0:
			return True
		else:
			return False
	def time_left(self)->float:
		"""returns time in seconds that the Wave takes to complete"""
		return self.delay/PA_BASERATE+self._dur/PA_BASERATE+self.fade/PA_BASERATE
	def construct(self)->float:
		"""returns the next sample"""
		self.progress=self.get_progress()
		if self.delay>0:
			self.delay-=1
			return 0
		elif self._dur>0:
			self._dur-=1
		elif self._fade>0:
			self._fade-=1
		else:
			return 0
		if self._att!=0:
			self.att=(self.progress/self._att)
			if self.att>1:
				self.att=1
			self.vol=self._vol*self.att
		else:
			self.vol=self._vol
		if self._dur==0:
			self.fade=self._fade/self._fade2
			self.vol*=self.fade
		return self.magicfunc()
	def stop(self):
		"""Ends the wave"""
		self._dur=0
		self._fade=0
		self.delay=0
	def magicfunc(self)->float:
		"""Returns the current sample, even when the wave ended.
Returns 0, since it's a null wave."""
		return 0
	def get_progress(self):
		return (self._fade2-self._fade+self._dur2-self._dur)
	def __iter__(self):
		return self
	def	__next__(self)->float:
		if self.alive():
			return self.construct()
		else:
			raise StopIteration()
	def __str__(self)->str:
		"""Returns a string representation of this object"""
		return "<"+self.typ+" Wave [dur="+str(self._dur2/PA_BASERATE)+",delay="+str(self._delay/PA_BASERATE)+",time2live="+str(self.progress/PA_BASERATE)+",freq="+str(self.freq*PA_BASERATE)+",vol="+str(self._vol/BIGGEST_SAMPLE)+"]>"

class WaveGen():
	class Sine(WaveForm):
		typ="Sine"
		__doc__="A sine wave"
		def magicfunc(self)->float:
			"""Returns the current sample, even when the wave ended"""
			return math.sin(self.progress*math.pi*2*self.freq)*self.vol
	class Square(WaveForm):
		typ="Square"
		__doc__="A square wave"
		duty=50
		def magicfunc(self)->float:
			"""Returns the current sample, even when the wave ended"""
			x=math.sin(self.progress*math.pi*2*self.freq)
			if x>(self.duty-50)/100:
				return self.vol
			else:
				return -self.vol
	class SuperSynth(Square):
		typ="Square"
		__doc__="A square wave"
		duty=50
		def magicfunc(self)->float:
			"""Returns the current sample, even when the wave ended"""
			x=math.sin(self.progress*math.pi*2*self.freq)
			self.duty+=0.01
			self.duty%=100
			if x>(self.duty-50)/100:
				return self.vol
			else:
				return -self.vol
	class Saw(WaveForm):
		typ="Saw"
		__doc__="A saw wave"
		def magicfunc(self)->float:
			"""Returns the current sample, even when the wave ended"""
			return ((self.progress*2*self.freq+1)%2-1)*self.vol
	class Triangle(WaveForm):
		typ="Sine"
		__doc__="A sine wave"
		def magicfunc(self)->float:
			"""Returns the current sample, even when the wave ended"""
			return math.asin(math.sin(self.progress*math.pi*2*self.freq))*self.vol
	__doc__="Collection class of waveforms"
	def __init__(self):
		pass

class Audi():
	__doc__="Main audio managing class."
	def __init__(self,name:str,rate:int=PA_BASERATE,form:int=PA_SAMPLE_FORM,realtime:bool=False,effects:[Effect]=[]):
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
		self.eg=EffectGen()
		self.wfs=[]
		self.effects={}
		self.effectn
		counter=0
		for effect in effects:
			self.effects[counter]=effect
			counter+=1
		del counter
		self.isreal=realtime
		pa_sample_spec = struct_pa_sample_spec
		self.s = self.pa.pa_simple_new(None,"EasyAudi - "+name,PA_STREAM_PLAYBACK,None,'playback',ctypes.byref(self.ss),None,None,ctypes.byref(self.error))
	async def audioloop(self):
		"""starts the audio loop"""
		try:
			startt=time.time()
			while True:
				#print("0.00\r",round(time.time()-startt,2),"\033[6G",self.wfs,sep='')
				#latency = self.pa.pa_simple_get_latency(self.s, self.error)
				#if latency == -1:
				#	raise Exception('Getting latency failed!')
				buf=self.getchunk()
				for effect in self.effects:
					buf=effect.aftermagic(buf)
				if not self.isreal:
					await asyncio.sleep(0)
				if buf == '':
					return
				if self.pa.pa_simple_write(self.s, buf, len(buf), self.error):
					raise Exception('Could not play!')
				if self._stop:
					break
				#print(latency)
		finally:
			self.pa.pa_simple_free(self.s)
	def add_effect(self,effect:Effect,place:int=-1)->int:
		"""Adds an effect to the effect chain.
Arguments:
	place	->	the id to place the effect. -1 means it gets automatically generated with the id() function"""
		if place<0:
			i=id(effect)
			self.effects[i]=effect
			return i
		else:
			self.effects[place]=effect
	def del_effect(self,id:int)->None:
		del self.effects[id]
	def get_effect(self,id:int)->Effect:
		return self.effects[id]
	def stop(self,wav:WaveForm=None):
		"""Stops the audio loop or a running wave."""
		if wav==None:
			self._stop=True
		else:
			del self.wfs[self.wfs.index(wav)]
	def getchunk(self)->bytes:
		"""Returns a chunk of 256 samples"""
		s=b""
		for x in range(256):
			sample=NEUTRAL_SAMPLE
			for wf in self.wfs:
				if wf.alive():
					sample+=wf.construct()
				else:
					del self.wfs[self.wfs.index(wf)]
			s+=samp2bytes(int(sample))
		return s
	def add(self,*waveforms:(WaveForm))->tuple:
		"""Adds several waveforms to the audio loop"""
		for wf in waveforms:
			self.wfs.append(wf)
	async def play(self,*waveforms:(WaveForm))->None:
		"""Adds several WaveForms and waits for them to finish"""
		longest=0
		for wf in waveforms:
			self.wfs.append(wf)
			x=wf.time_left()
			if x>longest:
				longest=x
		await asyncio.sleep(longest)

def samp2bytes(samp:int,meth:int=PA_SAMPLE_FORM)->bytes:
	"""Converts a sample to bytes"""
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

def Note(n:str)->float:
	"""Converts a note into a frequency.
Note Syntax:
<NOTE><OCTAVE><MODIFIER>
Examples: A4, A1b, A3#, C4B"""
	freq=440 #A4
	a=n[0].lower()
	try:
		m=n[2].lower()
		if not m in ("b","#"):
			raise ValueError("Don't worry, it'll get catched by the except below.")
	except (ValueError, IndexError):
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

if __name__=="__main__":
	import test_jingle as jingle
	jingle.main()
