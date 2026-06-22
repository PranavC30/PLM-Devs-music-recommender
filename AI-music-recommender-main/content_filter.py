import pandas as pd
import os

def _load_df():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "songs.csv")
    return pd.read_csv(path)

def _build_feature_matrix(df):
    return pd.get_dummies(df[["Mood", "Genre", "Language", "Energy"]])

def _cosine_similarity_row(vec_a, matrix):
    dot = matrix.dot(vec_a)
    norm_a = (vec_a ** 2).sum() ** 0.5
    norm_matrix = (matrix ** 2).sum(axis=1) ** 0.5
    denom = norm_matrix * norm_a
    denom = denom.where(denom != 0, other=1e-9)
    return dot / denom

def get_similar_songs(song_name: str, n: int = 6, language_filter: str = None) -> list:
    df = _load_df()
    features = _build_feature_matrix(df)
    matches = df[df["Song"].str.lower() == song_name.lower()]
    if matches.empty:
        matches = df[df["Song"].str.lower().str.contains(song_name.lower(), na=False)]
    if matches.empty:
        return []
    target_idx = matches.index[0]
    target_vec = features.loc[target_idx]
    sims = _cosine_similarity_row(target_vec, features).drop(index=target_idx)
    if language_filter:
        valid_idx = df[df["Language"].str.lower() == language_filter.lower()].index
        sims = sims[sims.index.isin(valid_idx)]
    top_idx = sims.nlargest(n).index
    result = df.loc[top_idx].to_dict("records")
    for i, idx in enumerate(top_idx):
        result[i]["similarity"] = round(float(sims[idx]) * 100, 1)
    return result

def get_recommendations_by_profile(liked_songs: list, n: int = 6, language_filter: str = None) -> list:
    df = _load_df()
    features = _build_feature_matrix(df)
    liked_idx = [df[df["Song"].str.lower() == name.lower()].index[0]
                 for name in liked_songs
                 if not df[df["Song"].str.lower() == name.lower()].empty]
    if not liked_idx:
        return []
    avg_vec = features.loc[liked_idx].mean()
    sims = _cosine_similarity_row(avg_vec, features)
    sims = sims.drop(index=[i for i in liked_idx if i in sims.index], errors="ignore")
    if language_filter:
        valid_idx = df[df["Language"].str.lower() == language_filter.lower()].index
        sims = sims[sims.index.isin(valid_idx)]
    top_idx = sims.nlargest(n).index
    result = df.loc[top_idx].to_dict("records")
    for i, idx in enumerate(top_idx):
        result[i]["similarity"] = round(float(sims[idx]) * 100, 1)
    return result
