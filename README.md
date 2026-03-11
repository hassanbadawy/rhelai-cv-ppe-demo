# RHELAI Computer Vision — PPE Detection Demo

End-to-end demo for training and running a **Personal Protective Equipment (PPE)** detection model on **Red Hat Enterprise Linux AI (RHELAI)**.

## Overview

This project walks through:

1. **Data loading & exploration** — load the Construction-PPE dataset and explore it with FiftyOne.
2. **Object detection** — add bounding-box detections using YOLOv8 / RT-DETR.
3. **Segmentation** — apply SAM2 for instance segmentation on detected PPE items.

### PPE Classes

| ID | Class | ID | Class |
|----|-------|----|-------|
| 0 | helmet | 6 | Person |
| 1 | gloves | 7 | no_helmet |
| 2 | vest | 8 | no_goggle |
| 3 | boots | 9 | no_gloves |
| 4 | goggles | 10 | no_boots |
| 5 | none | | |

## Notebooks

| # | Notebook | Description |
|---|----------|-------------|
| 1 | `01-ppe-data-load-explore.ipynb` | Load and explore the PPE dataset |
| 2 | `02_adding_detections.ipynb.ipynb` | Run object detection and visualize results |
| 3 | `03_sam2-segmentation.ipynb` | Instance segmentation with SAM2 |

Additional experimental notebooks are in the `expr/` directory.

## Dataset

Uses the [Construction-PPE](https://docs.ultralytics.com/datasets/detect/construction-ppe/) dataset (1132 train / 143 val / 141 test images). The dataset is not checked into the repo — download it or place it under `datasets/construction-ppe/`.

## Setup

```bash
pip install -r requirements.txt
```

## License

AGPL-3.0 — see [LICENSE](LICENSE) for details.
