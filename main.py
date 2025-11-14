import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from database import create_document, get_documents
from schemas import Inquiry

app = FastAPI(title="Choppinzskys API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# -----------------------------
# Choppinzskys API
# -----------------------------

class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    image: str
    category: str

class MenuCategory(BaseModel):
    key: str
    title: str
    items: List[MenuItem]

# Static menu data (images use royalty-free placeholders/Unsplash)
MENU_DATA: List[MenuCategory] = [
    MenuCategory(
        key="african",
        title="African Delights",
        items=[
            MenuItem(
                id="puff-puff",
                name="Puff Puff",
                description="Golden, fluffy bites lightly dusted with sugar.",
                image="https://images.unsplash.com/photo-1617191518205-29c76d7d6672?q=80&w=1400&auto=format&fit=crop",
                category="African Delights",
            ),
            MenuItem(
                id="akara",
                name="Akara",
                description="Crisp bean fritters with a soft, fragrant center.",
                image="https://images.unsplash.com/photo-1604908553982-57e1bdf4cf0f?q=80&w=1400&auto=format&fit=crop",
                category="African Delights",
            ),
            MenuItem(
                id="fried-yam",
                name="Fried Yam",
                description="Hearty yam chips, golden and perfectly seasoned.",
                image="https://images.unsplash.com/photo-1547592180-85f173990554?q=80&w=1400&auto=format&fit=crop",
                category="African Delights",
            ),
            MenuItem(
                id="plantain",
                name="Plantain",
                description="Sweet ripe plantain slices, caramelized to perfection.",
                image="https://images.unsplash.com/photo-1543332164-6e82f355badc?q=80&w=1400&auto=format&fit=crop",
                category="African Delights",
            ),
        ],
    ),
    MenuCategory(
        key="pastries",
        title="Savory Pastries & Rolls",
        items=[
            MenuItem(
                id="samosa",
                name="Samosa",
                description="Crisp pastry stuffed with spiced vegetables or meat.",
                image="https://images.unsplash.com/photo-1683021712492-27cf3ad5f222?q=80&w=1400&auto=format&fit=crop",
                category="Savory Pastries & Rolls",
            ),
            MenuItem(
                id="spring-rolls",
                name="Spring Rolls",
                description="Delicate rolls with a vibrant vegetable filling.",
                image="https://images.unsplash.com/photo-1512058564366-18510be2db19?q=80&w=1400&auto=format&fit=crop",
                category="Savory Pastries & Rolls",
            ),
            MenuItem(
                id="meat-pie",
                name="Meat Pie",
                description="Buttery pastry with a rich, savory filling.",
                image="https://images.unsplash.com/photo-1541781286675-7b3c9817e3d5?q=80&w=1400&auto=format&fit=crop",
                category="Savory Pastries & Rolls",
            ),
            MenuItem(
                id="fish-roll",
                name="Fish Roll",
                description="Flaky pastry embracing spiced fish.",
                image="https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?q=80&w=1400&auto=format&fit=crop",
                category="Savory Pastries & Rolls",
            ),
            MenuItem(
                id="chicken-roll",
                name="Chicken Roll",
                description="Tender chicken seasoned and wrapped in golden pastry.",
                image="https://images.unsplash.com/photo-1543336661-08fc734e01d2?q=80&w=1400&auto=format&fit=crop",
                category="Savory Pastries & Rolls",
            ),
        ],
    ),
    MenuCategory(
        key="global",
        title="Global Favourites",
        items=[
            MenuItem(
                id="potato-swirls",
                name="Potato Swirls",
                description="Fun, crispy swirls with a fluffy potato center.",
                image="https://images.unsplash.com/photo-1551183053-bf91a1d81141?q=80&w=1400&auto=format&fit=crop",
                category="Global Favourites",
            ),
        ],
    ),
]

@app.get("/api/menu", response_model=List[MenuCategory])
async def get_menu() -> List[MenuCategory]:
    return MENU_DATA

@app.post("/api/inquiries")
async def create_inquiry(inquiry: Inquiry) -> Dict[str, Any]:
    try:
        inserted_id = create_document("inquiry", inquiry)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inquiries")
async def list_inquiries(limit: int = 10):
    try:
        docs = get_documents("inquiry", limit=limit)
        # Convert ObjectId to string for JSON serialisation
        def normalize(doc):
            d = {k: v for k, v in doc.items() if k != "_id"}
            d["id"] = str(doc.get("_id"))
            return d
        return [normalize(doc) for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
