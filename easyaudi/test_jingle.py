#!/usr/bin/python3
import easyaudi as ezaud
import asyncio
async def amain(audi:ezaud.Audi):
	await asyncio.gather(feeder(audi),audi.audioloop())
async def feeder(audi:ezaud.Audi):
	s=asyncio.sleep
	print("Some sample from Super Mario Land 2")
	await audi.play(
		audi.wg.Square(dur=0.03,vol=0.5,note="E4"),
		audi.wg.Square(delay=0.03,dur=0.05,vol=0.5,note="H4"))
	print("Some melody with attack and Sines")
	await audi.play(
		audi.wg.Sine(dur=1,att=0.7,vol=1,note="A4b"),
		audi.wg.Sine(dur=0.1,delay=1,vol=0.5,note="C4"),
		audi.wg.Sine(dur=0.3,delay=1.1,vol=0.25,note="E4"),
		audi.wg.Sine(dur=0.1,delay=1.4,vol=0.125,note="C4"),
		audi.wg.Sine(dur=0.3,delay=1.5,vol=0.0625,note="A4"),
		audi.wg.Sine(dur=0.1,delay=1.8,vol=0.125,note="C4"),
		audi.wg.Sine(dur=0.3,delay=1.9,vol=0.25,note="E4"),
		audi.wg.Sine(dur=0.1,delay=2.2,fade=0.7,vol=0.5,note="C4"))
	await s(1)
	print("Some melody with Squares")
	await audi.play(
		audi.wg.Square(dur=0.3,vol=0.3,note="C4"),
		audi.wg.Square(dur=0.3,delay=0.1,vol=0.3,note="D4"),
		audi.wg.Square(dur=0.3,delay=0.2,vol=0.3,note="A4"))
	print("Some melody with Squares now with LowPass Filter")
	lp=audi.add_effect(audi.eg.LowPass(10))
	await audi.play(
		audi.wg.Square(dur=0.3,vol=0.3,note="C4"),
		audi.wg.Square(dur=0.3,delay=0.1,vol=0.3,note="D4"),
		audi.wg.Square(dur=0.3,delay=0.2,vol=0.3,note="A4"))
	audi.del_effect(lp)
	print("Some melody with Squares now with HighPass Filter")
	hp=audi.add_effect(audi.eg.HighPass(10))
	await audi.play(
		audi.wg.Square(dur=0.3,vol=0.3,note="C4"),
		audi.wg.Square(dur=0.3,delay=0.1,vol=0.3,note="D4"),
		audi.wg.Square(dur=0.3,delay=0.2,vol=0.3,note="A4"))
	audi.del_effect(hp)
	print("Some melody with Squares which differ in duty at the same time")
	await audi.play(
		audi.wg.Square(dur=0.3,vol=0.3,note="C4",duty=25),
		audi.wg.Square(dur=0.3,delay=0.1,vol=0.3,note="D4",duty=50),
		audi.wg.Square(dur=0.3,delay=0.2,vol=0.3,note="A4",duty=75))
	await s(0.5)
	print("All five instruments:")
	print("\tSaw")
	await audi.play(audi.wg.Saw(dur=0.2,vol=0.3,note="A4"))
	print("\tSquare")
	await audi.play(audi.wg.Square(dur=0.2,vol=0.3,note="A4"))
	print("\tSine")
	await audi.play(audi.wg.Sine(dur=0.2,vol=0.3,note="A4"))
	print("\tTriangle")
	await audi.play(audi.wg.Triangle(dur=0.2,vol=0.3,note="A4"))
	print("\tSuperSynth")
	await audi.play(audi.wg.SuperSynth(dur=0.2,vol=0.3,note="A4"))
	await s(0.2)	#I recommend some extra time between the last note finishing and the stream closing. It's still python, so speed isn't what you get here.
	audi.stop()
def main():
	audi=ezaud.Audi("Test")
	asyncio.run(amain(audi),debug=False)
if __name__ == '__main__':
	main()
