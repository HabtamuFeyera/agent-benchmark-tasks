"""Sentence embeddings with ONNX Runtime: mean pooling over the token vectors, L2-normalised."""
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

MODELS = "/app/models"
NEW_MODEL = "multilingual-e5-small"                       # in use since the re-index
OLD_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"       # kept on disk after the migration


class Embedder:
    def __init__(self, name=NEW_MODEL, models_dir=MODELS):
        self.name = name
        self.tok = Tokenizer.from_file(f"{models_dir}/{name}/tokenizer.json")
        self.tok.enable_truncation(256)
        self.tok.enable_padding()
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 2
        self.sess = ort.InferenceSession(f"{models_dir}/{name}/model.onnx", opts, providers=["CPUExecutionProvider"])

    def embed(self, texts, batch=32):
        out = []
        for i in range(0, len(texts), batch):
            enc = self.tok.encode_batch(texts[i:i + batch])
            ids = np.array([e.ids for e in enc], dtype=np.int64)
            mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
            hidden = self.sess.run(None, {"input_ids": ids, "attention_mask": mask,
                                          "token_type_ids": np.zeros_like(ids)})[0]
            v = (hidden * mask[..., None]).sum(1) / mask.sum(1, keepdims=True)
            out.append(v / np.linalg.norm(v, axis=1, keepdims=True))
        return np.vstack(out).astype(np.float32) if out else np.zeros((0, 384), np.float32)
