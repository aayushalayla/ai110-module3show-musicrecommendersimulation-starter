import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from CSV, converting numeric fields to appropriate types for scoring.
    
    Loads songs from a CSV file and converts them to dictionaries.
    
    Reads from csv_path (e.g., 'data/songs.csv') and returns a list of dictionaries.
    Numerical columns (id, energy, tempo_bpm, valence, danceability, acousticness)
    are converted to appropriate numeric types so they can be used in scoring calculations.
    
    Args:
        csv_path: Path to the CSV file (relative or absolute)
        
    Returns:
        List of dictionaries, one per song, with keys:
        - id (int), title (str), artist (str), genre (str), mood (str)
        - energy (float), tempo_bpm (float), valence (float), danceability (float), acousticness (float)
        
    Example:
        >>> songs = load_songs('data/songs.csv')
        >>> songs[0]['energy']  # Returns 0.82 (float, not string)
        0.82
    """
    songs = []
    
    # Numeric columns that need to be converted from strings to floats/ints
    numeric_columns = {
        'id': int,
        'energy': float,
        'tempo_bpm': float,
        'valence': float,
        'danceability': float,
        'acousticness': float,
    }
    
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert numeric columns
            for col_name, col_type in numeric_columns.items():
                if col_name in row:
                    row[col_name] = col_type(row[col_name])
            songs.append(row)
    
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song using genre (2.0), mood (1.0), and energy similarity (Gaussian).
    
    Scores a single song against user preferences using the Algorithm Recipe.
    
    ALGORITHM RECIPE (from Phase 2):
    ================================
    Score = Genre Match + Mood Match + Energy Similarity
    
    1. Genre Match (2.0 points)
       - If song['genre'] == user_prefs['genre']: +2.0 pts
       - Otherwise: +0.0 pts
       - Binary match only (no partial credit for related genres)
    
    2. Mood Match (1.0 point)
       - If song['mood'] == user_prefs['mood']: +1.0 pt
       - Otherwise: +0.0 pts
       - Binary match only
    
    3. Energy Similarity (0–2.0 points using Gaussian decay)
       - Calculate difference: diff = |song['energy'] - user_prefs['energy']|
       - Apply Gaussian: energy_score = 2.0 * exp(-5 * diff²)
       - Perfect match (diff ≤ 0.1): ~1.9–2.0 pts
       - Good match (diff ≤ 0.2): ~1.7–1.9 pts
       - Fair match (diff ≤ 0.35): ~1.0–1.7 pts
       - Poor match (diff > 0.5): < 0.5 pts
    
    TOTAL SCORE RANGE: 0.0–5.0 points (when all three factors align perfectly)
    
    RETURN FORMAT:
    - Tuple of (score: float, reasons: List[str])
    - Example: (4.5, ['genre match (+2.0)', 'mood match (+1.0)', 'energy similarity (+1.5)'])
    - Reasons should explain each component with its points, so users understand why a song was scored
    
    Args:
        user_prefs: Dict with keys 'genre', 'mood', 'energy' (representing user preferences)
        song: Dict with keys 'title', 'genre', 'mood', 'energy' (and other metadata)
    
    Returns:
        Tuple of (total_score, list_of_reasons)
        Example:
            >>> score, reasons = score_song(
            ...     {'genre': 'pop', 'mood': 'happy', 'energy': 0.8},
            ...     {'title': 'Sunrise City', 'genre': 'pop', 'mood': 'happy', 'energy': 0.82}
            ... )
            >>> score
            4.998
            >>> reasons
            ['genre match (+2.0)', 'mood match (+1.0)', 'energy similarity (+1.998)']
    """
    import math
    
    reasons = []
    score = 0.0
    
    # 1. Genre Match (2.0 points)
    genre_score = 0.0
    if song.get('genre') == user_prefs.get('genre'):
        genre_score = 2.0
        reasons.append(f"genre match (+{genre_score})")
    else:
        reasons.append(f"genre mismatch ({song.get('genre')} ≠ {user_prefs.get('genre')})")
    score += genre_score
    
    # 2. Mood Match (1.0 point)
    mood_score = 0.0
    if song.get('mood') == user_prefs.get('mood'):
        mood_score = 1.0
        reasons.append(f"mood match (+{mood_score})")
    else:
        reasons.append(f"mood mismatch ({song.get('mood')} ≠ {user_prefs.get('mood')})")
    score += mood_score
    
    # 3. Energy Similarity (0–2.0 points using Gaussian)
    energy_diff = abs(float(song.get('energy', 0)) - float(user_prefs.get('energy', 0)))
    energy_score = 2.0 * math.exp(-5 * energy_diff ** 2)
    reasons.append(f"energy similarity (+{energy_score:.3f})")
    score += energy_score
    
    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs, rank by descending score, and return the top K recommendations.
    
    ALGORITHM PROCESS:
    ==================
    1. Score Loop: Iterate through ALL songs, scoring each one using score_song()
    2. Ranking: Sort all (song, score, explanation) tuples by score descending
    3. Selection: Return only the top K results
    
    PYTHONIC APPROACH:
    - Use a list comprehension to generate (song, score, reasons) tuples
    - Use sorted() with a custom key to rank by score
    - Slice [:k] to get top K results
    
    WHY sorted() INSTEAD OF .sort()?
    ================================
    .sort() (in-place):
      - Modifies the original list
      - More memory efficient (no copy)
      - Returns None (chaining not possible)
      - Use when you own the list and don't need the original
      - Example: my_list.sort(key=..., reverse=True)
    
    sorted() (creates new list):
      - Creates and returns a NEW sorted list
      - Original list unchanged
      - Chainable with other operations
      - Use when you need to preserve original or work with immutable sequences
      - Example: new_list = sorted(my_list, key=..., reverse=True)
    
    For recommend_songs(), we use sorted() because:
    1. We don't own the input songs list (it comes from caller)
    2. We need to preserve the original order for other use cases
    3. It's cleaner and more functional (immutable approach)
    
    Args:
        user_prefs: Dict with keys 'genre', 'mood', 'energy'
        songs: List of song dictionaries from load_songs()
        k: Number of top recommendations to return (default 5)
    
    Returns:
        List of tuples: [(song_dict, score, explanation), ...]
        Sorted by score descending (highest score first)
        Limited to top K results
        
    Example:
        >>> user = {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}
        >>> recommendations = recommend_songs(user, songs, k=5)
        >>> recommendations[0]
        ({'title': 'Sunrise City', ...}, 4.996, 'genre match (+2.0); mood match (+1.0); energy similarity (+1.996)')
    """

    # 1. SCORE LOOP: Score every song and build (song, score, explanation) tuples
    # This is the Pythonic list comprehension approach
    scored_songs = [
        (song, score, '; '.join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]
    
    # 2. RANKING: Sort by score (second element) in descending order
    # Using sorted() creates a new list, preserving the original order of `songs`
    ranked_songs = sorted(scored_songs, key=lambda x: x[1], reverse=True)
    
    # 3. SELECTION: Return only the top K results
    top_k = ranked_songs[:k]
    
    return top_k
