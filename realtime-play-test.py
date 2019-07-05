#!/usr/bin/python3.7
import easyaudi as ezaud
import asyncio, pynput, os
KEY=pynput.keyboard.Key

def doit(on,note):
	if on:
		return audi.add(audi.wg.sin(dur=-1,vol=0.2,freq=ezaud.note("D3b")))
	else:
		wavlist[key].stop()

def feeder(key:int,on:bool):
	if key==-1:
		pass
	elif key=='<':
		doit(on,"C3")
	elif key=='a':
		doit(on,"D3b")
	elif key=='y':
		if on:
			return audi.add(audi.wg.sin(dur=-1,vol=0.2,freq=ezaud.note("D3")))
		else:
			wavlist[key].stop()
	elif key=='s':
		if on:
			return audi.add(audi.wg.sin(dur=-1,vol=0.2,freq=ezaud.note("E3b")))
		else:
			wavlist[key].stop()
	elif key=='x':
		if on:
			return audi.add(audi.wg.sin(dur=-1,vol=0.2,freq=ezaud.note("E3")))
		else:
			wavlist[key].stop()
	elif key=='d':
		pass	#there is no Fb or E#.
	elif key==99:	#c
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("F3")))
	elif key==102:	#f
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("G3b")))
	elif key==118:	#v
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("G3")))
	elif key==103:	#g
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("G3#")))
	elif key==98:	#b
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("A3")))
	elif key==104:	#h
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("A3#")))
	elif key==110:	#n
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("B3")))
	elif key==106:	#j
		pass 	#there is no Cb or B#
	elif key==109:	#m
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("C4")))
	elif key==107:	#k
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("C4#")))
	elif key==44:	#,
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("D4")))
	elif key==108:	#l
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("D4#")))
	elif key==46:	#.
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("E4")))
	elif key==195:	#ä/ö/ü
		if key==182:
			pass #still no E# nor Fb.
		elif key==164:#ä
			return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("F4#")))
		elif key==188:#ü
			return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("C1")))
	elif key==45:	#-
		return audi.add(audi.wg.sin(dur=0.3,vol=0.2,freq=ezaud.note("F4")))
	elif key==KEY.esc:
		audi.stop()
	else:
		print("Unmapped Key detected:",key,end="\n\r")
	
def on_press(key):
	try:
		key=key.char
	except AttributeError:
		pass
	if not key in wavlist:
		wav=feeder(key,True)
		if wav.__class__==ezaud.Sine:
			wavlist[key]=wav
def on_release(key):
	try:
		key=key.char
	except:
		pass
	if key in wavlist:
		feeder(key,False)
		del wavlist[key]
def main():
	global audi, wavlist
	wavlist={}
	audi=ezaud.Audi("Test-Realtime",realtime=True)
	listener=pynput.keyboard.Listener(on_press=on_press,on_release=on_release,suppress=False)
	listener.start()
	try:
		asyncio.run(audi.audioloop())
	finally:
		listener.stop()
if __name__ == '__main__':
	try:
		os.system("stty -echo")
		os.system("setterm -cursor off")
		main()
	finally:
		os.system("stty echo")
		os.system("setterm -cursor on")
