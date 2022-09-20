from pathlib import Path

print(Path(__file__).parent / "src") # this will work with the relative path

# There's 2 files, when hoi4 can't open autosave.hoi4, he will generate autosave_temp.hoi4