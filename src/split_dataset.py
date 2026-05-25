import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "clean_data.csv"

TRAIN_PATH = BASE_DIR / "data" / "processed" / "train.csv"
VAL_PATH   = BASE_DIR / "data" / "processed" / "val.csv"
TEST_PATH  = BASE_DIR / "data" / "processed" / "test.csv"

def main():
    print("📂 Loading cleaned dataset...")
    df = pd.read_csv(DATA_PATH)

    print(f"📊 Total samples: {len(df)}")

    # First split: Train (80%) and Temp (20%)
    train_df, temp_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["label"]  # 🔥 VERY IMPORTANT
    )

    # Second split: Validation (10%) and Test (10%)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,
        random_state=42,
        stratify=temp_df["label"]
    )

    print(f"✅ Train: {len(train_df)}")
    print(f"✅ Validation: {len(val_df)}")
    print(f"✅ Test: {len(test_df)}")

    # Save files
    train_df.to_csv(TRAIN_PATH, index=False)
    val_df.to_csv(VAL_PATH, index=False)
    test_df.to_csv(TEST_PATH, index=False)

    print("💾 Datasets saved successfully!")

if __name__ == "__main__":
    main()

# Commit marker: non-empty edit 5 - harmless comment added for commit tracking