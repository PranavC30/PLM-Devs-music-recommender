"""
Content-Based Filtering using cosine similarity on song features.
Features used: Mood, Genre, Language, Energy (one-hot encoded).
"""
import pandas as pd
import os

def _load_df():
    path = os.path.join(os.path.dirname(__file__), "data", "songs.csv")
    return pd.read_csv(path)

def _build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode categorical features into a numeric matrix."""
    features = pd.get_dummies(df[["Mood", "Genre", "Language", "Energy"]])
    return features

def _cosine_similarity_row(vec_a, matrix):
    """Compute cosine similarity between a vector and all rows of a matrix."""
    dot = matrix.dot(vec_a)
    norm_a = (vec_a ** 2).sum() ** 0.5
    norm_matrix = (matrix ** 2).sum(axis=1) ** 0.5
    denom = norm_matrix * norm_a
    denom = denom.where(denom != 0, other=1e-9)
    return dot / denom

def get_similar_songs(song_name: str, n: int = 6, language_filter: str = None) -> list:
    """
    Returns n songs most similar to `song_name` based on feature cosine similarity.
    Optionally filter results by language.
    """
    df = _load_df()
    features = _build_feature_matrix(df)

    # Find the target song
    matches = df[df["Song"].str.lower() == song_name.lower()]
    if matches.empty:
        # Try partial match
        matches = df[df["Song"].str.lower().str.contains(song_name.lower(), na=False)]
    if matches.empty:
        return []

    target_idx = matches.index[0]
    target_vec = features.loc[target_idx]

    # Compute similarities
    sims = _cosine_similarity_row(target_vec, features)
    sims = sims.drop(index=target_idx)  # exclude the song itself

    # Language filter
    if language_filter:
        valid_idx = df[df["Language"].str.lower() == language_filter.lower()].index
        sims = sims[sims.index.isin(valid_idx)]

    top_idx = sims.nlargest(n).index
    result = df.loc[top_idx].to_dict("records")

    # Add similarity score
    for i, idx in enumerate(top_idx):
        result[i]["similarity"] = round(float(sims[idx]) * 100, 1)

    return result


def get_recommendations_by_profile(
    liked_songs: list,
    n: int = 6,
    language_filter: str = None,
) -> list:
    """
    Given a list of liked song names, aggregate their feature vectors
    and return the top-n unseen similar songs.
    """
    df = _load_df()
    features = _build_feature_matrix(df)

    liked_idx = []
    for name in liked_songs:
        m = df[df["Song"].str.lower() == name.lower()]
        if not m.empty:
            liked_idx.append(m.index[0])

    if not liked_idx:
        return []

    # Average feature vector of liked songs
    avg_vec = features.loc[liked_idx].mean()

    # Compute similarity against all songs
    sims = _cosine_similarity_row(avg_vec, features)

    # Exclude already-liked songs
    sims = sims.drop(index=[i for i in liked_idx if i in sims.index], errors="ignore")

    # Language filter
    if language_filter:
        valid_idx = df[df["Language"].str.lower() == language_filter.lower()].index
        sims = sims[sims.index.isin(valid_idx)]

    top_idx = sims.nlargest(n).index
    result = df.loc[top_idx].to_dict("records")
    for i, idx in enumerate(top_idx):
        result[i]["similarity"] = round(float(sims[idx]) * 100, 1)

    return result
