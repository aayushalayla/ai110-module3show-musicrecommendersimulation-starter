"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    # Try relative import first (when run as module: python -m src.main)
    from .recommender import load_songs, recommend_songs
except ImportError:
    # Fall back to direct import (when run as script: python src/main.py)
    from recommender import load_songs, recommend_songs


def format_recommendations(recommendations: list) -> str:
    """
    Formats a list of recommendations into a clean, readable terminal output.
    
    Args:
        recommendations: List of (song_dict, score, explanation) tuples from recommend_songs()
    
    Returns:
        Formatted string with ranked recommendations
    """
    if not recommendations:
        return "No recommendations found."
    
    output = []
    output.append("=" * 80)
    output.append("🎵 TOP MUSIC RECOMMENDATIONS 🎵".center(80))
    output.append("=" * 80)
    output.append("")
    
    for rank, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        
        # Format: Rank. Title by Artist (Score/5.0)
        title = song.get('title', 'Unknown')
        artist = song.get('artist', 'Unknown Artist')
        genre = song.get('genre', 'N/A')
        mood = song.get('mood', 'N/A')
        
        output.append(f"  {rank}. {title}")
        output.append(f"     Artist: {artist} | Genre: {genre} | Mood: {mood}")
        output.append(f"     Score: {score:.2f} / 5.00 ({(score/5.0)*100:.1f}%)")
        output.append(f"     Why this match: {explanation}")
        output.append("")
    
    output.append("=" * 80)
    return "\n".join(output)


def main() -> None:
    """Main entry point for the music recommender."""
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    
    print("\n📊 User Profile:")
    print(f"   Favorite Genre: {user_prefs['genre']}")
    print(f"   Favorite Mood: {user_prefs['mood']}")
    print(f"   Target Energy Level: {user_prefs['energy']}/1.0")

    recommendations = recommend_songs(user_prefs, songs, k=5)
    
    # Display formatted recommendations
    formatted_output = format_recommendations(recommendations)
    print(formatted_output)


if __name__ == "__main__":
    main()
