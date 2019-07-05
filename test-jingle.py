#!/usr/bin/python3.7
import easyaudi as ezaud
import asyncio
async def amain(audi:ezaud.Audi):
	await asyncio.gather(feeder(audi),audi.audioloop())
async def feeder(audi:ezaud.Audi):
	s=asyncio.sleep
	await s(0.5)
	print("Playing...")
	for x in range(2):
		await audi.add(audi.wg.sin(dur=0.3,vol=0.5,freq=ezaud.note("A4b")))		#yes, you have to create a new object for every note.
		await s(0.3)
		await audi.add(audi.wg.sin(dur=0.1,vol=0.5,freq=ezaud.note("C4")))
		await s(0.1)
		await audi.add(audi.wg.sin(dur=0.3,vol=0.5,freq=ezaud.note("E4")))
		await s(0.3)
		await audi.add(audi.wg.sin(dur=0.1,vol=0.5,freq=ezaud.note("C4")))
		await s(0.1)
		await audi.add(audi.wg.sin(dur=0.3,vol=0.5,freq=ezaud.note("A4")))
		await s(0.3)
		await audi.add(audi.wg.sin(dur=0.1,vol=0.5,freq=ezaud.note("C4")))
		await s(0.1)
		await audi.add(audi.wg.sin(dur=0.3,vol=0.5,freq=ezaud.note("E4")))
		await s(0.3)
		await audi.add(audi.wg.sin(dur=0.1,vol=0.5,freq=ezaud.note("C4")))
		await s(0.1)
	await s(0.1)
	audi.stop()
def main():
	audi=ezaud.Audi("Test")
	asyncio.run(amain(audi),debug=False)
if __name__ == '__main__':
	main()
