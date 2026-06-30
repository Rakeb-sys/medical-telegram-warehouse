"""
YOLO Object Detection for Telegram Channel Images
===================================================
Scans downloaded images, runs YOLOv8 detection, classifies images,
and saves results to CSV.

Usage:
    python src/yolo_detect.py --images data/raw/images --output data/yolo_results.csv
    python src/yolo_detect.py --demo   # Generate sample detection results
"""

import os
import csv
import argparse
import random
import logging
from pathlib import Path

logger = logging.getLogger("yolo_detect")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

PERSON_CLASSES = {"person"}
PRODUCT_CLASSES = {"bottle", "cup", "bowl", "vase", "handbag", "suitcase", "backpack"}


def classify_image(detected_objects: list) -> str:
    class_names = {obj["class"] for obj in detected_objects}
    has_person = bool(class_names & PERSON_CLASSES)
    has_product = bool(class_names & PRODUCT_CLASSES)

    if has_person and has_product:
        return "promotional"
    elif has_product and not has_person:
        return "product_display"
    elif has_person and not has_product:
        return "lifestyle"
    return "other"


def run_detection(images_dir: str, output_csv: str):
    from ultralytics import YOLO

    model = YOLO("yolov8n.pt")
    results_rows = []

    for channel_dir in sorted(Path(images_dir).iterdir()):
        if not channel_dir.is_dir():
            continue

        channel_name = channel_dir.name
        image_files = sorted(channel_dir.glob("*.jpg"))
        logger.info(f"Processing {len(image_files)} images from {channel_name}")

        for img_path in image_files:
            message_id = img_path.stem

            try:
                results = model(str(img_path), verbose=False)
            except Exception as e:
                logger.warning(f"Detection failed for {img_path}: {e}")
                continue

            detections = []
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    cls_name = model.names[cls_id]
                    conf = float(box.conf[0])
                    detections.append({"class": cls_name, "confidence": conf})

            category = classify_image(detections)

            if detections:
                top = max(detections, key=lambda d: d["confidence"])
                results_rows.append({
                    "image_path": str(img_path),
                    "message_id": message_id,
                    "channel_name": channel_name,
                    "detected_class": top["class"],
                    "confidence": round(top["confidence"], 4),
                    "image_category": category,
                })
            else:
                results_rows.append({
                    "image_path": str(img_path),
                    "message_id": message_id,
                    "channel_name": channel_name,
                    "detected_class": "none",
                    "confidence": 0.0,
                    "image_category": "other",
                })

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "image_path", "message_id", "channel_name",
            "detected_class", "confidence", "image_category",
        ])
        writer.writeheader()
        writer.writerows(results_rows)

    logger.info(f"Saved {len(results_rows)} detection results to {output_csv}")
    return results_rows


def run_demo_detection(images_dir: str, output_csv: str):
    """Generate realistic detection results without running YOLO."""
    logger.info("[DEMO] Generating sample YOLO detection results")

    demo_classes = [
        ("bottle", "product_display", 0.85),
        ("person", "lifestyle", 0.92),
        ("person", "promotional", 0.88),
        ("cup", "product_display", 0.76),
        ("handbag", "product_display", 0.71),
        ("bottle", "product_display", 0.90),
        ("person", "promotional", 0.94),
        ("vase", "product_display", 0.65),
        ("none", "other", 0.0),
        ("person", "lifestyle", 0.87),
    ]

    results_rows = []
    for channel_dir in sorted(Path(images_dir).iterdir()):
        if not channel_dir.is_dir():
            continue
        channel_name = channel_dir.name
        image_files = sorted(channel_dir.glob("*.jpg"))

        for img_path in image_files:
            cls, cat, base_conf = random.choice(demo_classes)
            conf = round(base_conf + random.uniform(-0.1, 0.05), 4) if base_conf > 0 else 0.0
            conf = max(0.0, min(conf, 1.0))

            results_rows.append({
                "image_path": str(img_path),
                "message_id": img_path.stem,
                "channel_name": channel_name,
                "detected_class": cls,
                "confidence": conf,
                "image_category": cat,
            })

    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "image_path", "message_id", "channel_name",
            "detected_class", "confidence", "image_category",
        ])
        writer.writeheader()
        writer.writerows(results_rows)

    logger.info(f"[DEMO] Saved {len(results_rows)} detection results to {output_csv}")
    return results_rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLO object detection on scraped images")
    parser.add_argument("--images", default="data/raw/images")
    parser.add_argument("--output", default="data/yolo_results.csv")
    parser.add_argument("--demo", action="store_true",
                        help="Generate sample results without running YOLO model")
    args = parser.parse_args()

    if args.demo:
        run_demo_detection(args.images, args.output)
    else:
        run_detection(args.images, args.output)
