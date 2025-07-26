#!/usr/bin/env python3
"""
Meme Loader Utility
Stage 7: Loads meme library from folders, ensures correct structure,
and provides random meme selection by category.
"""

import os
import random
from typing import Dict, List, Set


def load_meme_library(meme_folder: str) -> Dict[str, List[str]]:
    """
    Load all meme images/videos into a library grouped by category.

    Args:
        meme_folder: Path to the main meme folder.

    Returns:
        Dictionary {category_name: [list of meme file paths]}.
    """
    meme_library: Dict[str, List[str]] = {}

    if not os.path.exists(meme_folder):
        os.makedirs(meme_folder, exist_ok=True)
        return meme_library

    for category in os.listdir(meme_folder):
        category_path = os.path.join(meme_folder, category)
        if os.path.isdir(category_path):
            files = [
                os.path.join(category_path, f)
                for f in os.listdir(category_path)
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".mp4"))
            ]
            if files:
                meme_library[category] = files

    return meme_library


def get_random_memes(
    meme_library: Dict[str, List[str]],
    selected_categories: Set[str],
    count: int
) -> List[str]:
    """
    Get a random selection of memes from selected categories.

    Args:
        meme_library: Dictionary {category: [file paths]}.
        selected_categories: Set of categories to include.
        count: Number of memes to retrieve.

    Returns:
        List of meme file paths.
    """
    if not isinstance(meme_library, dict):
        raise ValueError("Invalid meme library: expected a dictionary of categories.")

    available_memes: List[str] = []
    for category in selected_categories:
        available_memes.extend(meme_library.get(category, []))

    if not available_memes:
        return []

    return random.sample(available_memes, min(count, len(available_memes)))
