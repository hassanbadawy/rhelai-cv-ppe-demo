# `extras/` — alternative orchestration lanes

The main workshop flow ([01–06](..)) runs training inside the workbench kernel. The [`pipelines/`](../pipelines/) directory runs it as an orchestrated Elyra DAG. This directory shows **a third option**: a single Kubeflow `PyTorchJob` submitted from the workbench as one yaml.

## Why offer three lanes?

Different audiences, same cluster. Each lane answers a different MLOps question:

| Lane | Orchestration | Strength | When to use |
|---|---|---|---|
| Workbench ([04-train-yolo.ipynb](../04-train-yolo.ipynb)) | Jupyter kernel | Interactive, live results | Teaching, exploration |
| Elyra pipeline ([pipelines/](../pipelines/)) | Multi-node Kubeflow DAG | Reproducible, scheduled | Scheduled retraining |
| **PyTorchJob ([train-pytorchjob.ipynb](train-pytorchjob.ipynb))** | **Training Operator** | **One yaml, fire-and-forget, GPU-requestable** | **Large training on cluster GPUs** |

## What you need on the cluster

- **Kubeflow Training Operator** (ships with RHOAI's `Distributed Workloads` component). `oc get crd pytorchjobs.kubeflow.org` should return non-empty.
- **`aws-connection-storage` secret** in your namespace (same one notebook 05 and the Elyra pipeline use).
- Optional: a GPU-enabled node if you want to show off `resources.limits[nvidia.com/gpu]`. The demo runs fine on CPU; training just takes longer.

## Contract

Same S3 layout as the Elyra pipeline, so downstream steps (notebook 05, pipeline node 03) can consume either output interchangeably:

```
s3://$BUCKET/$MODEL_PREFIX/$MODEL_VERSION/best.pt
                                        /data.yaml
                                        /args.yaml
                                        /results.csv
```

Run [train-pytorchjob.ipynb](train-pytorchjob.ipynb) → wait for the job to finish → proceed with [05-register-and-deploy.ipynb](../05-register-and-deploy.ipynb) to register and deploy. The registered model's `tag.run_mode` will be `workbench` (since 05 has no knowledge of where the weights came from — it just picks up the latest `best.pt`). If you want to distinguish cleanly, override `tag.run_mode` in 05's metadata dict or add a small cell that patches the Model Registry entry afterwards.
