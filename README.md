# Music Recommendation System

A hybrid music recommender that blends **content-based filtering** (audio features) and **collaborative filtering** (playlist co-occurrence) to suggest tracks a user is likely to add to their playlist next. Built on a subset of Spotify's Million Playlist Dataset, enriched with audio features pulled from the Spotify Web API.

> NYU project by [Kristo Papadhimitri](mailto:kp1404@nyu.edu), [Tzu-An Wang](mailto:tw2770@nyu.edu), and [Yu-Hsiang Lan](mailto:yl12081@nyu.edu).

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Dataset](#dataset)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Results](#results)
- [Limitations & Future Work](#limitations--future-work)
- [References](#references)

## Overview

Streaming platforms live and die by how well they surface music a listener hasn't heard yet. This project compares three approaches to that problem — content-based filtering, collaborative filtering, and a hybrid of the two — against a set of simple baselines (popularity, logistic regression, decision tree), and shows that the hybrid model comes out on top.

## How It Works

**Content-based filtering** builds a profile for each playlist by averaging the audio-feature vectors (danceability, energy, loudness, acousticness, tempo, etc.) of its tracks, then ranks candidate tracks by cosine similarity to that profile.

**Collaborative filtering** builds a co-occurrence matrix across all playlists — how often two tracks show up together — and scores candidates by their total co-occurrence with tracks already in the playlist.

**Hybrid model** blends the two:

```
Hybrid Score = α · Content Score + (1 − α) · Collaborative Score
```

`α = 1` is pure content-based, `α = 0` is pure collaborative. Sweeping α showed **0.60** gives the best hit rate.

Evaluation uses a leakage-safe split: for each playlist, 80% of tracks are used to build the user profile / co-occurrence matrix, and the model is scored on whether it recommends the withheld 20% ("hit rate").

## Dataset

- **Source:** [Spotify Million Playlist Dataset](https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge) + Spotify Web API
- 4,000 playlists sampled from the full 1,000,000, each capped at 40 tracks
- 43,588 unique tracks enriched with audio features (popularity, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo)

Raw playlist/track CSVs aren't checked into this repo (Spotify's terms + file size) — regenerate them with the script below.

## Repository Structure

```
.
├── spotify_api_batch.py           # Pulls audio features from the Spotify Web API in batches of 50
├── Hybrid_Recommender.ipynb       # Early prototype: content/collaborative/hybrid scoring functions
├── music_recommendation_system.ipynb  # Final pipeline: leakage-safe train/test split, α tuning, evaluation
└── README.md
```

<!-- TODO: add playlists.csv generation script / notebook if it lives in this repo -->
<!-- TODO: add baseline models (popularity, logistic regression, decision tree) notebook if included -->

## Getting Started

### Requirements

```
pandas
numpy
scikit-learn
matplotlib
spotipy
requests
```

Install with:

```bash
pip install pandas numpy scikit-learn matplotlib spotipy requests
```

### 1. Fetch audio features

`spotify_api_batch.py` takes a CSV of playlist tracks (must include a `track_id` column) and pulls audio features for a slice of it using your own [Spotify API credentials](https://developer.spotify.com/dashboard):

```bash
python spotify_api_batch.py <file_path> <start_index> <end_index> <client_id> <client_secret>

# Example
python spotify_api_batch.py 4000_playlists_91598.csv 0 100 SPOTIFY_CLIENT_ID SPOTIFY_CLIENT_SECRET
```

This writes a `<start_index>_<end_index>.csv` with one row per track, including `Popularity`, `Danceability`, `Energy`, `Loudness`, `Valence`, `Tempo`, and more. Batching by 50 tracks keeps requests under Spotify's rate limits.

### 2. Run the recommender

Open `music_recommendation_system.ipynb` and point `track_path` / `playlist_path` at your `tracks.csv` / `playlists.csv`. The notebook will:

1. Clean and de-duplicate tracks and playlists
2. Split each playlist 80/20 into train/test tracks
3. Normalize audio features with `MinMaxScaler`
4. Build user profiles and a co-occurrence matrix from the training data only
5. Generate hybrid recommendations and evaluate hit rate across a sweep of α values

`Hybrid_Recommender.ipynb` contains the earlier, more exploratory version of these functions if you want to see how the scoring logic evolved.

## Results

| Recommendation Method       | Mean Hit Ratio |
|------------------------------|:--------------:|
| Popularity-Based              | 0.0007 |
| Logistic Regression            | 0.0007 |
| Decision Tree                  | 0.0205 |
| Content-Based Filtering        | 0.0011 |
| Collaborative Filtering        | 0.0449 |
| **Hybrid Model (α = 0.6)**     | **0.0467** |

Hit rate also climbs with playlist size — the model has more signal to work with once a user has 25+ tracks in their playlist, which makes sense given both scoring methods depend on having enough of the user's existing tracks to build a profile from.

## Limitations & Future Work

- Audio features and co-occurrence counts don't capture lyrical meaning, cultural context, or emotional tone — two songs can score high on cosine similarity and still miss what actually makes a track appealing.
- Collaborative filtering struggles with cold start: brand-new tracks with no playlist history get no signal.
- Next steps: NLP on lyrics for sentiment/theme features, incorporating explicit user feedback (likes/skips/ratings), and contextual signals like listening time or activity.

## References

1. Garanayak et al. *Content and popularity-based music recommendation system.* Int. J. Inf. Syst. Model. Des., 2022.
2. Junaidi et al. *Music recommendation system using machine learning methods.* EECSI, 2023.
3. Kumar. *Music recommendation system using machine learning.* ICAC3N, 2022.
4. Anthony et al. *The utilization of content based filtering for spotify music recommendation.* ICIEE, 2022.
5. Shakirova. *Collaborative filtering for music recommender system.* EIConRus, 2017.
6. Raschka. *Musicmood: Predicting the mood of music from song lyrics using machine learning.* 2016.
