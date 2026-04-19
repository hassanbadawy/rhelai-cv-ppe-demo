# RHOAI pipeline — the production parallel of notebooks 02–05

The numbered notebooks in the repo root teach the workshop story interactively. This directory rebuilds the same flow as a **Kubeflow Pipeline** (via Elyra) so the customer sees how that story runs unattended on their cluster.

## DAG

```
                ┌────────────────────┐       ┌────────────────┐       ┌──────────────────────┐
  raw images ──▶│  01 annotate (VLM) │──▶ S3 │ 02 train YOLO  │──▶ S3 │ 03 register + deploy │──▶ endpoint.txt
                └────────────────────┘       └────────────────┘       └──────────────────────┘
```

Each node is a plain notebook that runs inside a Kubeflow pod spawned from the Red Hat runtime image. Data flows between nodes via **S3**, not FiftyOne or shared filesystems — this is deliberate: every node is idempotent and restartable.

## S3 contract

One bucket (defaults to `storage` via the `aws-connection-storage` data connection); everything is under configurable prefixes.

| Step | Reads | Writes |
|------|-------|--------|
| 01 annotate  | `s3://$BUCKET/$RAW_PREFIX/train/*.jpg` | `s3://$BUCKET/$DATASET_PREFIX/{images,labels}/train/*`, `dataset.yaml` |
| 02 train     | `s3://$BUCKET/$DATASET_PREFIX/…`       | `s3://$BUCKET/$MODEL_PREFIX/$MODEL_VERSION/best.pt`, `data.yaml` |
| 03 deploy    | `s3://$BUCKET/$MODEL_PREFIX/$MODEL_VERSION/` | Model Registry entry + KServe `InferenceService` |

Defaults (overrideable per node in the Elyra manifest):

| Env var | Default |
|---------|---------|
| `RAW_PREFIX` | `workshop-data` |
| `DATASET_PREFIX` | `workshop-dataset` |
| `MODEL_PREFIX` | `models/ppe-yolov8n-vlm` |
| `MODEL_VERSION` | `v1` |
| `MODEL_NAME` | `ppe-yolov8n-vlm` |

## Cluster prerequisites

- **Data connection** named `aws-connection-storage` (RHOAI UI: *Data Science Projects → Data connections*). This secret supplies `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_ENDPOINT`, `AWS_DEFAULT_REGION`, `AWS_S3_BUCKET`.
- **VLM endpoint** reachable from the cluster — set `VLM_ENDPOINT` on the `annotate-node` (optionally with a `vlm-credentials` secret holding `token`).
- **Model Registry** secret named `model-registry-access` with keys `url`, `token`, and optional `port`.
- **KServe serving runtime** that can load an Ultralytics `.pt`. The manifest defaults to `ultralytics-yolo-runtime` in namespace `ppe-detection-cv`; change via env vars on `deploy-node` if your lab differs.

## Bootstrap (one-time, per workshop cluster)

The pipeline reads raw images from S3, so push the 40 committed workshop images up first:

```bash
# From the repo root, inside a pod or laptop with the cluster creds loaded:
aws --endpoint-url "$AWS_S3_ENDPOINT" s3 sync \
    datasets/ppe/images/train/ s3://$AWS_S3_BUCKET/workshop-data/train/
```

After that, open `full-lifecycle.pipeline` in the Elyra visual editor (RHOAI workbench → *File → Open* → the `.pipeline` file), hit *Run*, and watch the three pods go green.

## Why this mirrors notebooks, not replaces them

- The **notebooks** are the teaching tool — Gradio, FiftyOne app, and inline previews live there. They run in a single workbench kernel, with humans in the loop.
- The **pipeline** is the productionization — no humans, no UI, idempotent nodes, artifact-driven contracts, scheduled/triggered execution. Dropping FiftyOne between nodes is intentional.

If the VLM, training, or deploy step needs a schema change, update **both** places — they intentionally duplicate the prompt, training hyperparams, and InferenceService manifest.
