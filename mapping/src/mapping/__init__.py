from pathlib import Path
mapping_dir = Path(__file__).parent.parent.parent
assert(mapping_dir.name == 'mapping')
