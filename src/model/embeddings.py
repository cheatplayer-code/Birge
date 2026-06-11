"""
Embedding utilities with deterministic fallback.

If embeddings are missing, uses category/tag overlap.
Provides deterministic 12-dimensional demo vectors from category/tags.
"""

from typing import List, Dict, Any, Optional
import math


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Returns a value between -1 and 1.
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)


# Deterministic embedding basis vectors for categories
# 12-dimensional vectors for demo purposes
CATEGORY_EMBEDDINGS: Dict[str, List[float]] = {
    "electronics": [0.8, 0.2, 0.1, 0.3, 0.1, 0.2, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1],
    "home": [0.1, 0.7, 0.2, 0.1, 0.3, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1],
    "fashion": [0.2, 0.1, 0.8, 0.2, 0.1, 0.3, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1],
    "sports": [0.1, 0.2, 0.1, 0.8, 0.2, 0.1, 0.3, 0.1, 0.1, 0.2, 0.1, 0.1],
    "books": [0.1, 0.1, 0.2, 0.1, 0.8, 0.2, 0.1, 0.3, 0.1, 0.1, 0.2, 0.1],
    "toys": [0.2, 0.1, 0.1, 0.2, 0.1, 0.8, 0.2, 0.1, 0.3, 0.1, 0.1, 0.2],
    "food": [0.1, 0.2, 0.1, 0.1, 0.2, 0.1, 0.8, 0.2, 0.1, 0.3, 0.1, 0.1],
    "beauty": [0.1, 0.1, 0.2, 0.1, 0.1, 0.2, 0.1, 0.8, 0.2, 0.1, 0.3, 0.1],
    "auto": [0.2, 0.1, 0.1, 0.2, 0.1, 0.1, 0.2, 0.1, 0.8, 0.2, 0.1, 0.3],
    "garden": [0.1, 0.3, 0.1, 0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.8, 0.2, 0.1],
}

