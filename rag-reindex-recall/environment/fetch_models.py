"""Downloads both embedding models (ONNX export, tokenizer, config) at pinned revisions and
checks every file's SHA-256, so the image is the same on every build."""
import hashlib
import os
import urllib.request

MODELS = {
    "multilingual-e5-small": ("intfloat/multilingual-e5-small", "614241f622f53c4eeff9890bdc4f31cfecc418b3", {
        "onnx/model.onnx": "ca456c06b3a9505ddfd9131408916dd79290368331e7d76bb621f1cba6bc8665",
        "tokenizer.json": "0b44a9d7b51c3c62626640cda0e2c2f70fdacdc25bbbd68038369d14ebdf4c39",
        "config.json": "69137736cab8b8903a07fe8afaafdda25aac55415a12a55d1bffa9f581abf959"}),
    "paraphrase-multilingual-MiniLM-L12-v2": ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "e8f8c211226b894fcb81acc59f3b34ba3efd5f42", {
        "onnx/model.onnx": "10f7a088420252b26caf819236ca2c9d2987afd0fc06fec7553b542a5655a05a",
        "tokenizer.json": "2c3387be76557bd40970cec13153b3bbf80407865484b209e655e5e4729076b8",
        "config.json": "6300193cb75e01cf80c96decef7187dfb33094d97cc1490b7ead6ff134476e4e"}),
}

for name, (repo, rev, files) in MODELS.items():
    os.makedirs(f"/app/models/{name}", exist_ok=True)
    for path, sha in files.items():
        dest = f"/app/models/{name}/{os.path.basename(path)}"
        urllib.request.urlretrieve(f"https://huggingface.co/{repo}/resolve/{rev}/{path}", dest)
        h = hashlib.sha256()
        with open(dest, "rb") as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                h.update(block)
        if h.hexdigest() != sha:
            raise SystemExit(f"checksum mismatch: {repo}/{path}")
    print(f"{name}: ok")
