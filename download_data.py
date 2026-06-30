from datasets import load_dataset
import os

print("Loading Fula dataset...")

dataset = load_dataset(
    "Pullo-Africa-Protagonist/FulaData",
    split="train"
)

# Audio column bilkul remove karo
dataset = dataset.remove_columns(["audio_path"])

print(f"Total rows: {len(dataset)}")
print(f"Columns: {dataset.column_names}")

# Pandas se dekho
df = dataset.to_pandas()

print("\n--- First 5 Samples ---")
for i in range(5):
    print(f"\nSample {i+1}:")
    print("Transcript:", df.iloc[i]["transcript"])
    print("Dialect:   ", df.iloc[i]["dialect_label"])

os.makedirs("./data", exist_ok=True)
df.to_csv("./data/fula_text.csv", index=False)
print(f"\n✅ Saved! Total: {len(df)} rows")
print("File: ./data/fula_text.csv")