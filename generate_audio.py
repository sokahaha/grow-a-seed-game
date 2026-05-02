#!/usr/bin/env python3
"""
Generate all TTS audio files for the Grow a Seed! review game (W2).
Usage:  python3 generate_audio.py
Output: audio/ folder with all mp3 files
"""

import asyncio
import json
import sys
from pathlib import Path

try:
    import edge_tts
except ImportError:
    print("pip3 install edge-tts")
    sys.exit(1)

# ── Configuration ──────────────────────────────────────────────
VOICE = "en-US-AnaNeural"    # Ana: young and clear (same as W1)
RATE = "+0%"                  # Normal speed for clarity
PITCH = "+10Hz"               # Higher pitch for playful kid-friendly tone
OUTPUT_DIR = Path(__file__).parent / "audio"

# ── Question Bank ─────────────────────────────────────────────
QUESTIONS = {
    "easy": [
        {
            "id": "e1",
            "tts": "Look at these pictures! Which one shows a sprout? That's a tiny green baby plant just poking out of the soil!",
            "growText": "Great job! You found the sprout!",
        },
        {
            "id": "e2",
            "tts": "This one protects the baby plant inside, like a tiny raincoat! Which picture is it?",
            "growText": "Yes! The seed coat is like a raincoat!",
        },
        {
            "id": "e3",
            "tts": "Shhh... this one is sleeping inside the seed. A tiny baby plant, curled up and waiting. Which picture shows it?",
            "growText": "That's right! The embryo is a sleeping baby plant!",
        },
        {
            "id": "e4",
            "tts": "This one is like a packed lunchbox, full of yummy food for the baby plant! Which picture shows it?",
            "growText": "Correct! The cotyledon is a lunchbox!",
        },
        {
            "id": "e5",
            "tts": "Whoa! This seed is drinking water and getting BIGGER and ROUNDER, like a balloon! Which picture shows it?",
            "growText": "Yes! The seed is swelling like a balloon!",
        },
        {
            "id": "e6",
            "tts": "These seeds are taking a really, really long nap through the cold winter. Zzz... Which picture shows it?",
            "growText": "That's right! Dormancy is a long winter nap!",
        },
        {
            "id": "e7",
            "tts": "Ring ring ring! The alarm clock inside the seed goes off! The baby plant wakes up and starts to grow! Which picture shows this?",
            "growText": "Yes! Germination is when the alarm goes off!",
        },
        {
            "id": "e8",
            "tts": "This one is like a tiny green arm pushing UP through the soil, reaching for the sky! Which picture shows it?",
            "growText": "Great! The shoot reaches for the sky!",
        },
        {
            "id": "e9",
            "tts": "Ta-da! This little baby plant just popped out of the soil! It's brand new! Which picture shows it?",
            "growText": "Correct! A seedling just came out!",
        },
        {
            "id": "e10",
            "tts": "A seed needs three things to wake up. It needs water... it needs warmth... and it needs one more thing. Can you guess?",
            "growText": "Yes! Seeds need oxygen to breathe!",
        },
        {
            "id": "e11",
            "tts": "Leaves are like tiny kitchens! They cook food using nothing but sunlight! What's this big word called?",
            "growText": "Wow! You know photosynthesis!",
        },
        {
            "id": "e12",
            "tts": "Some things need batteries to work. But leaves only need sunshine! They run on solar power! What do we call that?",
            "growText": "That's right! Solar-powered!",
        },
    ],
    "hard": [
        {
            "id": "h1",
            "tts": "A tiny seed lands in warm, wet soil. It's time to grow! But what happens FIRST? The seed coat cracks open, the root grows down, or the flower blooms?",
            "growText": "Yes! The seed coat cracks open first!",
        },
        {
            "id": "h2",
            "tts": "Seeds need water, warmth, and oxygen to wake up. But one of these four things, seeds do NOT need to germinate. Which one?",
            "growText": "That's right! Seeds don't need sunlight underground!",
        },
        {
            "id": "h3",
            "tts": "A cotyledon is like a lunchbox full of food for the baby plant. But once the real leaves start cooking with sunlight, what happens to the cotyledon?",
            "growText": "Correct! The cotyledon falls off!",
        },
        {
            "id": "h4",
            "tts": "A little seedling is growing in a dark box. There's only one small hole letting light in. Which way will the shoot bend?",
            "growText": "Amazing! Plants always reach for the light!",
        },
        {
            "id": "h5",
            "tts": "The root grows DOWN to find water. But which part grows UP to find sunlight?",
            "growText": "Right! The shoot pushes up!",
        },
        {
            "id": "h6",
            "tts": "An embryo is a baby plant sleeping inside a seed. But once it pops out of the soil and opens its leaves, what do we call it now?",
            "growText": "Yes! Once it pops out, it's a seedling!",
        },
        {
            "id": "h7",
            "tts": "Quick quiz! A seed needs three things to wake up. Name all three!",
            "growText": "Yes! Water, warmth, and oxygen!",
        },
        {
            "id": "h8",
            "tts": "Leaves cook food using sunlight during the day. But at night, when there's no sun, plants actually breathe IN something, just like you! What do they breathe in?",
            "growText": "Yes! Plants breathe in oxygen at night, just like us!",
        },
        {
            "id": "h9",
            "tts": "Some seed coats are so tough that they need extreme heat to crack open! In Australia, some seeds only grow after what big event?",
            "growText": "Wow! Some seeds need fire to open!",
        },
        {
            "id": "h10",
            "tts": "A seed coat is like a raincoat. A cotyledon is like a lunchbox. And an embryo is like... what?",
            "growText": "Yes! The embryo is a sleeping baby!",
        },
        {
            "id": "h11",
            "tts": "Imagine a seed has water and oxygen, but it's freezing cold outside. Will it germinate?",
            "growText": "That's right! Seeds need warmth too!",
        },
        {
            "id": "h12",
            "tts": "Once germination starts, the seed CANNOT go back to sleep! It must keep growing! True or false?",
            "growText": "That's right! It can't stop!",
        },
    ],
}

