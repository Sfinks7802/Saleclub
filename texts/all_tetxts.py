from pathlib import Path

def read_file(filename, Path=Path):
    return open(Path(__file__).with_name(filename), encoding='UTF-8').read()