from fastapi import APIRouter, BackgroundTasks
import asyncio
from app.services.scraper import scrape_recipe
from app.services.parser import parse_recipe

router = APIRouter()

async def process_single_recipe(url: str):
    scraped_data = await scrape_recipe(url)
    await parse_recipe(scraped_data)
    return {"url": url, "status": "completed"}

async def process_bulk_recipes(urls: list[str]):
    tasks = [process_single_recipe(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

@router.post("/recipes/bulk/async")
async def bulk_import_async(data: dict, background_tasks: BackgroundTasks):
    urls = data.get("urls", [])
    background_tasks.add_task(process_bulk_recipes, urls)
    return {"message": "Bulk recipe import started", "count": len(urls)}
