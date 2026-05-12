from datasets import load_dataset, Features, Value, Audio

features = Features(
    {
        "audio": Audio(),
        "transcription": Value("string"),
    }
)

dataset = load_dataset(
    "csv",
    data_files="metadata.csv",
    features=features,
)

dataset.push_to_hub("Abdelrahman2922/Egyptian-Arabic-synthetic-stt")
