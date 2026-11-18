"""Builds the vector index: every passage is prepared and embedded with the current model.

Usage: python3 indexer.py CHUNKS_JSONL OUT_VECTORS_NPY"""
import json
import sys

import numpy as np

from embedder import Embedder
from textprep import prepare


def main(chunks_path, out_path):
    chunks = [json.loads(line) for line in open(chunks_path, encoding="utf-8")]
    vectors = Embedder().embed([prepare(c["text"], "passage") for c in chunks])
    np.save(out_path, vectors)
    print(f"indexed {len(chunks)} passages")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
