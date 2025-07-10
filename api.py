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
                        "location": f"{city}, {country}",
                        "timezone": data['data']['meta']['timezone']
                    }
                else:
                    return {"error": "API returned invalid data."}
            else:
                return {"error": "API request failed: " + str(response.status)}

async def get_location_info(latitude: float, longitude: float) -> dict:
    """
    Convert latitutde/longitude to city, countri info
    Uses OpenStreetMap Nominatim (free service)
    """

    url = "https://nominatim.openstreetmap.org/reverse"

    params = { 
        "lat": latitude,
        "lon": longitude,
        "format": "json",
        "addressdetails": 1,
        "accept-language": "en"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status ==200:
                    data = await response.json()

                    #Extract city and country from the response
                    address = data.get("address",{})

                    city = (address.get("city") or address.get("town") or address.get("village") or "Unknown City")
                    country = address.get("country_code", "Unknown Country")
                    
                    return {
                        "city": city,
                        "country": country,
                        "success": True
                    }
                else:
                    return {"success": False, "error": "API request failed: " + str(response.status)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    
                    
    