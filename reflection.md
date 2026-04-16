# Reflection: Music Recommender Testing

## Profiles Tested

I tested five user profiles, each representing a distinct listening style:

| Profile | Genre | Mood | Energy |
|---|---|---|---|
| High-Energy Pop | pop | happy | 0.8 |
| Chill Lofi | lofi | chill | 0.4 |
| Deep Intense Rock | rock | intense | 0.9 |
| Smooth Jazz | jazz | relaxed | 0.37 |
| Energetic Electronic | electronic | energetic | 0.95 |

---

## Why "Gym Hero" Keeps Showing Up (Plain Language Explanation)

Imagine you walk into a store and ask for "a bright, cheerful pop song" — something you'd hear at a birthday party. The shopkeeper looks at their catalog and says: "Well, we have two pop songs. One is exactly what you want. The other is a high-intensity gym anthem. Since you said pop, here's both."

That's exactly what happens here. The recommender gives **two points for genre match** (the strongest signal) and only **one point for mood match**. There are only two pop songs in the catalog: *Sunrise City* (pop, happy) and *Gym Hero* (pop, intense). Because both are "pop," Gym Hero earns those two genre points whether or not the user wants a happy song or an intense one.

The system doesn't know that "intense" is the opposite of "happy" for someone in a celebratory mood. It just sees: "pop song, check. Genre match, +2 points. Done." The mood mismatch only costs one point, so Gym Hero still scores **3.84 out of 5** for someone who explicitly wants "happy" music — high enough to reach #2 on the list.

This is the core tension in the algorithm: **genre is worth twice as much as mood**, so a genre match can paper over a completely wrong emotional vibe.

---

## Surprises from the Results

**1. Chill Lofi was the most consistent profile.**  
Three of the top five recommendations were genuinely lofi songs (*Midnight Coding*, *Library Rain*, *Focus Flow*). This worked because the lofi genre happens to have good catalog coverage. The profile also benefited from low target energy (0.4), which naturally filters out the high-energy songs that dominate the catalog.

**2. Smooth Jazz fell off a cliff after the first recommendation.**  
*Coffee Shop Stories* scored a perfect 5.0 — it was the only jazz song in the catalog, and it matched genre, mood, and energy exactly. But then the next four recommendations scored around 2.0 and included folk, lofi, soul — none of them jazz or relaxed. They were only there because their energy levels happened to be close to 0.37. This exposed a weakness: **when a genre has only one song, the algorithm has no fallback plan** and just grabs whatever has similar energy.

**3. Gym Hero appeared in three different profiles' top-5 lists** — High-Energy Pop (#2), Deep Intense Rock (#2), and Energetic Electronic (#2). It's a "universal intruder" because it has high energy (0.93) and an "intense" mood, which happen to be close enough to what several profiles want on energy alone, even when the genre and mood are completely wrong. A single song can exploit the scoring formula from multiple angles.

**4. Rock and Electronic both had exactly one strong match and then nothing.**  
Storm Runner was a near-perfect 5.0 for the rock profile, and Electric Dreams was a perfect 5.0 for electronic. But the remaining four recommendations in each case were low-scoring mismatches that simply had similar energy levels. The catalog doesn't have enough rock or electronic songs to fill out a meaningful top-5.

---

## Profile Pair Comparisons

### High-Energy Pop vs. Chill Lofi
These two profiles sit at opposite ends of the energy dial (0.8 vs. 0.4) and completely different genres. As expected, their recommendations don't overlap at all. The pop profile returns high-energy songs clustered around 0.8 BPM, while the lofi profile returns slow, laid-back tracks. What changed: the Chill Lofi profile consistently scores 4.0+ on its top three picks because the lofi genre is well-represented in the catalog. The High-Energy Pop profile only has one true match (Sunrise City) before the quality drops sharply. This makes sense — lofi has three catalog entries, pop has two, and the algorithm rewards genre coverage.

### High-Energy Pop vs. Deep Intense Rock
Both profiles want high energy (0.8 and 0.9 respectively), but they differ on genre and mood. Gym Hero (#2) appears in both lists — for the pop user because it's pop, and for the rock user because it has an "intense" mood. What's telling is that Rooftop Lights (indie pop, happy) shows up at #3 for the pop user because of the happy mood match, but doesn't appear for the rock user at all. Sunrise City (pop, happy) actually sneaks into the rock user's top-5 at #5 purely on energy similarity — not because it sounds anything like rock. High energy pulls songs across genre boundaries when the catalog is thin.

### Chill Lofi vs. Smooth Jazz
Both profiles want low energy (0.4 and 0.37), but they target very different genres. Chill Lofi builds a solid top-3 from genuine lofi tracks because the catalog has three of them. Smooth Jazz builds a solid top-1 from the one jazz track, then collapses into random low-energy songs with no jazz or relaxed character at all. The contrast shows how much catalog depth matters: lofi has coverage, jazz doesn't. If you imagined these as real apps, the jazz listener would feel like the app forgot about them after the first song.

### Deep Intense Rock vs. Energetic Electronic
Both profiles push energy to the extreme (0.9 and 0.95). The gap between their #1 recommendations is near zero — Storm Runner and Electric Dreams each scored close to 5.0. But everything after #1 is nearly identical in character: Gym Hero, Thunder Strike, and Storm Runner/Electric Dreams trade places between the two lists. The algorithm can't distinguish "aggressive rock intensity" from "upbeat electronic energy" once genre and mood penalties are applied equally. From position #2 onward, both profiles are essentially just getting the highest-energy songs in the catalog regardless of fit.

### Smooth Jazz vs. Energetic Electronic
These are polar opposites — quiet and contemplative vs. loud and driving. The algorithm separates them cleanly at the top: Coffee Shop Stories for jazz, Electric Dreams for electronic, with scores of 5.0 each. But the interesting observation is in the filler recommendations. Smooth Jazz fills positions 2–5 with low-energy acoustic songs (folk, lofi, soul). Energetic Electronic fills positions 2–5 with high-energy aggressive songs (metal, rock, pop gym tracks). The energy signal alone is doing the heavy lifting here, correctly keeping these two profiles far apart even when genre and mood match no one. This is actually a case where the Gaussian energy decay is working well — it serves as a rough proxy for "similar feel" when nothing better is available.

---

## What This Tells Us About the Algorithm

The recommender works best when:
- The user's preferred genre has **multiple songs** in the catalog
- The genre + mood + energy all point in the same direction (they reinforce each other)

It breaks down when:
- A genre has only one song (jazz, rock, electronic each have 1–2 entries)
- A high-energy song from the wrong genre sneaks in via genre match (Gym Hero for pop fans)
- The user's preferences have no matching songs at all — the algorithm just finds the least-wrong option by energy, which doesn't feel like a real recommendation

The most important lesson: **scoring formulas are only as good as the catalog behind them.** With 20 songs and five distinct genres, many profiles are one song away from collapse.
