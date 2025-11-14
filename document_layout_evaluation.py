"""Document layout evaluation script for Qwen2.5-VL 3B on DocLayNet.

This script loads the DocLayNet test split (or any Hugging Face dataset that
provides DocLayNet-style annotations), filters both predictions and ground
truths to a predefined set of layout categories, and evaluates the model using
mAP@0.5.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image
from tqdm import tqdm

try:
    import torch
    from transformers import (
        AutoProcessor,
        Qwen2VLForConditionalGeneration,
    )
except ImportError as exc:  # pragma: no cover - surface a readable message.
    raise SystemExit(
        "Required dependencies are missing. Please install `torch` and "
        "`transformers` before running this script."
    ) from exc

try:
    from datasets import load_dataset
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "The Hugging Face `datasets` package is required. Install it with "
        "`pip install datasets`."
    ) from exc

# Target image size specified in the user instructions.
TARGET_SIZE: Tuple[int, int] = (924, 1204)

# Model and prompt configuration. The checkpoint corresponds to a LoRA adapted
# version of Qwen2.5-VL 3B published on Hugging Face.
MODEL_BASE_ID = "ChaseHan/Latex2Layout-2000-sync"
DEFAULT_PROMPT = (
    """<image>Please carefully observe the document and detect the following regions: "
    "\"title\", \"abstract\", \"heading\", \"footnote\", \"figure\", \"figure caption\", "
    "\"table\", \"table caption\", \"math\". Output each detected region's bbox coordinates in "
    "JSON format. The format of the output is: <answer>```json[{\"bbox_2d\": [x1, y1, x2, y2], \"label\": "
    "\"region name\", \"order\": \"reading order\"}]```</answer>."""
)

# Supported categories for evaluation.
TARGET_CATEGORIES: Tuple[str, ...] = (
    "title",
    "abstract",
    "heading",
    "footnote",
    "figure",
    "figure caption",
    "table",
    "table caption",
    "math",
)

_JSON_PATTERN = re.compile(r"```json(.*?)```", re.DOTALL)


@dataclass
class BoundingBox:
    """Axis aligned bounding box in the (x1, y1, x2, y2) format."""

    x1: float
    y1: float
    x2: float
    y2: float

    def __post_init__(self) -> None:
        self.x1 = float(self.x1)
        self.y1 = float(self.y1)
        self.x2 = float(self.x2)
        self.y2 = float(self.y2)

    @classmethod
    def from_xywh(cls, bbox: Sequence[float]) -> "BoundingBox":
        if len(bbox) != 4:
            raise ValueError(f"Expected 4 elements for bbox, received {len(bbox)}")
        x, y, w, h = bbox
        return cls(x, y, x + w, y + h)

    def to_array(self) -> np.ndarray:
        return np.array([self.x1, self.y1, self.x2, self.y2], dtype=np.float32)


@dataclass
class Detection:
    bbox: BoundingBox
    score: float
    label: str
    image_id: str


@dataclass
class Annotation:
    bbox: BoundingBox
    label: str


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Qwen2.5-VL 3B on DocLayNet")
    parser.add_argument(
        "--dataset",
        default="doclaynet/doclaynet",
        help="Hugging Face dataset identifier containing DocLayNet data.",
    )
    parser.add_argument(
        "--config",
        default="full",
        help="Dataset configuration name.",
    )
    parser.add_argument(
        "--split",
        default="test",
        help="Dataset split to evaluate on.",
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=1000,
        help="Number of pages to evaluate (1K requested in the instructions).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Batch size for inference. Qwen2.5-VL works best with batch size 1.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=1024,
        help="Maximum number of tokens to generate per page.",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=None,
        help="Optional cache directory for Hugging Face models and datasets.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to save the prediction JSON lines file.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device for inference (e.g. cuda, cuda:0, cpu). Defaults to auto selection.",
    )
    parser.add_argument(
        "--dtype",
        type=str,
        default="bfloat16",
        choices=("float16", "bfloat16", "float32"),
        help="Torch dtype for the model weights.",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=DEFAULT_PROMPT,
        help="Custom prompt template. Use <image> as image placeholder.",
    )
    return parser.parse_args()


def normalise_label(label: str) -> Optional[str]:
    value = label.strip().lower()
    if value in TARGET_CATEGORIES:
        return value
    return None


def resolve_example_id(example: Dict, fallback: str) -> str:
    for key in ("id", "image_id", "page_id", "file_name", "name"):
        if key in example:
            value = example[key]
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return str(int(value))
            return str(value)
    return fallback


