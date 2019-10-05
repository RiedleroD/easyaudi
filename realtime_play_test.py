#!/usr/bin/python3.7
import easyaudi as ezaud
import asyncio, pygame

class RealTimePlayer():
	def __init__(self):
		self.wavlist={}
		self.audi=ezaud.Audi("Test-Realtime",realtime=True)
		self.screen=pygame.set_mode((720,720))
	def doit(self,note,on):
		if on and note not in self.wavlist:
			self.wavlist[note]=audi.add(audi.wg.sin(dur=-1,vol=0.2,freq=ezaud.note(note)))
		elif note in self.wavlist and not on:
			self.wavlist[note].stop()
			del self.wavlist[note]
	async def keyEventListener(self):
		for event in pygame.events.get():
			if event.type==pygame.KEYDOWN:
				self.keyfunc(on=True,event.key)
			elif event.type==pygame.KEYUP:
				self.keyfunc(on=False,event.key)
			elif event.type==pygame.QUIT:
				quit()
	def keyfunc(self,on,key):
		if key==pygame.K_a:
			self.doit(on,)

def main():
	rtp=RealTimePlayer()
	try:
		asyncio.run(audi.audioloop())
	finally:
		audi.stop()

if __name__=="__main__":
	main()
