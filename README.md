# RHELAI Computer Vision — VLM-assisted PPE Detection Demo

End-to-end workshop demo for **Red Hat Enterprise Linux AI (RHELAI)** / **Red Hat OpenShift AI (RHOAI)**: build a production PPE detector from raw, unlabeled images without hand-labeling a single bounding box.

## The story

A customer hands us a folder of construction-site photos. They want a detector for **PPE compliance** — flagging workers who are wearing (or NOT wearing) a helmet, vest, or gloves. They have no labels. We:

1. **Load** the raw images into FiftyOne so we can browse them.
2. **Annotate** all of them zero-shot with **Qwen2.5-VL**, a Vision-Language Model.
3. **Curate** the VLM labels in FiftyOne and export to YOLO format.
4. **Train** a small YOLOv8n specialist on the VLM labels.
5. **Register** the trained model in the RHOAI Model Registry.
6. **Deploy** it with KServe and **consume** the endpoint over HTTP.

No manual annotation. One VLM, one small detector, one platform.

## Notebooks

| # | Notebook | Produces |
|---|----------|----------|
| 1 | [`01-data-load-explore.ipynb`](01-data-load-explore.ipynb) | FiftyOne dataset `ppe` (40 images, no labels) |
| 2 | [`02-vlm-zero-shot-annotation.ipynb`](02-vlm-zero-shot-annotation.ipynb) | `vlm_predictions` field on all 40 samples |
| 3 | [`03-curate-and-export.ipynb`](03-curate-and-export.ipynb) | `datasets/vlm-annotated/` (YOLOv5 format) |
| 4 | [`04-train-yolo.ipynb`](04-train-yolo.ipynb) | `runs/detect/ppe-vlm/weights/best.pt` |
| 5 | [`05-register-and-deploy.ipynb`](05-register-and-deploy.ipynb) | Registered model + running `InferenceService` |
| 6 | [`06-consume-deployed-endpoint.ipynb`](06-consume-deployed-endpoint.ipynb) | Predictions on 10 held-out `datasets/ppe/images/test/` images |

Run them in order. Each notebook's final markdown cell links to the next.

## Taxonomy

Seven classes: `person`, `helmet`, `no-helmet`, `vest`, `no-vest`, `gloves`, `no-gloves`. Positives mean the worker *is* wearing the PPE; negatives are boxed around the uncovered body part. Pinned in [`data-vlm.yaml`](data-vlm.yaml) and referenced identically by the VLM prompt, the YOLO trainer, and the endpoint consumer.

## Dataset

Fifty raw JPEGs ship in this repo under [`datasets/ppe/images/`](datasets/ppe/images/) — 40 in `train/` for VLM annotation + YOLO training, 10 in `test/` held out for the final deployed-model demo, and an empty `val/` placeholder (YOLO training reuses the train split for validation). They were randomly picked from the [Construction-PPE](https://docs.ultralytics.com/datasets/detect/construction-ppe/) dataset with seed `51`. To regenerate (or pick a different seed), run:

```bash
python scripts/curate_workshop_samples.py
```

No labels come with the images — the whole point of the workshop is that the VLM produces them.

## Prerequisites

- Python 3.10+ and `pip install -r requirements.txt`
- Network access to a Qwen2.5-VL endpoint (set `VLM_ENDPOINT`) — the default in notebook 02 points at the workshop lab's OpenShift route
- For notebooks 05–06 only: an RHOAI cluster with
  - an S3-compatible data connection (env vars `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_ENDPOINT`)
  - the Model Registry component enabled (env var `MODEL_REGISTRY_URL`)
  - a YOLO-capable `ServingRuntime` (defaults to `ultralytics-yolo-runtime`)

## Repository layout

```
├── 01-data-load-explore.ipynb           # main workshop flow
├── 02-vlm-zero-shot-annotation.ipynb
├── 03-curate-and-export.ipynb
├── 04-train-yolo.ipynb
├── 05-register-and-deploy.ipynb
├── 06-consume-deployed-endpoint.ipynb
├── data-vlm.yaml                        # 7-class PPE-compliance taxonomy, source of truth
├── datasets/ppe/images/                 # 50 committed JPEGs (40 train + 10 test + empty val)
├── scripts/curate_workshop_samples.py   # reproduces the curated set from full Construction-PPE
├── pipelines/                           # Elyra/Kubeflow pipeline assets (optional)
├── samples/                             # standalone smoke-test images
├── output/                              # generated annotated images
└── expr/                                # archival / experimental notebooks (SAM2, RT-DETR, etc.)
```

## License

AGPL-3.0 — see [LICENSE](LICENSE).