# Tag-specific adjustments to category embeddings
TAG_ADJUSTMENTS: Dict[str, List[float]] = {
    "smartphone": [0.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "laptop": [0.2, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "headphones": [0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "camera": [0.2, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "furniture": [0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0],
    "decor": [0.0, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "kitchen": [0.0, 0.2, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "clothing": [0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0],
    "shoes": [0.0, 0.0, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "fitness": [0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0],
    "football": [0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "novel": [0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "science": [0.1, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
}


def get_deterministic_embedding(category: str, tags: Optional[List[str]] = None) -> List[float]:
    """
    Generate a deterministic 12-dimensional embedding from category and tags.
    
    This is used as a fallback when no real embeddings are available.
    The embedding is computed deterministically from category and tag strings.
    
    Returns a 12-dimensional vector.
    """
    # Start with category base vector
    category_lower = category.lower().strip()
    base_vector = CATEGORY_EMBEDDINGS.get(category_lower, [0.5] * 12).copy()
    
    # Add tag adjustments
    if tags:
        for tag in tags:
            tag_lower = tag.lower().strip()
            adjustment = TAG_ADJUSTMENTS.get(tag_lower, [0.05] * 12)
            for i in range(12):
                base_vector[i] += adjustment[i]
    
    # Normalize the vector
    norm = math.sqrt(sum(v * v for v in base_vector))
    if norm > 0:
        base_vector = [v / norm for v in base_vector]
    
    return base_vector


def get_demo_data() -> Dict[str, Any]:
    """
    Get synthetic demo data for testing without Supabase.
    
    Returns demo users, products, deals, and events.
    All data is clearly labeled as synthetic.
    All IDs are valid UUID strings compatible with Supabase schema.
    """
    # Demo users with different profiles (valid UUIDs)
    users = {
        "00000000-0000-0000-0000-000000000001": {
            "id": "00000000-0000-0000-0000-000000000001",
            "budget_tier": "mid",
            "city": "Алматы",
            "interests": ["electronics", "home"],
            "interest_weights": {"electronics": 0.6, "home": 0.4},
            "created_at": "2024-01-15T10:00:00Z"
        },
        "00000000-0000-0000-0000-000000000002": {
            "id": "00000000-0000-0000-0000-000000000002",
            "budget_tier": "low",
            "city": "Астана",
            "interests": ["fashion", "beauty"],
            "interest_weights": {"fashion": 0.7, "beauty": 0.5},
            "created_at": "2024-02-20T14:30:00Z"
        },
        "00000000-0000-0000-0000-000000000003": {
            "id": "00000000-0000-0000-0000-000000000003",
            "budget_tier": "high",
            "city": "Алматы",
            "interests": ["electronics", "sports", "auto"],
            "interest_weights": {"electronics": 0.8, "sports": 0.6, "auto": 0.5},
            "created_at": "2024-03-10T09:15:00Z"
        }
    }
    
    # Demo products (25 items) with valid UUIDs
    products = {}
    product_data = [
        ("10000000-0000-0000-0000-000000000001", "electronics", "Беспроводные наушники Sony", "Sony сымсыз құлаққаптары", ["smartphone", "audio"], 25200, 17900),
        ("10000000-0000-0000-0000-000000000002", "electronics", "Смартфон Xiaomi Redmi", "Xiaomi Redmi смартфоны", ["smartphone", "android"], 89900, 72000),
        ("10000000-0000-0000-0000-000000000003", "electronics", "Ноутбук ASUS", "ASUS ноутбугі", ["laptop", "work"], 285000, 245000),
        ("10000000-0000-0000-0000-000000000004", "home", "Набор посуды", "Ыдыс жиынтығы", ["kitchen", "cook"], 18500, 12900),
        ("10000000-0000-0000-0000-000000000005", "home", "Увлажнитель воздуха", "Ауа ылғалдандырғышы", ["decor", "health"], 15600, 9900),
        ("10000000-0000-0000-0000-000000000006", "home", "Кофемашина", "Кофе машинасы", ["kitchen", "appliance"], 65000, 52000),
        ("10000000-0000-0000-0000-000000000007", "fashion", "Кроссовки Nike", "Nike кроссовкалары", ["shoes", "sport"], 45000, 35000),
        ("10000000-0000-0000-0000-000000000008", "fashion", "Куртка зимняя", "Қысқы куртка", ["clothing", "warm"], 28000, 19900),
        ("10000000-0000-0000-0000-000000000009", "fashion", "Джинсы Levi's", "Levi's джинсысы", ["clothing", "casual"], 32000, 24000),
        ("10000000-0000-0000-0000-000000000010", "sports", "Велосипед горный", "Тау велосипеді", ["fitness", "outdoor"], 85000, 68000),
        ("10000000-0000-0000-0000-000000000011", "sports", "Гантели набор", "Гантель жиынтығы", ["fitness", "home"], 12500, 8900),
        ("10000000-0000-0000-0000-000000000012", "sports", "Футбольный мяч", "Футбол добы", ["football", "outdoor"], 8500, 5900),
        ("10000000-0000-0000-0000-000000000013", "beauty", "Набор косметики", "Косметика жиынтығы", ["skincare", "gift"], 15800, 11200),
        ("10000000-0000-0000-0000-000000000014", "beauty", "Фен профессиональный", "Кәсіби фен", ["haircare", "appliance"], 22000, 16500),
        ("10000000-0000-0000-0000-000000000015", "books", "Книга 'Путь'", "'Жол' кітабы", ["novel", "bestseller"], 4500, 3200),
        ("10000000-0000-0000-0000-000000000016", "books", "Энциклопедия", "Энциклопедия", ["science", "education"], 8900, 6500),
        ("10000000-0000-0000-0000-000000000017", "toys", "Конструктор LEGO", "LEGO конструкторы", ["building", "kids"], 18900, 14500),
        ("10000000-0000-0000-0000-000000000018", "toys", "Настольная игра", "Үстел ойыны", ["family", "fun"], 12000, 8500),
        ("10000000-0000-0000-0000-000000000019", "food", "Набор специй", "Дәмдеуіштер жиынтығы", ["cook", "organic"], 3500, 2400),
        ("10000000-0000-0000-0000-000000000020", "food", "Чай премиум", "Премиум шай", ["drink", "gift"], 5600, 3900),
        ("10000000-0000-0000-0000-000000000021", "auto", "Автопылесос", "Автошаңсорғыш", ["car", "clean"], 12500, 8900),
        ("10000000-0000-0000-0000-000000000022", "auto", "Видеорегистратор", "Бейнетіркегіш", ["car", "safety"], 18500, 13900),
        ("10000000-0000-0000-0000-000000000023", "garden", "Садовый инструмент", "Бау құралы", ["outdoor", "tool"], 9500, 6800),
        ("10000000-0000-0000-0000-000000000024", "garden", "Семена овощей", "Көкөніс тұқымдары", ["garden", "organic"], 2500, 1800),
        ("10000000-0000-0000-0000-000000000025", "electronics", "Камера GoPro", "GoPro камерасы", ["camera", "action"], 145000, 125000),
    ]
    
    for prod_id, category, name_ru, name_kk, tags, retail, group in product_data:
        embedding = get_deterministic_embedding(category, tags)
        products[prod_id] = {
            "id": prod_id,
            "name_ru": name_ru,
            "name_kk": name_kk,
            "category": category,
            "tags": tags,
            "retail_price_kzt": retail,
            "group_price_kzt": group,
            "image_url": f"https://example.com/images/{prod_id}.jpg",
            "embedding": embedding
        }
    
    # Demo deals (8 active deals) with valid UUIDs
    # Main demo deal at 14/20 participants
    from datetime import datetime, timedelta
    now = datetime.now()
    
    deals = [
        {
            "id": "20000000-0000-0000-0000-000000000001",
            "product_id": "10000000-0000-0000-0000-000000000001",
            "city": "Алматы",
            "current_participants": 14,  # Main demo deal
            "target_participants": 20,
            "tiers": [{"min_participants": 10, "discount": 0.15}, {"min_participants": 20, "discount": 0.25}],
            "deadline": (now + timedelta(days=3)).isoformat() + "Z",
            "status": "active",
            "created_at": (now - timedelta(days=5)).isoformat() + "Z"
        },
        {
            "id": "20000000-0000-0000-0000-000000000002",
            "product_id": "10000000-0000-0000-0000-000000000002",
            "city": "Алматы",
            "current_participants": 8,
            "target_participants": 15,
            "tiers": [{"min_participants": 10, "discount": 0.12}, {"min_participants": 15, "discount": 0.20}],
            "deadline": (now + timedelta(days=5)).isoformat() + "Z",
            "status": "active",
            "created_at": (now - timedelta(days=2)).isoformat() + "Z"
        },
        {
            "id": "20000000-0000-0000-0000-000000000003",
            "product_id": "10000000-0000-0000-0000-000000000004",
            "city": "Астана",
            "current_participants": 18,
            "target_participants": 20,
            "tiers": [{"min_participants": 15, "discount": 0.20}, {"min_participants": 20, "discount": 0.30}],
            "deadline": (now + timedelta(days=1)).isoformat() + "Z",
            "status": "active",
            "created_at": (now - timedelta(days=7)).isoformat() + "Z"
        },
        {
            "id": "20000000-0000-0000-0000-000000000004",
            "product_id": "10000000-0000-0000-0000-000000000007",
            "city": "Алматы",
            "current_participants": 5,
            "target_participants": 12,
            "tiers": [{"min_participants": 8, "discount": 0.15}, {"min_participants": 12, "discount": 0.25}],
            "deadline": (now + timedelta(days=7)).isoformat() + "Z",
            "status": "active",
            "created_at": (now - timedelta(days=1)).isoformat() + "Z"
        },
        {
            "id": "20000000-0000-0000-0000-000000000005",
            "product_id": "10000000-0000-0000-0000-000000000010",
            "city": "Шымкент",
            "current_participants": 3,
            "target_participants": 10,
            "tiers": [{"min_participants": 5, "discount": 0.10}, {"min_participants": 10, "discount": 0.20}],
            "deadline": (now + timedelta(days=10)).isoformat() + "Z",
            "status": "active",
            "created_at": (now - timedelta(days=3)).isoformat() + "Z"
        },
        {
            "id": "20000000-0000-0000-0000-000000000006",
            "product_id": "10000000-0000-0000-0000-000000000011",
            "city": "Алматы",
            "current_participants": 22,
            "target_participants": 25,
            "tiers": [{"min_participants": 20, "discount": 0.18}, {"min_participants": 25, "discount": 0.28}],
            "deadline": (now + timedelta(days=2)).isoformat() + "Z",
            "status": "active",
            "created_at": (now - timedelta(days=10)).isoformat() + "Z"
        },
        {
            "id": "20000000-0000-0000-0000-000000000007",
            "product_id": "10000000-0000-0000-0000-000000000013",
            "city": "Астана",
            "current_participants": 6,
            "target_participants": 15,
            "tiers": [{"min_participants": 10, "discount": 0.15}, {"min_participants": 15, "discount": 0.25}],
            "deadline": (now + timedelta(days=4)).isoformat() + "Z",
            "status": "active",
            "created_at": (now - timedelta(days=2)).isoformat() + "Z"
        },
        {
            "id": "20000000-0000-0000-0000-000000000008",
            "product_id": "10000000-0000-0000-0000-000000000025",
            "city": "Алматы",
            "current_participants": 2,
            "target_participants": 8,
            "tiers": [{"min_participants": 5, "discount": 0.12}, {"min_participants": 8, "discount": 0.22}],
            "deadline": (now + timedelta(days=14)).isoformat() + "Z",
            "status": "active",
            "created_at": (now - timedelta(days=1)).isoformat() + "Z"
        }
    ]
    
    # Demo events with valid UUIDs
    events = [
        {"user_id": "00000000-0000-0000-0000-000000000001", "event_type": "view", "product_id": "10000000-0000-0000-0000-000000000001", "category": "electronics", "created_at": (now - timedelta(days=2)).isoformat() + "Z"},
        {"user_id": "00000000-0000-0000-0000-000000000001", "event_type": "click", "product_id": "10000000-0000-0000-0000-000000000001", "category": "electronics", "created_at": (now - timedelta(days=2)).isoformat() + "Z"},
        {"user_id": "00000000-0000-0000-0000-000000000001", "event_type": "click", "product_id": "10000000-0000-0000-0000-000000000002", "category": "electronics", "created_at": (now - timedelta(days=1)).isoformat() + "Z"},
        {"user_id": "00000000-0000-0000-0000-000000000001", "event_type": "view", "product_id": "10000000-0000-0000-0000-000000000004", "category": "home", "created_at": (now - timedelta(days=1)).isoformat() + "Z"},
        {"user_id": "00000000-0000-0000-0000-000000000002", "event_type": "view", "product_id": "10000000-0000-0000-0000-000000000007", "category": "fashion", "created_at": (now - timedelta(days=3)).isoformat() + "Z"},
        {"user_id": "00000000-0000-0000-0000-000000000002", "event_type": "click", "product_id": "10000000-0000-0000-0000-000000000007", "category": "fashion", "created_at": (now - timedelta(days=3)).isoformat() + "Z"},
        {"user_id": "00000000-0000-0000-0000-000000000002", "event_type": "join", "product_id": "10000000-0000-0000-0000-000000000007", "deal_id": "20000000-0000-0000-0000-000000000004", "category": "fashion", "created_at": (now - timedelta(days=2)).isoformat() + "Z"},
        {"user_id": "00000000-0000-0000-0000-000000000003", "event_type": "view", "product_id": "10000000-0000-0000-0000-000000000025", "category": "electronics", "created_at": (now - timedelta(days=1)).isoformat() + "Z"},
        {"user_id": "00000000-0000-0000-0000-000000000003", "event_type": "share", "product_id": "10000000-0000-0000-0000-000000000025", "category": "electronics", "created_at": (now - timedelta(hours=12)).isoformat() + "Z"},
    ]
    
    return {
        "users": users,
        "products": products,
        "deals": deals,
        "events": events,
        "_demo_note": "All data above is synthetic demo data for hackathon demonstration purposes. All IDs are valid UUID strings."
    }
