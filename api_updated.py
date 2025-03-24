from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import collect_highres_image_urls

app = FastAPI()

class ImageRequest(BaseModel):
    keyword: str
    max_images: int = 10

@app.post("/get_images")
def get_images(req: ImageRequest):
    try:
        image_urls = collect_highres_image_urls(req.keyword, req.max_images)
        return {"images": image_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scrape")
def scrape(keyword: str, max_images: int = 10):
    try:
        image_urls = collect_highres_image_urls(keyword, max_images)
        return {"images": image_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
