import httpx
import asyncio

API_URL = "http://localhost:8000/api/ask"   # change if needed

async def send_req(n):
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            API_URL,
            json={"question": f"Load test question {n}"}
        )
        print(f"[{n}] Response:", resp.json())

async def main():
    NUM_REQUESTS = 20   # how many parallel requests you want
    tasks = [send_req(i) for i in range(NUM_REQUESTS)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
