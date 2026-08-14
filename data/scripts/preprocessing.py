import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
RAW_PATH = SCRIPT_DIR.parent / "raw" / "ASAP2_train_sourcetexts.csv"
OUT_DIR = SCRIPT_DIR.parent / "processed"

def load_and_clean(path=RAW_PATH, prompts_to_keep=None):
    df = pd.read_csv(str(path))

    keep_cols = [
        "essay_id", "score", "full_text", "assignment", "prompt_name",
        "economically_disadvantaged", "student_disability_status",
        "ell_status", "race_ethnicity", "gender", "source_text_1"
    ]
    df = df[keep_cols]

    if prompts_to_keep:
        df = df[df["prompt_name"].isin(prompts_to_keep)]

    df = df.dropna(subset=["full_text", "score"])
    df["word_count"] = df["full_text"].str.split().str.len()

    for col in ["economically_disadvantaged", "student_disability_status", "ell_status"]:
        df[col] = df[col].fillna("Unknown")

    return df

def stratified_split(df, test_size=0.15, val_size=0.15, seed=42):
    train_val, test = train_test_split(
        df, test_size=test_size, stratify=df["score"], random_state=seed
    )
    train, val = train_test_split(
        train_val, test_size=val_size / (1 - test_size),
        stratify=train_val["score"], random_state=seed
    )
    return train, val, test


if __name__ == "__main__":
    df = load_and_clean(prompts_to_keep=None)  # change to e.g. ["Exploring Venus"] once team decides
    train, val, test = stratified_split(df)
    train.to_csv(OUT_DIR / "train.csv", index=False)
    val.to_csv(OUT_DIR / "val.csv", index=False)
    test.to_csv(OUT_DIR / "test.csv", index=False)
    print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
    print(df["score"].value_counts(normalize=True).sort_index())