def prepare_ground_truths(example: Dict) -> List[Annotation]:
    annotations: List[Annotation] = []
    anns = example.get("annotations") or example.get("labels") or []
    for ann in anns:
        label = ann.get("category") or ann.get("category_name") or ann.get("label")
        if not label:
            continue
        label = normalise_label(label)
        if label is None:
            continue
        bbox = ann.get("bbox") or ann.get("bbox_2d") or ann.get("bounding_box")
        if bbox is None:
            continue
        if ann.get("bbox_mode") == "xyxy":
            bb = BoundingBox(*bbox)
        else:
            bb = BoundingBox.from_xywh(bbox)
        annotations.append(Annotation(bb, label))
    return annotations


def resize_image(image: Image.Image) -> Image.Image:
    return image.resize(TARGET_SIZE, Image.BICUBIC)


def move_to_device(batch: Dict[str, torch.Tensor], device: torch.device) -> Dict[str, torch.Tensor]:
    moved = {}
    for key, value in batch.items():
        if isinstance(value, torch.Tensor):
            moved[key] = value.to(device)
        else:
            moved[key] = value
    return moved


def extract_answer_text(raw_output: str) -> Optional[str]:
    match = _JSON_PATTERN.search(raw_output)
    if match:
        return match.group(1)
    return None


def parse_predictions(
    raw_output: str, image_id: str, fallback_label: str = "heading"
) -> List[Detection]:
    answer_text = extract_answer_text(raw_output)
    if not answer_text:
        logging.warning("Unable to find JSON block in model output for %s", image_id)
        return []

    text = answer_text.strip()
    if text.startswith("["):
        json_text = text
    else:
        json_text = f"[{text}]"

    try:
        predictions = json.loads(json_text)
    except json.JSONDecodeError as exc:
        logging.warning("JSON decoding failed for %s: %s", image_id, exc)
        return []

    detections: List[Detection] = []
    for entry in predictions:
        label = entry.get("label") or entry.get("category") or fallback_label
        label_norm = normalise_label(label)
        if label_norm is None:
            continue
        bbox = entry.get("bbox_2d") or entry.get("bbox") or entry.get("bounding_box")
        if bbox is None or len(bbox) != 4:
            continue
        bbox_obj = BoundingBox(*bbox)
        score = float(entry.get("score", 1.0))
        detections.append(Detection(bbox_obj, score, label_norm, image_id))
    return detections


def compute_iou(box1: BoundingBox, box2: BoundingBox) -> float:
    a = box1.to_array()
    b = box2.to_array()
    x_left = max(a[0], b[0])
    y_top = max(a[1], b[1])
    x_right = min(a[2], b[2])
    y_bottom = min(a[3], b[3])
    if x_right <= x_left or y_bottom <= y_top:
        return 0.0
    intersection = (x_right - x_left) * (y_bottom - y_top)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - intersection
    if union <= 0:
        return 0.0
    return intersection / union


def compute_average_precision(
    detections: List[Detection],
    ground_truths: Dict[str, List[Annotation]],
    iou_threshold: float,
) -> float:
    if not detections:
        return 0.0

    detections = sorted(detections, key=lambda det: det.score, reverse=True)
    tp = np.zeros(len(detections), dtype=np.float32)
    fp = np.zeros(len(detections), dtype=np.float32)

    matched: Dict[str, List[bool]] = {
        image_id: [False] * len(ground_truths.get(image_id, []))
        for image_id in ground_truths
    }

    total_gts = sum(len(ground_truths[img]) for img in ground_truths)
    if total_gts == 0:
        return 0.0

    for idx, det in enumerate(detections):
        gts = ground_truths.get(det.image_id, [])
        ious = [compute_iou(det.bbox, ann.bbox) for ann in gts]
        if not ious:
            fp[idx] = 1.0
            continue
        best_iou = max(ious)
        best_gt = int(np.argmax(ious))
        if best_iou >= iou_threshold and not matched[det.image_id][best_gt]:
            tp[idx] = 1.0
            matched[det.image_id][best_gt] = True
        else:
            fp[idx] = 1.0

    cumulative_tp = np.cumsum(tp)
    cumulative_fp = np.cumsum(fp)
    recalls = cumulative_tp / total_gts
    precisions = cumulative_tp / np.maximum(cumulative_tp + cumulative_fp, np.finfo(float).eps)

    # Standard VOC-style interpolation.
    ap = 0.0
    for t in np.linspace(0, 1, 11):
        precisions_at_recall = precisions[recalls >= t]
        p = max(precisions_at_recall) if precisions_at_recall.size > 0 else 0.0
        ap += p / 11.0
    return ap


