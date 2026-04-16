import csv
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Challenge 2 — Scoring Modes (Strategy pattern)
# Each mode reweights the three base signals: genre, mood, energy.
# Switch modes by passing scoring_mode in user_prefs or via recommend_songs().
# ---------------------------------------------------------------------------
SCORING_MODES: Dict[str, Dict[str, float]] = {
    # Default: genre matters most, energy close behind, mood is a tiebreaker
    "balanced":      {"genre": 2.0, "mood": 1.0, "energy": 2.0},
    # Genre-First: heavily rewards exact genre matches; mood/energy are secondary
    "genre_first":   {"genre": 4.0, "mood": 0.5, "energy": 1.0},
    # Mood-First: emotional feel is the top priority over genre label
    "mood_first":    {"genre": 1.0, "mood": 3.0, "energy": 1.0},
    # Energy-Focused: tempo/intensity drives ranking; genre/mood are minor hints
    "energy_focused": {"genre": 1.0, "mood": 0.5, "energy": 4.0},
}


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
    # Challenge 1 — new advanced attributes (all optional with safe defaults)
    popularity: int = 50          # 0–100: how widely known the song is
    release_decade: int = 2020    # e.g. 1990, 2000, 2010, 2020
    sub_mood: str = ""            # fine-grained mood tag (euphoric, aggressive, etc.)
    language: str = "english"     # language of the lyrics
    liveness: float = 0.3         # 0–1: how live/raw vs polished the recording sounds


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
    # Challenge 1 — advanced preference fields (all optional)
    preferred_sub_mood: str = ""       # "" means no preference
    preferred_decade: int = 0          # 0  means no preference
    popularity_target: float = -1.0    # -1 means no preference
    preferred_liveness: float = -1.0   # -1 means no preference
    preferred_language: str = ""       # "" means no preference
    # Challenge 2 — scoring mode for this profile
    scoring_mode: str = "balanced"
    # Challenge 3 — opt-in to diversity reranking
    diversity: bool = False


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _song_to_dict(self, song: Song) -> Dict:
        return {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "tempo_bpm": song.tempo_bpm,
            "valence": song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
            "popularity": song.popularity,
            "release_decade": song.release_decade,
            "sub_mood": song.sub_mood,
            "language": song.language,
            "liveness": song.liveness,
        }

    def _user_to_prefs(self, user: UserProfile) -> Dict:
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "preferred_sub_mood": user.preferred_sub_mood,
            "preferred_decade": user.preferred_decade,
            "popularity_target": user.popularity_target,
            "preferred_liveness": user.preferred_liveness,
            "preferred_language": user.preferred_language,
            "scoring_mode": user.scoring_mode,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_prefs = self._user_to_prefs(user)
        scored = [
            (song, score_song(user_prefs, self._song_to_dict(song))[0])
            for song in self.songs
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_prefs = self._user_to_prefs(user)
        sc, reasons = score_song(user_prefs, self._song_to_dict(song))
        return f"Score {sc:.2f} — " + "; ".join(reasons)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from CSV, converting numeric fields to appropriate types.

    Returns a list of dicts. Numeric columns are cast to int or float so they
    can be used directly in scoring calculations.
    """
    int_columns   = {"id", "release_decade", "popularity"}
    float_columns = {"energy", "tempo_bpm", "valence", "danceability",
                     "acousticness", "liveness"}

    songs = []
    with open(csv_path, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for col in int_columns:
                if col in row:
                    row[col] = int(row[col])
            for col in float_columns:
                if col in row:
                    row[col] = float(row[col])
            songs.append(row)

    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


# ---------------------------------------------------------------------------
# Challenge 1 — Advanced feature scoring helpers
# ---------------------------------------------------------------------------

def _score_sub_mood(user_prefs: Dict, song: Dict) -> Tuple[float, Optional[str]]:
    """
    +0.75 if user specified a sub_mood preference and the song matches it exactly.
    Sub-mood is a finer emotional label (e.g. 'euphoric', 'aggressive', 'nostalgic').
    """
    preferred = user_prefs.get("preferred_sub_mood", "")
    if not preferred:
        return 0.0, None
    if song.get("sub_mood", "") == preferred:
        return 0.75, f"sub-mood match (+0.75)"
    return 0.0, f"sub-mood mismatch ({song.get('sub_mood')} ≠ {preferred})"


def _score_popularity(user_prefs: Dict, song: Dict) -> Tuple[float, Optional[str]]:
    """
    +1.0 max using Gaussian decay around the user's target popularity (0–100).
    Sigma = 25 so songs within ~25 points score above 0.6.
    A target of -1 means the user has no popularity preference (skipped).
    """
    target = float(user_prefs.get("popularity_target", -1))
    if target < 0:
        return 0.0, None
    diff = abs(song.get("popularity", 50) - target)
    pts = round(1.0 * math.exp(-((diff / 25) ** 2)), 3)
    return pts, f"popularity match (+{pts})"


def _score_decade(user_prefs: Dict, song: Dict) -> Tuple[float, Optional[str]]:
    """
    Reward songs from the user's preferred era:
      - Exact decade match  → +1.0
      - Within 10 years     → +0.5
      - More than 10 years away → 0.0
    A preferred_decade of 0 means no preference (skipped).
    """
    preferred = int(user_prefs.get("preferred_decade", 0))
    if preferred == 0:
        return 0.0, None
    song_decade = int(song.get("release_decade", 0))
    if song_decade == preferred:
        return 1.0, f"decade match ({song_decade}s, +1.0)"
    if abs(song_decade - preferred) <= 10:
        return 0.5, f"nearby decade ({song_decade}s, +0.5)"
    return 0.0, f"era mismatch ({song_decade}s ≠ {preferred}s)"


def _score_liveness(user_prefs: Dict, song: Dict) -> Tuple[float, Optional[str]]:
    """
    +1.0 max using Gaussian decay around the user's preferred liveness (0–1).
    Sigma controls how tightly studio vs live feel is penalized.
    A preferred_liveness of -1 means no preference (skipped).
    """
    target = float(user_prefs.get("preferred_liveness", -1))
    if target < 0:
        return 0.0, None
    diff = abs(float(song.get("liveness", 0.3)) - target)
    pts = round(1.0 * math.exp(-8 * diff ** 2), 3)
    return pts, f"liveness match (+{pts})"


def _score_language(user_prefs: Dict, song: Dict) -> Tuple[float, Optional[str]]:
    """
    +0.5 if the song's language matches the user's preferred language.
    An empty string means no preference (skipped).
    """
    preferred = user_prefs.get("preferred_language", "")
    if not preferred:
        return 0.0, None
    if song.get("language", "").lower() == preferred.lower():
        return 0.5, f"language match (+0.5)"
    return 0.0, f"language mismatch ({song.get('language')} ≠ {preferred})"


# ---------------------------------------------------------------------------
# Core scoring
# ---------------------------------------------------------------------------

def score_song(user_prefs: Dict, song: Dict,
               weights: Optional[Dict[str, float]] = None) -> Tuple[float, List[str]]:
    """Score a single song against user preferences.

    Challenge 2 — Scoring Modes
    ===========================
    The three base signals (genre, mood, energy) are weighted according to the
    active scoring mode. Weights are passed in or resolved from user_prefs.

    Challenge 1 — Advanced Features
    ================================
    Five bonus signals are added on top of the base score when the user has
    specified those preferences. They are independent of the scoring mode.

    Base score range  : 0 – (genre_w + mood_w + energy_w)
    Bonus score range : 0 – 4.25  (sub_mood 0.75 + popularity 1.0 +
                                    decade 1.0 + liveness 1.0 + language 0.5)

    Args:
        user_prefs : dict with at minimum 'genre', 'mood', 'energy' keys
        song       : dict loaded from CSV (all numeric fields already cast)
        weights    : optional override for {genre, mood, energy} weights

    Returns:
        (total_score, list_of_reason_strings)
    """
    # Resolve mode weights
    if weights is None:
        mode = user_prefs.get("scoring_mode", "balanced")
        weights = SCORING_MODES.get(mode, SCORING_MODES["balanced"])

    genre_w  = weights["genre"]
    mood_w   = weights["mood"]
    energy_w = weights["energy"]

    reasons: List[str] = []
    score = 0.0

    # --- 1. Genre match ---------------------------------------------------
    genre_score = 0.0
    if song.get("genre") == user_prefs.get("genre"):
        genre_score = genre_w
        reasons.append(f"genre match (+{genre_score})")
    else:
        reasons.append(
            f"genre mismatch ({song.get('genre')} ≠ {user_prefs.get('genre')})"
        )
    score += genre_score

    # --- 2. Mood match ----------------------------------------------------
    mood_score = 0.0
    if song.get("mood") == user_prefs.get("mood"):
        mood_score = mood_w
        reasons.append(f"mood match (+{mood_score})")
    else:
        reasons.append(
            f"mood mismatch ({song.get('mood')} ≠ {user_prefs.get('mood')})"
        )
    score += mood_score

    # --- 3. Energy similarity (Gaussian) ---------------------------------
    energy_diff  = abs(float(song.get("energy", 0)) - float(user_prefs.get("energy", 0)))
    energy_score = round(energy_w * math.exp(-5 * energy_diff ** 2), 3)
    reasons.append(f"energy similarity (+{energy_score})")
    score += energy_score

    # --- Challenge 1 bonus signals ---------------------------------------
    for fn in (_score_sub_mood, _score_popularity, _score_decade,
               _score_liveness, _score_language):
        pts, label = fn(user_prefs, song)
        if label is not None:
            reasons.append(label)
        score += pts

    return (round(score, 3), reasons)


# ---------------------------------------------------------------------------
# Challenge 3 — Diversity penalty (greedy reranker)
# ---------------------------------------------------------------------------

def _greedy_diverse_select(
    scored_songs: List[Tuple[Dict, float, str]],
    k: int,
    artist_penalty: float = 1.5,
    max_per_genre: int = 2,
    genre_penalty: float = 0.75,
) -> List[Tuple[Dict, float, str]]:
    """Greedily pick top-k songs while penalising repeated artists and genres.

    At each step we deduct:
      - artist_penalty  if the artist already appears in selected results
      - genre_penalty   if the genre already appears max_per_genre times

    The effective score is used only for ordering; the stored score is unchanged.
    """
    selected: List[Tuple[Dict, float, str]] = []
    artist_counts: Dict[str, int] = {}
    genre_counts:  Dict[str, int] = {}
    remaining = list(scored_songs)

    while len(selected) < k and remaining:
        best_idx = 0
        best_eff  = -999.0

        for i, (song, raw_score, _) in enumerate(remaining):
            artist = song.get("artist", "")
            genre  = song.get("genre", "")
            penalty = 0.0
            if artist_counts.get(artist, 0) > 0:
                penalty += artist_penalty
            if genre_counts.get(genre, 0) >= max_per_genre:
                penalty += genre_penalty
            eff = raw_score - penalty
            if eff > best_eff:
                best_eff = eff
                best_idx = i

        chosen = remaining.pop(best_idx)
        artist_counts[chosen[0].get("artist", "")] = \
            artist_counts.get(chosen[0].get("artist", ""), 0) + 1
        genre_counts[chosen[0].get("genre", "")] = \
            genre_counts.get(chosen[0].get("genre", ""), 0) + 1
        selected.append(chosen)

    return selected


# ---------------------------------------------------------------------------
# Top-level recommendation function
# ---------------------------------------------------------------------------

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: Optional[str] = None,
    diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """Score all songs, rank by descending score, and return the top K.

    Challenge 2 — pass mode="genre_first" / "mood_first" / "energy_focused"
                  (or set user_prefs['scoring_mode']) to switch strategies.
    Challenge 3 — pass diversity=True to apply the greedy diversity reranker.

    Args:
        user_prefs : dict with genre, mood, energy (and optional advanced keys)
        songs      : list of song dicts from load_songs()
        k          : number of results to return
        mode       : override for scoring_mode (takes precedence over user_prefs)
        diversity  : if True, apply diversity penalty after initial ranking

    Returns:
        List of (song_dict, score, explanation_string) sorted by score desc.
    """
    # Resolve which weights to use
    active_mode = mode or user_prefs.get("scoring_mode", "balanced")
    weights = SCORING_MODES.get(active_mode, SCORING_MODES["balanced"])

    scored_songs = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song, weights=weights)]
    ]

    ranked = sorted(scored_songs, key=lambda x: x[1], reverse=True)

    if diversity:
        return _greedy_diverse_select(ranked, k)

    return ranked[:k]
