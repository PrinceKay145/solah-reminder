import requests
import asyncio
import aiohttp
from datetime import datetime

async def get_prayer_times(city: str, country: str, method: int = 2, date: str = None) -> dict:
    date_str = date if date else datetime.now().strftime("%d-%m-%Y")
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.aladhan.com/v1/timingsByCity",
            params={
                "city": city,
                "country": country,
                "method": method,
                "date": date_str
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                if data['code'] == 200:
                    return{
                        "date": data['data']['date']['readable'],
                        "timings": data['data']['timings'],
                        "location": f"{city}, {country}"
                    }
                else:
                    return {"error": "API returned invalid data."}
            else:
                return {"error": "API request failed: " + str(response.status)}