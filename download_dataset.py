import kagglehub
import os
import shutil

# Project data folder
data_dir = os.path.join(os.getcwd(), "data")
os.makedirs(data_dir, exist_ok=True)

print("Downloading Kaggle Toxic Comment Classification Challenge...")

# Download competition files
path = kagglehub.competition_download(
    "jigsaw-toxic-comment-classification-challenge"
)

print("\nDownloaded competition files to:")
print(path)

# Copy downloaded files into our project's data folder
for filename in os.listdir(path):
    source = os.path.join(path, filename)
    destination = os.path.join(data_dir, filename)

    if os.path.isfile(source):
        shutil.copy2(source, destination)

print("\nDataset copied to:")
print(data_dir)

print("\nFiles:")
for filename in os.listdir(data_dir):
    print(" -", filename)
    