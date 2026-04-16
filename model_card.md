# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

---

## 2. Goal / Task

VibeMatch suggests songs a user might enjoy based on three things: their favorite genre, preferred mood, and how energetic they want the music to feel.

It does not learn from listening history. It scores every song in the catalog against the user's stated preferences and returns the top five matches.


---

## 3. Data Used

- **Catalog size:** 20 songs
- **Features per song:** title, artist, genre, mood, energy (0–1), tempo (BPM), valence, danceability, acousticness
- **Genres represented:** pop, lofi, rock, jazz, ambient, synthwave, electronic, hip-hop, indie pop, soul, country, classical, metal, reggae, indie rock, folk, deep house
- **Moods represented:** happy, chill, intense, relaxed, focused, moody, energetic, melancholic, nostalgic, dreamy, aggressive, laid-back, confident, peaceful, atmospheric
- **Features actually used for scoring:** genre, mood, and energy only — the rest are stored but ignored by the algorithm

**Limits:**
- 20 songs is a very small catalog. Most genres have only one or two songs.
- The dataset was hand-crafted for this project and does not represent real listening trends.
- There are no songs in languages other than English, and no classical or non-Western genres beyond one token entry each.

---

## 4. Algorithm Summary

The recommender scores every song on three criteria, then ranks by total score (highest first).

**Genre match — up to 2.0 points**
If the song's genre exactly matches what the user wants, it gets 2 points. If not, it gets 0. There is no partial credit. "Indie pop" and "pop" are treated as completely different genres.

**Mood match — up to 1.0 point**
Same idea. If the mood tag matches, add 1 point. If not, add nothing.

**Energy similarity — up to 2.0 points**
Energy is a number between 0 and 1 (0 = very quiet/slow, 1 = very loud/intense). The closer the song's energy is to the user's target, the more points it earns. The scoring uses a curve (Gaussian decay) so that being slightly off costs a little, but being way off costs a lot. A perfect match gives 2.0 points; a song that is 0.5 away gives less than 0.5 points.

**Total possible score: 5.0 points.**

The top 5 songs by total score are returned as recommendations.

---

## 5. Observed Behavior / Biases

**Gym Hero problem — genre beats mood**
Genre is worth 2 points and mood is only worth 1. This means a song in the right genre but the wrong mood will almost always outscore a song in the wrong genre but the right mood. In practice, a user who wants "happy pop" will get *Gym Hero* (pop, intense) as their #2 recommendation because it shares the pop genre — even though the vibe is totally different. The algorithm does not know that "intense" and "happy" are opposites.

- Jazz, rock, and electronic each have only one or two songs in the catalog. The top result is usually a perfect match. But positions 2–5 fill up with unrelated songs that just happen to have similar energy. A jazz listener gets folk and lofi filler. This is not useful.

- When genre and mood both miss, energy similarity is the only scoring signal left. This causes high-energy songs (metal, gym pop) to cluster together in the recommendations of any high-energy user, regardless of how different they actually sound.


- "Indie pop" gets zero genre points from a user who wants "pop," even though they are closely related. The same applies to "rock" vs. "metal" or "lofi" vs. "ambient." Real music listeners would consider these close; the algorithm treats them as strangers.

---

## 6. Evaluation Process

I tested all five user profiles defined in `src/main.py` and examined the top-5 recommendations for each:

- **High-Energy Pop** (genre: pop, mood: happy, energy: 0.8)
- **Chill Lofi** (genre: lofi, mood: chill, energy: 0.4)
- **Deep Intense Rock** (genre: rock, mood: intense, energy: 0.9)
- **Smooth Jazz** (genre: jazz, mood: relaxed, energy: 0.37)
- **Energetic Electronic** (genre: electronic, mood: energetic, energy: 0.95)

For each profile I looked at:
- Whether the #1 result was a genuine match
- Whether positions 2–5 made intuitive sense or were just energy-adjacent fillers
- Which songs appeared across multiple profiles (Gym Hero appeared in three)

I also compared pairs of profiles directly — for example, Smooth Jazz vs. Energetic Electronic — to check that very different preferences produced very different results. They did at position #1, but the filler results (positions 2–5) overlapped more than expected because energy similarity dominated when genre and mood didn't match.

No numeric accuracy metrics were used. Evaluation was based on whether results felt reasonable to a human listener.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- A classroom demonstration of how a rule-based recommender works
- Exploring how scoring weights affect output
- Understanding trade-offs in simple recommendation algorithms

**Not intended for:**
- Real music streaming or production use
- Users who want personalized recommendations based on listening history
- Any catalog larger than a few dozen songs (performance was not optimized)
- Making claims about musical taste, culture, or identity

---

## 8. Ideas for Improvement

**1. Add partial credit for related genres**
Instead of treating every genre mismatch as a 0, create a small similarity table. For example, "rock" and "metal" could share 1.0 point, while "rock" and "jazz" share 0. This would reduce the cliff between close and unrelated genres.

**2. Expand the catalog significantly**
With only 20 songs, most genres have one entry. Adding 100–200 songs — especially more jazz, rock, and electronic tracks — would make the recommendations feel meaningful past position #1.

**3. Let users weight the factors themselves**
Right now genre is always worth twice as much as mood. But some users care more about mood than genre. Letting users say "mood matters more to me right now" (like a slider) would make the system much more useful and would also reveal how sensitive the results are to those weights.