# ── Shared phrases ─────────────────────────────────────────────
SHARED_PHRASES = {
    "wrong_retry": "Oops! Let's try again! You got this!",
    "victory": "Incredible! You grew a beautiful plant from a tiny seed! You are a real Seed Scientist!",
    "partial": "You grew {n} stages. Try again to grow the whole plant!",
}


async def generate_one(text: str, output_path: Path) -> bool:
    """Generate a single audio file. Returns True on success."""
    try:
        communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
        await communicate.save(str(output_path))
        return True
    except Exception as e:
        print(f"  Failed: {output_path.name} - {e}")
        return False


async def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Voice: {VOICE}")
    print(f"Output: {OUTPUT_DIR}/")
    print()

    tasks = []

    # Question TTS + grow feedback TTS
    for level, questions in QUESTIONS.items():
        for q in questions:
            qid = q["id"]
            tasks.append(("question", qid, q["tts"], OUTPUT_DIR / f"q_{qid}.mp3"))
            tasks.append(("grow", qid, q["growText"], OUTPUT_DIR / f"grow_{qid}.mp3"))

    # Shared phrases
    for key, text in SHARED_PHRASES.items():
        tasks.append(("shared", key, text, OUTPUT_DIR / f"{key}.mp3"))

    # Partial messages (n=1 to 5)
    for n in range(1, 6):
        text = SHARED_PHRASES["partial"].replace("{n}", str(n))
        tasks.append(("shared", f"partial_{n}", text, OUTPUT_DIR / f"partial_{n}.mp3"))

    total = len(tasks)
    success = 0
    failed = []

    print(f"Generating {total} audio files...\n")

    for i, (category, name, text, path) in enumerate(tasks):
        short_text = text[:50] + "..." if len(text) > 50 else text
        print(f"  [{i+1}/{total}] {category}/{name}")
        ok = await generate_one(text, path)
        if ok:
            success += 1
        else:
            failed.append(name)
        await asyncio.sleep(0.3)

    print(f"\n{'='*50}")
    print(f"Generated: {success}/{total}")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    asyncio.run(main())
