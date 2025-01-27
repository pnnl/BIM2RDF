from pathlib import Path
dir = Path(__file__).parent 
assert(dir.exists())
del Path