
"""Seed AnimeWall's default aesthetic categories."""

import asyncio

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.database import dispose_database, get_session_factory
from app.models import Category


CATEGORIES = [
    {
        "slug": "nature",
        "name": "Nature",
        "kanji": "自然",
        "romaji": "Shizen",
        "description": "Quiet mossy forests, ancient weeping willows, morning mist rolling over emerald valleys, and sacred cedar groves.",
        "accent_color": "#4A6B56",
        "sort_order": 1,
        "is_active": True,
    },
    {
        "slug": "japanese-aesthetic",
        "name": "Japanese Aesthetic",
        "kanji": "日本美",
        "romaji": "Nihonbi",
        "description": "Vermilion torii gates, paper shoji lanterns, twilight Kyoto alleyways, and the timeless principle of Wabi-Sabi.",
        "accent_color": "#B83B3B",
        "sort_order": 2,
        "is_active": True,
    },
    {
        "slug": "dark",
        "name": "Dark",
        "kanji": "闇",
        "romaji": "Yami",
        "description": "Yūgen shadows, melancholic rainy nightscapes, deep midnight silhouettes, and contemplative solitude.",
        "accent_color": "#2C2D35",
        "sort_order": 3,
        "is_active": True,
    },
    {
        "slug": "minimalist",
        "name": "Minimalist",
        "kanji": "簡素",
        "romaji": "Kanso",
        "description": "Intelligent use of Ma (negative space), gentle muted tones, clean geometric framing, and breathing room for your icons.",
        "accent_color": "#8C857B",
        "sort_order": 4,
        "is_active": True,
    },
    {
        "slug": "cyberpunk",
        "name": "Cyberpunk",
        "kanji": "電脳",
        "romaji": "Dennou",
        "description": "Neon-drenched Shibuya crossings, holographic rain reflections, futuristic megastructures, and retro-futurism.",
        "accent_color": "#6C429C",
        "sort_order": 5,
        "is_active": True,
    },
    {
        "slug": "romance",
        "name": "Romance",
        "kanji": "恋",
        "romaji": "Koi",
        "description": "Fleeting twilight meetings, drifting cherry blossoms, nostalgic sunsets, and bittersweet memories beneath open skies.",
        "accent_color": "#D97B8F",
        "sort_order": 6,
        "is_active": True,
    },
    {
        "slug": "action",
        "name": "Action",
        "kanji": "躍動",
        "romaji": "Yakudou",
        "description": "Dynamic sword sweeps, celestial sorcery battles, roaring wind trails, and thunderous cinematic climaxes.",
        "accent_color": "#D45037",
        "sort_order": 7,
        "is_active": True,
    },
    {
        "slug": "landscape",
        "name": "Landscape",
        "kanji": "風景",
        "romaji": "Fuukei",
        "description": "Towering cumulonimbus clouds over azure coasts, panoramic mountain ranges, and expansive Makoto Shinkai vistas.",
        "accent_color": "#3B7080",
        "sort_order": 8,
        "is_active": True,
    },
]


async def seed_categories() -> None:
    factory = get_session_factory()

    try:
        async with factory() as session:
            statement = (
                insert(Category)
                .values(CATEGORIES)
                .on_conflict_do_nothing(
                    index_elements=[Category.slug]
                )
            )

            result = await session.execute(statement)
            await session.commit()

            total = await session.scalar(
                select(func.count()).select_from(Category)
            )

            print(f"New categories inserted: {result.rowcount}")
            print(f"Total categories in database: {total}")

    finally:
        await dispose_database()


if __name__ == "__main__":
    asyncio.run(seed_categories())
