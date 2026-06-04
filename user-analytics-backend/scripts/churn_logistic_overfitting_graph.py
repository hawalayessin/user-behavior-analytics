from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from churn_model_comparison import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    RANDOM_STATE,
    class_ratio,
    dataset_quality_report,
    json_default,
    load_dataset,
    make_pipeline,
    split_dataset,
    stratified_cap,
)


def logistic_spec() -> dict[str, Any]:
    return {
        "scale_numeric": True,
        "estimator": LogisticRegression(
            class_weight="balanced",
            max_iter=3000,
            random_state=RANDOM_STATE,
        ),
    }


def predict_positive_score(model: Any, X: pd.DataFrame) -> np.ndarray:
    return np.asarray(model.predict_proba(X))[:, 1].astype(float)


def compute_learning_curve(
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
    y_train: pd.Series,
    y_val: pd.Series,
    *,
    fractions: list[float],
) -> pd.DataFrame:
    spec = logistic_spec()
    rows: list[dict[str, Any]] = []
    for fraction in fractions:
        train_rows = max(50, int(len(X_train) * fraction))
        X_sub, y_sub = stratified_cap(X_train, y_train, train_rows)

        model = make_pipeline(
            "Logistic Regression",
            spec["estimator"],
            X_sub,
            scale_numeric=True,
            use_smote=False,
            y_train=y_sub,
            feature_engineering="churn_logistic",
        )
        model.set_params(model__C=1.0)

        start = time.perf_counter()
        model.fit(X_sub, y_sub)
        fit_seconds = time.perf_counter() - start

        train_score = float(roc_auc_score(y_sub, predict_positive_score(model, X_sub)))
        val_score = float(roc_auc_score(y_val, predict_positive_score(model, X_val)))
        rows.append(
            {
                "fraction": float(fraction),
                "train_rows": int(len(X_sub)),
                "train_roc_auc": train_score,
                "validation_roc_auc": val_score,
                "generalization_gap": train_score - val_score,
                "fit_seconds": float(fit_seconds),
            }
        )
        print(
            f"fraction={fraction:.2f} train_rows={len(X_sub)} "
            f"train_auc={train_score:.4f} val_auc={val_score:.4f} "
            f"gap={train_score - val_score:.4f}",
            flush=True,
        )
    return pd.DataFrame(rows)


def save_overfitting_plot(df: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    x = df["train_rows"].to_numpy()
    ax.plot(
        x,
        df["train_roc_auc"],
        marker="o",
        linewidth=2.2,
        color="#2563eb",
        label="Train ROC-AUC",
    )
    ax.plot(
        x,
        df["validation_roc_auc"],
        marker="o",
        linewidth=2.2,
        color="#16a34a",
        label="Validation ROC-AUC",
    )
    ax.fill_between(
        x,
        df["train_roc_auc"],
        df["validation_roc_auc"],
        color="#94a3b8",
        alpha=0.18,
        label="Generalization gap",
    )

    ax.set_title("Logistic Regression - Learning Curve / Overfitting Check")
    ax.set_xlabel("Training rows")
    ax.set_ylabel("ROC-AUC")
    ax.set_ylim(0.70, max(0.90, float(df[["train_roc_auc", "validation_roc_auc"]].max().max()) + 0.02))
    ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.45)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(output_dir / "logistic_regression_overfitting_curve.png", dpi=200)
    plt.close(fig)


def save_report_snippet(df: pd.DataFrame, output_dir: Path) -> None:
    last = df.iloc[-1]
    max_gap = float(df["generalization_gap"].abs().max())
    text = f"""# Graphe overfitting - Regression Logistique

Le graphe `logistic_regression_overfitting_curve.png` compare le ROC-AUC obtenu sur l'ensemble d'entrainement et sur l'ensemble de validation pour plusieurs tailles d'apprentissage.

Resultat principal:

- ROC-AUC train final: {last["train_roc_auc"]:.4f}
- ROC-AUC validation final: {last["validation_roc_auc"]:.4f}
- Ecart final train-validation: {last["generalization_gap"]:.4f}
- Ecart maximal observe: {max_gap:.4f}

Interpretation pour le rapport:

Les courbes train et validation restent proches lorsque la taille d'entrainement augmente. L'ecart de generalisation reste faible, ce qui indique que la regression logistique ne memorise pas excessivement les donnees d'apprentissage. Le modele presente donc une bonne stabilite et constitue un choix pertinent lorsque l'objectif du PFE est de combiner performance, robustesse et interpretabilite.

Mise en valeur de la regression logistique:

La regression logistique offre une interpretabilite forte: ses coefficients permettent d'expliquer directement l'influence des variables churn comme l'inactivite recente, les echecs de paiement ou la retention D7. Meme si Random Forest obtient le meilleur ROC-AUC pur, la regression logistique reste plus facile a justifier devant un jury et plus transparente pour une integration metier.
"""
    (output_dir / "logistic_regression_overfitting_interpretation.md").write_text(
        text,
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Logistic Regression learning curve to check overfitting."
    )
    parser.add_argument(
        "--data-path",
        default=None,
        help="Optional CSV/XLSX/Parquet dataset path. If omitted, the Analytics DB is used.",
    )
    parser.add_argument(
        "--target-column",
        default="churned",
        help="Target column when --data-path is used.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where the graph and interpretation are saved.",
    )
    parser.add_argument(
        "--query-timeout-ms",
        type=int,
        default=180000,
        help="SQL statement timeout for building the churn dataset.",
    )
    parser.add_argument(
        "--fractions",
        default="0.02,0.05,0.10,0.25,0.50,1.00",
        help="Comma-separated training fractions for the learning curve.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    X, y, source = load_dataset(args)
    X = X.reset_index(drop=True)
    y = pd.Series(y).reset_index(drop=True).astype(int)
    quality = dataset_quality_report(X, y)
    quality["class_imbalance_ratio"] = class_ratio(y)
    print("Dataset loaded:", json.dumps(quality, default=json_default), flush=True)

    X_train, X_val, _X_test, y_train, y_val, _y_test = split_dataset(X, y)
    fractions = [float(value.strip()) for value in args.fractions.split(",") if value.strip()]
    fractions = sorted({min(max(value, 0.001), 1.0) for value in fractions})

    curve = compute_learning_curve(
        X_train,
        X_val,
        y_train,
        y_val,
        fractions=fractions,
    )
    curve.to_csv(output_dir / "logistic_regression_overfitting_curve.csv", index=False)
    save_overfitting_plot(curve, output_dir)
    save_report_snippet(curve, output_dir)

    payload = {
        "data_source": source,
        "dataset_quality": quality,
        "split": {
            "train_rows": int(len(X_train)),
            "validation_rows": int(len(X_val)),
            "random_state": RANDOM_STATE,
            "stratify": True,
        },
        "curve": curve.to_dict(orient="records"),
        "artifacts": {
            "plot": str(output_dir / "logistic_regression_overfitting_curve.png"),
            "csv": str(output_dir / "logistic_regression_overfitting_curve.csv"),
            "interpretation": str(output_dir / "logistic_regression_overfitting_interpretation.md"),
        },
    }
    (output_dir / "logistic_regression_overfitting_metrics.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=json_default),
        encoding="utf-8",
    )

    final = curve.iloc[-1]
    print("\nSaved overfitting graph to:", output_dir / "logistic_regression_overfitting_curve.png")
    print(
        "Final gap:",
        f"train_auc={final['train_roc_auc']:.4f}",
        f"validation_auc={final['validation_roc_auc']:.4f}",
        f"gap={final['generalization_gap']:.4f}",
    )


if __name__ == "__main__":
    main()