def evaluate_map50(
    detections: Iterable[Detection],
    ground_truths: Dict[str, List[Annotation]],
) -> Dict[str, float]:
    per_label: Dict[str, List[Detection]] = {label: [] for label in TARGET_CATEGORIES}
    per_label_gt: Dict[str, Dict[str, List[Annotation]]] = {
        label: {} for label in TARGET_CATEGORIES
    }

    for det in detections:
        per_label.setdefault(det.label, []).append(det)

    for image_id, ann_list in ground_truths.items():
        for ann in ann_list:
            per_label_gt.setdefault(ann.label, {}).setdefault(image_id, []).append(ann)

    map_scores: Dict[str, float] = {}
    aps = []
    for label in TARGET_CATEGORIES:
        label_dets = per_label.get(label, [])
        label_gts = per_label_gt.get(label, {})
        ap = compute_average_precision(label_dets, label_gts, iou_threshold=0.5)
        map_scores[label] = ap
        aps.append(ap)

    map_scores["mAP50"] = float(np.mean(aps) if aps else 0.0)
    return map_scores


def load_model(cache_dir: Optional[str], device: Optional[str], dtype: str):
    torch_dtype = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }[dtype]

    processor = AutoProcessor.from_pretrained(MODEL_BASE_ID, cache_dir=cache_dir)
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        MODEL_BASE_ID,
        torch_dtype=torch_dtype,
        device_map="auto" if device is None else None,
        cache_dir=cache_dir,
    )
    if device is not None:
        model = model.to(device)
    model.eval()
    return processor, model


def run_inference(
    processor,
    model,
    dataset,
    prompt: str,
    max_new_tokens: int,
    batch_size: int,
) -> List[Detection]:
    detections: List[Detection] = []
    device = next(model.parameters()).device

    for idx in tqdm(range(0, len(dataset), batch_size), desc="Running inference"):
        batch_examples = dataset[idx : idx + batch_size]
        images = [resize_image(example["image"].convert("RGB")) for example in batch_examples]
        inputs = processor(text=[prompt] * len(images), images=images, return_tensors="pt")
        inputs = move_to_device(inputs, device)
        with torch.no_grad():
            output_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
        generated = processor.batch_decode(output_ids, skip_special_tokens=False)
        for local_idx, (example, text) in enumerate(zip(batch_examples, generated)):
            image_id = resolve_example_id(example, fallback=str(idx + local_idx))
            detections.extend(parse_predictions(text, image_id))
    return detections


def main() -> None:
    args = parse_arguments()

    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

    logging.info(
        "Loading dataset %s (config=%s, split=%s, num_samples=%s)",
        args.dataset,
        args.config,
        args.split,
        args.num_samples,
    )

    split = args.split
    if args.num_samples:
        split = f"{split}[:{args.num_samples}]"
    dataset = load_dataset(args.dataset, args.config, split=split, cache_dir=args.cache_dir)

    logging.info("Preparing ground truth annotations")
    ground_truths: Dict[str, List[Annotation]] = {}
    for index, example in enumerate(tqdm(dataset, desc="Preparing annotations")):
        annotations = prepare_ground_truths(example)
        if annotations:
            image_id = resolve_example_id(example, fallback=str(index))
            ground_truths[image_id] = annotations

    logging.info("Loading model %s", MODEL_BASE_ID)
    processor, model = load_model(args.cache_dir, args.device, args.dtype)

    logging.info("Running inference")
    detections = run_inference(
        processor=processor,
        model=model,
        dataset=dataset,
        prompt=args.prompt,
        max_new_tokens=args.max_new_tokens,
        batch_size=args.batch_size,
    )

    logging.info("Computing mAP@0.5")
    metrics = evaluate_map50(detections, ground_truths)
    for label, score in metrics.items():
        logging.info("%s: %.4f", label, score)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            for det in detections:
                f.write(
                    json.dumps(
                        {
                            "image_id": det.image_id,
                            "label": det.label,
                            "bbox_2d": [det.bbox.x1, det.bbox.y1, det.bbox.x2, det.bbox.y2],
                            "score": det.score,
                        }
                    )
                    + "\n"
                )
        logging.info("Predictions saved to %s", output_path)

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
