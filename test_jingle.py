#!/usr/bin/python3.7
import easyaudi as ezaud
import asyncio
async def amain(audi:ezaud.Audi):
	await asyncio.gather(feeder(audi),audi.audioloop())
async def feeder(audi:ezaud.Audi):
	s=asyncio.sleep
	print("Some sample from Super Mario Land 2")
	audi.add_mult(
		audi.wg.Square(dur=0.03,vol=0.5,freq=ezaud.note("E4")),
		audi.wg.Square(delay=0.03,dur=0.05,vol=0.5,freq=ezaud.note("H4")))
	await s(0.1)
	print("Some melody with attack and Sines")
	audi.add(audi.wg.Sine(dur=1,att=0.7,vol=1,freq=ezaud.note("A4b")))		#yes, you have to create a new object for every note.
	await s(1)
	audi.add(audi.wg.Sine(dur=0.1,vol=0.5,freq=ezaud.note("C4")))
	await s(0.1)
	audi.add(audi.wg.Sine(dur=0.3,vol=0.25,freq=ezaud.note("E4")))
	await s(0.3)
	audi.add(audi.wg.Sine(dur=0.1,vol=0.125,freq=ezaud.note("C4")))
	await s(0.1)
	audi.add(audi.wg.Sine(dur=0.3,vol=0.0625,freq=ezaud.note("A4")))
	await s(0.3)
	audi.add(audi.wg.Sine(dur=0.1,vol=0.125,freq=ezaud.note("C4")))
	await s(0.1)
	audi.add(audi.wg.Sine(dur=0.3,vol=0.25,freq=ezaud.note("E4")))
	await s(0.3)
	audi.add(audi.wg.Sine(dur=0.1,vol=0.5,freq=ezaud.note("C4")))
	await s(0.4)
	print("Some melody with Squares at the same time")
	audi.add(audi.wg.Square(dur=0.3,vol=0.3,freq=ezaud.note("C4")))
	await s(0.1)
	audi.add(audi.wg.Square(dur=0.3,fade=0.1,vol=0.3,freq=ezaud.note("D4")))
	await s(0.1)
	audi.add(audi.wg.Square(dur=0.3,fade=0.7,vol=0.3,freq=ezaud.note("A4")))
	await s(1.2)
	print("All four instruments")
	audi.add(audi.wg.Saw(dur=0.2,vol=0.3,freq=ezaud.note("A4")))
	await s(0.2)
	audi.add(audi.wg.Square(dur=0.2,vol=0.3,freq=ezaud.note("A4")))
	await s(0.2)
	audi.add(audi.wg.Sine(dur=0.2,vol=0.3,freq=ezaud.note("A4")))
	await s(0.2)
	audi.add(audi.wg.Triangle(dur=0.2,vol=0.3,freq=ezaud.note("A4")))
	await s(0.5)	#I recommend some extra time between the last note finishing and the stream closing. It's still python, so speed isn't what you get here.
	audi.stop()
	print("Stopped")
def main():
	audi=ezaud.Audi("Test")
	asyncio.run(amain(audi),debug=False)
if __name__ == '__main__':
	main()
