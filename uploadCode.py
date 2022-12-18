import sync_file as s
import asyncio

async def main():
    syncer = s.WebSync()
    files = ['main.py','core.py','clean_record.py','parse.py','tester.py','writer.py']
    for file in files:
        await syncer.pushToTarget(file)
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())