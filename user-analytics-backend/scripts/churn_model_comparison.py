from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


RANDOM_STATE = 42
TEST_SIZE = 0.15
VALIDATION_SIZE = 0.15
TRAIN_SIZE = 0.70
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports" / "churn_model_comparison"


INTERPRETABILITY = {
    "Logistic Regression": {"label": "Forte", "score": 1.0},
    "Random Forest": {"label": "Moyenne", "score": 0.7},
    "XGBoost": {"label": "Moyenne", "score": 0.6},
    "SVM (RBF)": {"label": "Faible", "score": 0.25},
}


@dataclass(frozen=True)
class ExperimentResult:
    algorithm: str
    variant: str
    estimator: Any
    threshold: float
    best_params: dict[str, Any]
    validation_score: float
    metrics: dict[str, Any]
    y_test: np.ndarray
    y_proba: np.ndarray
    y_pred: np.ndarray


def require_dependencies() -> None:
    missing: list[str] = []
    required = [
        ("sklearn", "scikit-learn"),
        ("matplotlib", "matplotlib"),
        ("xgboost", "xgboost"),
    ]
    optional = [("imblearn", "imbalanced-learn")]

    for module_name, package_name in required + optional:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(package_name)

    if missing:
        install_line = "python -m pip install " + " ".join(sorted(set(missing)))
        raise SystemExit(
            "Missing ML dependencies: "
            + ", ".join(sorted(set(missing)))
            + f"\nInstall them with: {install_line}"
        )


def json_default(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    return str(value)


def slugify(value: str) -> str:
    return (
        value.lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "plus")
        .replace("/", "_")
    )


def read_csv_or_excel(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported dataset format: {path.suffix}")


def load_dataset(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.Series, dict[str, Any]]:
    if args.data_path:
        data_path = Path(args.data_path).resolve()
        if not data_path.exists():
            raise FileNotFoundError(f"Dataset not found: {data_path}")

        df = read_csv_or_excel(data_path)
        target_column = args.target_column or "churned"
        if target_column not in df.columns:
            raise ValueError(
                f"Target column '{target_column}' not found. "
                f"Available columns: {', '.join(df.columns)}"
            )
        y = normalize_target(df[target_column])
        X = df.drop(columns=[target_column])
        source = {"type": "file", "path": str(data_path), "target_column": target_column}
        return X, y, source

    from app.core.database import SessionLocal
    from ml_models.churn_predictor import ChurnPredictor

    predictor = ChurnPredictor(query_timeout_ms=args.query_timeout_ms)
    db = SessionLocal()
    try:
        X, y = predictor.generate_training_dataset(db)
    finally:
        db.close()

    source = {
        "type": "analytics_db",
        "builder": "ml_models.churn_predictor.ChurnPredictor.generate_training_dataset",
        "features": list(X.columns),
        "target_column": "churned",
    }
    return X, y.astype(int), source


def normalize_target(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.astype(int)
    if pd.api.types.is_numeric_dtype(series):
        values = series.fillna(0).astype(float)
        unique_values = set(values.dropna().unique().tolist())
        if unique_values <= {0.0, 1.0}:
            return values.astype(int)
        return (values > 0).astype(int)

    normalized = series.astype(str).str.strip().str.lower()
    positives = {"1", "true", "yes", "y", "churn", "churned", "cancelled", "canceled"}
    negatives = {"0", "false", "no", "n", "active", "retained", "not_churned"}
    unknown = sorted(set(normalized.unique()) - positives - negatives)
    if unknown:
        raise ValueError(
            "Cannot normalize target values automatically. Unknown labels: "
            + ", ".join(map(str, unknown[:10]))
        )
    return normalized.isin(positives).astype(int)


def dataset_quality_report(X: pd.DataFrame, y: pd.Series) -> dict[str, Any]:
    return {
        "n_rows": int(len(X)),
        "n_features": int(X.shape[1]),
        "n_positive": int((y == 1).sum()),
        "n_negative": int((y == 0).sum()),
        "positive_rate": float(y.mean()) if len(y) else 0.0,
        "missing_values_total": int(X.isna().sum().sum()),
        "numeric_features": int(len(X.select_dtypes(include=[np.number, "bool"]).columns)),
        "categorical_features": int(
            len(X.select_dtypes(exclude=[np.number, "bool"]).columns)
        ),
    }


def split_dataset(
    X: pd.DataFrame, y: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    from sklearn.model_selection import train_test_split

    if y.nunique() < 2:
        raise ValueError("Dataset contains a single class. Need churned=0 and churned=1.")
    min_class_count = int(y.value_counts().min())
    if min_class_count < 3:
        raise ValueError(
            "Not enough samples in the minority class for a 70/15/15 stratified split. "
            f"Minority class count: {min_class_count}"
        )

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=(VALIDATION_SIZE + TEST_SIZE),
        random_state=RANDOM_STATE,
        stratify=y,
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=TEST_SIZE / (VALIDATION_SIZE + TEST_SIZE),
        random_state=RANDOM_STATE,
        stratify=y_temp,
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


def stratified_cap(
    X: pd.DataFrame,
    y: pd.Series,
    max_rows: int,
) -> tuple[pd.DataFrame, pd.Series]:
    if max_rows <= 0 or len(X) <= max_rows:
        return X, y

    from sklearn.model_selection import train_test_split

    _, X_sample, _, y_sample = train_test_split(
        X,
        y,
        test_size=max_rows,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    return X_sample.reset_index(drop=True), y_sample.reset_index(drop=True)


def make_preprocessor(X: pd.DataFrame, *, scale_numeric: bool):
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    numeric_columns = X.select_dtypes(include=[np.number, "bool"]).columns.tolist()
    categorical_columns = [col for col in X.columns if col not in numeric_columns]

    numeric_steps: list[tuple[str, Any]] = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    transformers: list[tuple[str, Any, list[str]]] = []
    if numeric_columns:
        transformers.append(("num", Pipeline(numeric_steps), numeric_columns))
    if categorical_columns:
        transformers.append(
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "encoder",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        ),
                    ]
                ),
                categorical_columns,
            )
        )

    if not transformers:
        raise ValueError("No usable feature columns found.")

    return ColumnTransformer(transformers=transformers, remainder="drop")


def class_ratio(y: pd.Series) -> float:
    counts = y.value_counts()
    if len(counts) < 2 or counts.min() == 0:
        return math.inf
    return float(counts.max() / counts.min())


def smote_is_pertinent(y_train: pd.Series, mode: str) -> bool:
    if mode == "never":
        return False
    min_class_count = int(y_train.value_counts().min())
    if min_class_count < 6:
        return False
    if mode == "always":
        return True
    return class_ratio(y_train) >= 1.5


def make_pipeline(
    algorithm: str,
    estimator: Any,
    X_train: pd.DataFrame,
    *,
    scale_numeric: bool,
    use_smote: bool,
    y_train: pd.Series,
    feature_engineering: str | None = None,
):
    from sklearn.base import clone
    from sklearn.pipeline import Pipeline

    estimator = clone(estimator)
    if use_smote:
        if hasattr(estimator, "class_weight"):
            estimator.set_params(class_weight=None)
        if hasattr(estimator, "scale_pos_weight"):
            estimator.set_params(scale_pos_weight=1.0)

    if feature_engineering == "churn_logistic":
        from sklearn.preprocessing import StandardScaler
        from ml_models.churn_predictor import ChurnLogisticFeatureEngineer

        steps: list[tuple[str, Any]] = [
            ("features", ChurnLogisticFeatureEngineer(X_train.columns.tolist())),
            ("scaler", StandardScaler()),
        ]
    else:
        preprocessor = make_preprocessor(X_train, scale_numeric=scale_numeric)
        steps = [("preprocess", preprocessor)]

    if use_smote:
        from imblearn.over_sampling import SMOTE
        from imblearn.pipeline import Pipeline as ImbPipeline

        minority_count = int(y_train.value_counts().min())
        k_neighbors = max(1, min(5, minority_count - 1))
        steps.append(("smote", SMOTE(random_state=RANDOM_STATE, k_neighbors=k_neighbors)))
        steps.append(("model", estimator))
        return ImbPipeline(steps)

    steps.append(("model", estimator))
    return Pipeline(steps)


def model_specs(y_train: pd.Series) -> dict[str, dict[str, Any]]:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from xgboost import XGBClassifier

    counts = y_train.value_counts()
    neg = int(counts.get(0, 1))
    pos = int(counts.get(1, 1))
    scale_pos_weight = neg / pos if pos else 1.0

    return {
        "Logistic Regression": {
            "scale_numeric": True,
            "feature_engineering": "churn_logistic",
            "estimator": LogisticRegression(
                class_weight="balanced",
                max_iter=3000,
                random_state=RANDOM_STATE,
            ),
            "param_grid": {
                "model__C": [0.1, 1.0, 10.0],
            },
        },
        "Random Forest": {
            "scale_numeric": False,
            "estimator": RandomForestClassifier(
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            "param_grid": {
                "model__n_estimators": [150],
                "model__max_depth": [None, 10],
                "model__min_samples_leaf": [1, 3],
            },
        },
        "XGBoost": {
            "scale_numeric": False,
            "estimator": XGBClassifier(
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=RANDOM_STATE,
                n_jobs=-1,
                tree_method="hist",
                scale_pos_weight=scale_pos_weight,
            ),
            "param_grid": {
                "model__n_estimators": [120],
                "model__max_depth": [3, 5],
                "model__learning_rate": [0.1],
                "model__subsample": [0.9],
            },
        },
        "SVM (RBF)": {
            "scale_numeric": True,
            "estimator": SVC(
                kernel="rbf",
                probability=False,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            ),
            "param_grid": {
                "model__C": [1.0, 10.0],
                "model__gamma": ["scale"],
            },
        },
    }


def iter_param_grid(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = list(grid)
    values = [grid[key] for key in keys]
    return [dict(zip(keys, combo)) for combo in itertools.product(*values)]


def predict_proba_positive(model: Any, X: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        return np.asarray(proba)[:, 1].astype(float)
    if hasattr(model, "decision_function"):
        return np.asarray(model.decision_function(X)).astype(float)
    raise TypeError("Estimator does not expose predict_proba or decision_function.")


def validation_score(y_true: pd.Series, y_proba: np.ndarray) -> float:
    from sklearn.metrics import average_precision_score, roc_auc_score

    if y_true.nunique() < 2:
        return float(average_precision_score(y_true, y_proba))
    return float(roc_auc_score(y_true, y_proba))


def select_threshold(y_true: pd.Series, y_proba: np.ndarray) -> tuple[float, list[dict[str, float]]]:
    from sklearn.metrics import precision_recall_fscore_support

    if float(np.nanmin(y_proba)) >= 0.0 and float(np.nanmax(y_proba)) <= 1.0:
        candidates = np.unique(np.round(np.linspace(0.05, 0.95, 91), 3))
    else:
        candidates = np.unique(np.quantile(y_proba, np.linspace(0.05, 0.95, 91)))
    rows: list[dict[str, float]] = []
    y_true_arr = np.asarray(y_true).astype(int)
    positive_rate = float(np.mean(y_true_arr)) if len(y_true_arr) else 0.0
    majority_baseline_accuracy = float(max(positive_rate, 1.0 - positive_rate))
    accuracy_floor = max(0.70, majority_baseline_accuracy - 0.08)

    for threshold in candidates:
        y_pred = (y_proba >= threshold).astype(int)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true_arr,
            y_pred,
            average="binary",
            zero_division=0,
        )
        row = {
            "threshold": float(threshold),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "accuracy": float((y_pred == y_true_arr).mean()),
        }
        rows.append(row)

    eligible = [row for row in rows if row["accuracy"] >= accuracy_floor]
    if eligible:
        best = max(eligible, key=lambda row: (row["f1"], row["recall"], row["accuracy"]))
    else:
        best = max(rows, key=lambda row: (row["accuracy"], row["f1"], row["recall"]))

    return float(best["threshold"]), rows


def compute_metrics(
    y_true: pd.Series,
    y_proba: np.ndarray,
    threshold: float,
    *,
    train_time_seconds: float,
    inference_time_seconds: float,
    tuning_time_seconds: float,
) -> tuple[dict[str, Any], np.ndarray]:
    from sklearn.metrics import (
        accuracy_score,
        average_precision_score,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    y_pred = (y_proba >= threshold).astype(int)
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)) if y_true.nunique() > 1 else None,
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "training_time_seconds": float(train_time_seconds),
        "inference_time_seconds": float(inference_time_seconds),
        "tuning_time_seconds": float(tuning_time_seconds),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]).astype(int).tolist(),
    }
    return metrics, y_pred


def run_single_experiment(
    algorithm: str,
    spec: dict[str, Any],
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_val: pd.Series,
    y_test: pd.Series,
    *,
    use_smote: bool,
    svm_max_train_rows: int,
) -> ExperimentResult:
    fit_X_train = X_train
    fit_y_train = y_train
    if algorithm == "SVM (RBF)" and svm_max_train_rows > 0 and len(X_train) > svm_max_train_rows:
        fit_X_train, fit_y_train = stratified_cap(X_train, y_train, svm_max_train_rows)
        print(
            f"SVM (RBF): using stratified training cap "
            f"{len(fit_X_train)}/{len(X_train)} rows for tractable RBF fitting.",
            flush=True,
        )

    best_model = None
    best_params: dict[str, Any] = {}
    best_score = -math.inf
    best_train_time = 0.0
    tuning_start = time.perf_counter()

    for params in iter_param_grid(spec["param_grid"]):
        model = make_pipeline(
            algorithm,
            spec["estimator"],
            fit_X_train,
            scale_numeric=bool(spec["scale_numeric"]),
            use_smote=use_smote,
            y_train=fit_y_train,
            feature_engineering=spec.get("feature_engineering"),
        )
        model.set_params(**params)
        fit_start = time.perf_counter()
        model.fit(fit_X_train, fit_y_train)
        fit_time = time.perf_counter() - fit_start
        val_proba = predict_proba_positive(model, X_val)
        score = validation_score(y_val, val_proba)
        if score > best_score:
            best_score = score
            best_model = model
            best_params = dict(params)
            best_train_time = fit_time

    tuning_time = time.perf_counter() - tuning_start
    if best_model is None:
        raise RuntimeError(f"No model could be trained for {algorithm}.")

    val_proba = predict_proba_positive(best_model, X_val)
    threshold, threshold_candidates = select_threshold(y_val, val_proba)

    inference_start = time.perf_counter()
    test_proba = predict_proba_positive(best_model, X_test)
    inference_time = time.perf_counter() - inference_start
    metrics, y_pred = compute_metrics(
        y_test,
        test_proba,
        threshold,
        train_time_seconds=best_train_time,
        inference_time_seconds=inference_time,
        tuning_time_seconds=tuning_time,
    )
    metrics["threshold"] = threshold
    metrics["threshold_candidates"] = threshold_candidates
    metrics["training_rows_used"] = int(len(fit_X_train))
    metrics["training_rows_available"] = int(len(X_train))

    return ExperimentResult(
        algorithm=algorithm,
        variant="SMOTE" if use_smote else "class_weight/scale_pos_weight",
        estimator=best_model,
        threshold=threshold,
        best_params=best_params,
        validation_score=float(best_score),
        metrics=metrics,
        y_test=np.asarray(y_test).astype(int),
        y_proba=np.asarray(test_proba).astype(float),
        y_pred=np.asarray(y_pred).astype(int),
    )


def run_experiments(
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_val: pd.Series,
    y_test: pd.Series,
    *,
    smote_mode: str,
    svm_max_train_rows: int,
) -> list[ExperimentResult]:
    specs = model_specs(y_train)
    include_smote = smote_is_pertinent(y_train, smote_mode)

    results: list[ExperimentResult] = []
    for algorithm, spec in specs.items():
        print(f"Training {algorithm} with class weights...", flush=True)
        results.append(
            run_single_experiment(
                algorithm,
                spec,
                X_train,
                X_val,
                X_test,
                y_train,
                y_val,
                y_test,
                use_smote=False,
                svm_max_train_rows=svm_max_train_rows,
            )
        )
        if include_smote:
            print(f"Training {algorithm} with SMOTE...", flush=True)
            results.append(
                run_single_experiment(
                    algorithm,
                    spec,
                    X_train,
                    X_val,
                    X_test,
                    y_train,
                    y_val,
                    y_test,
                    use_smote=True,
                    svm_max_train_rows=svm_max_train_rows,
                )
            )
    return results


def results_dataframe(results: list[ExperimentResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        interp = INTERPRETABILITY[result.algorithm]
        row = {
            "algorithm": result.algorithm,
            "variant": result.variant,
            "roc_auc": result.metrics["roc_auc"],
            "pr_auc": result.metrics["pr_auc"],
            "accuracy": result.metrics["accuracy"],
            "precision": result.metrics["precision"],
            "recall": result.metrics["recall"],
            "f1_score": result.metrics["f1_score"],
            "training_time_seconds": result.metrics["training_time_seconds"],
            "inference_time_seconds": result.metrics["inference_time_seconds"],
            "tuning_time_seconds": result.metrics["tuning_time_seconds"],
            "threshold": result.threshold,
            "validation_score": result.validation_score,
            "interpretability": interp["label"],
            "interpretability_score": interp["score"],
            "best_params": json.dumps(result.best_params, default=json_default),
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    df["performance_score"] = 0.6 * df["roc_auc"].fillna(0) + 0.4 * df["f1_score"].fillna(0)
    max_time = max(float(df["training_time_seconds"].max()), 1e-12)
    df["time_score"] = 1.0 - (df["training_time_seconds"] / max_time).clip(0, 1)
    df["compromise_score"] = (
        0.62 * df["performance_score"]
        + 0.28 * df["interpretability_score"]
        + 0.10 * df["time_score"]
    )
    return df.sort_values(["roc_auc", "f1_score"], ascending=False).reset_index(drop=True)


def best_result_by_name(results: list[ExperimentResult], algorithm: str, variant: str) -> ExperimentResult:
    for result in results:
        if result.algorithm == algorithm and result.variant == variant:
            return result
    raise KeyError(f"Result not found: {algorithm} / {variant}")


def identify_best_models(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    best_roc = df.sort_values(["roc_auc", "f1_score"], ascending=False).iloc[0]
    best_f1 = df.sort_values(["f1_score", "roc_auc"], ascending=False).iloc[0]
    best_compromise = df.sort_values(["compromise_score", "roc_auc"], ascending=False).iloc[0]

    def pack(row: pd.Series) -> dict[str, Any]:
        return {
            "algorithm": row["algorithm"],
            "variant": row["variant"],
            "roc_auc": float(row["roc_auc"]),
            "f1_score": float(row["f1_score"]),
            "pr_auc": float(row["pr_auc"]),
            "interpretability": row["interpretability"],
            "compromise_score": float(row["compromise_score"]),
        }

    return {
        "best_by_roc_auc": pack(best_roc),
        "best_by_f1_score": pack(best_f1),
        "best_by_performance_interpretability": pack(best_compromise),
    }


def save_plots(
    output_dir: Path,
    results: list[ExperimentResult],
    best: ExperimentResult,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay, PrecisionRecallDisplay, RocCurveDisplay

    plots_dir = output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    for result in results:
        fig, ax = plt.subplots(figsize=(5, 4))
        ConfusionMatrixDisplay.from_predictions(
            result.y_test,
            result.y_pred,
            labels=[0, 1],
            display_labels=["No churn", "Churn"],
            cmap="Blues",
            ax=ax,
            colorbar=False,
        )
        ax.set_title(f"{result.algorithm} - {result.variant}")
        fig.tight_layout()
        fig.savefig(plots_dir / f"{slugify(result.algorithm)}_{slugify(result.variant)}_confusion_matrix.png", dpi=180)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    for result in results:
        label = f"{result.algorithm} ({result.variant})"
        RocCurveDisplay.from_predictions(result.y_test, result.y_proba, name=label, ax=ax)
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1)
    ax.set_title("ROC Curves - Churn Model Comparison")
    fig.tight_layout()
    fig.savefig(output_dir / "roc_curve.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    for result in results:
        label = f"{result.algorithm} ({result.variant})"
        PrecisionRecallDisplay.from_predictions(result.y_test, result.y_proba, name=label, ax=ax)
    ax.set_title("Precision-Recall Curves - Churn Model Comparison")
    fig.tight_layout()
    fig.savefig(output_dir / "precision_recall_curve.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_predictions(
        best.y_test,
        best.y_pred,
        labels=[0, 1],
        display_labels=["No churn", "Churn"],
        cmap="Blues",
        ax=ax,
        colorbar=False,
    )
    ax.set_title(f"Best model: {best.algorithm} - {best.variant}")
    fig.tight_layout()
    fig.savefig(output_dir / "confusion_matrix.png", dpi=180)
    plt.close(fig)


def latex_table(df: pd.DataFrame) -> str:
    table = df[
        [
            "algorithm",
            "variant",
            "roc_auc",
            "pr_auc",
            "accuracy",
            "f1_score",
            "training_time_seconds",
            "interpretability",
        ]
    ].copy()
    table["Algorithme"] = table["algorithm"] + " (" + table["variant"] + ")"
    table = table.rename(
        columns={
            "roc_auc": "ROC-AUC",
            "pr_auc": "PR-AUC",
            "accuracy": "Accuracy",
            "f1_score": "F1",
            "training_time_seconds": "Temps",
            "interpretability": "Interpretabilite",
        }
    )
    table = table[["Algorithme", "ROC-AUC", "PR-AUC", "Accuracy", "F1", "Temps", "Interpretabilite"]]
    return table.to_latex(index=False, float_format="%.4f", escape=True)


def generate_conclusion(df: pd.DataFrame, best_models: dict[str, dict[str, Any]]) -> str:
    best = best_models["best_by_performance_interpretability"]
    best_roc = best_models["best_by_roc_auc"]
    best_f1 = best_models["best_by_f1_score"]

    ordered = df.sort_values("compromise_score", ascending=False).reset_index(drop=True)
    lines = [
        "# Conclusion automatique - comparaison churn",
        "",
        (
            "Le modele retenu selon le compromis performance / interpretabilite est "
            f"**{best['algorithm']} ({best['variant']})**. "
            f"Il obtient un ROC-AUC de {best['roc_auc']:.4f}, un F1-score de "
            f"{best['f1_score']:.4f} et une PR-AUC de {best['pr_auc']:.4f}. "
            "Ce choix equilibre la qualite de discrimination, la detection de la classe churn "
            "et la capacite a expliquer le modele dans un rapport de PFE."
        ),
        "",
        (
            f"Le meilleur score ROC-AUC est obtenu par **{best_roc['algorithm']} "
            f"({best_roc['variant']})** avec {best_roc['roc_auc']:.4f}. "
            f"Le meilleur F1-score est obtenu par **{best_f1['algorithm']} "
            f"({best_f1['variant']})** avec {best_f1['f1_score']:.4f}."
        ),
        "",
        "Analyse par famille de modeles:",
    ]

    best_by_algorithm = (
        df.sort_values(["algorithm", "roc_auc", "f1_score"], ascending=[True, False, False])
        .groupby("algorithm")
        .head(1)
    )
    for _, row in best_by_algorithm.iterrows():
        algo = row["algorithm"]
        interp = row["interpretability"]
        if algo == "Logistic Regression":
            comment = (
                "tres interpretable et utile comme baseline robuste, mais peut sous-apprendre "
                "les relations non lineaires."
            )
        elif algo == "Random Forest":
            comment = (
                "capture des interactions non lineaires et donne des importances de variables, "
                "mais reste moins lisible qu'une regression logistique."
            )
        elif algo == "XGBoost":
            comment = (
                "souvent performant sur donnees tabulaires, avec une bonne gestion des interactions, "
                "mais plus complexe a justifier et a regler."
            )
        else:
            comment = (
                "peut modeliser des frontieres complexes avec le noyau RBF, mais son interpretabilite "
                "est faible et le cout d'inference peut augmenter."
            )
        lines.append(
            (
                f"- **{algo}**: meilleure variante {row['variant']}, ROC-AUC={row['roc_auc']:.4f}, "
                f"F1={row['f1_score']:.4f}, interpretabilite={interp}. {comment}"
            )
        )

    lines.extend(
        [
            "",
            "Classement compromis:",
        ]
    )
    for idx, row in ordered.iterrows():
        lines.append(
            (
                f"{idx + 1}. {row['algorithm']} ({row['variant']}) - "
                f"score compromis={row['compromise_score']:.4f}, ROC-AUC={row['roc_auc']:.4f}, "
                f"F1={row['f1_score']:.4f}"
            )
        )
    return "\n".join(lines) + "\n"


def save_outputs(
    output_dir: Path,
    X: pd.DataFrame,
    y: pd.Series,
    source: dict[str, Any],
    split_info: dict[str, int],
    results: list[ExperimentResult],
    df: pd.DataFrame,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "plots").mkdir(parents=True, exist_ok=True)

    best_models = identify_best_models(df)
    best_info = best_models["best_by_performance_interpretability"]
    best = best_result_by_name(results, best_info["algorithm"], best_info["variant"])

    df.to_csv(output_dir / "results.csv", index=False)
    df.to_pickle(output_dir / "results_dataframe.pkl")
    (output_dir / "metrics_table.tex").write_text(latex_table(df), encoding="utf-8")
    conclusion = generate_conclusion(df, best_models)
    (output_dir / "conclusion.md").write_text(conclusion, encoding="utf-8")
    joblib.dump(best.estimator, output_dir / "best_model.joblib")

    metrics_payload = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "random_state": RANDOM_STATE,
        "split": {
            "train": TRAIN_SIZE,
            "validation": VALIDATION_SIZE,
            "test": TEST_SIZE,
            "counts": split_info,
            "stratify": True,
        },
        "data_source": source,
        "dataset_quality": dataset_quality_report(X, y),
        "class_imbalance_ratio": class_ratio(y),
        "best_models": best_models,
        "results": df.to_dict(orient="records"),
        "artifacts": {
            "best_model": str(output_dir / "best_model.joblib"),
            "metrics_json": str(output_dir / "metrics.json"),
            "confusion_matrix": str(output_dir / "confusion_matrix.png"),
            "roc_curve": str(output_dir / "roc_curve.png"),
            "precision_recall_curve": str(output_dir / "precision_recall_curve.png"),
            "latex_table": str(output_dir / "metrics_table.tex"),
            "conclusion": str(output_dir / "conclusion.md"),
            "results_csv": str(output_dir / "results.csv"),
            "results_dataframe": str(output_dir / "results_dataframe.pkl"),
        },
        "models": {
            f"{result.algorithm} ({result.variant})": {
                "best_params": result.best_params,
                "validation_score": result.validation_score,
                "threshold": result.threshold,
                "metrics": result.metrics,
            }
            for result in results
        },
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics_payload, indent=2, ensure_ascii=False, default=json_default),
        encoding="utf-8",
    )
    save_plots(output_dir, results, best)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare churn classification algorithms on the DigMaco Analytics dataset."
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
        help="Directory where metrics, plots and models are saved.",
    )
    parser.add_argument(
        "--smote",
        choices=["auto", "always", "never"],
        default="auto",
        help="Compare SMOTE variants when useful. Default: auto.",
    )
    parser.add_argument(
        "--query-timeout-ms",
        type=int,
        default=180000,
        help="SQL statement timeout for building the churn dataset.",
    )
    parser.add_argument(
        "--svm-max-train-rows",
        type=int,
        default=5000,
        help=(
            "Maximum stratified training rows for SVM RBF. "
            "Use 0 to disable the cap; default keeps the experiment tractable."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    require_dependencies()
    output_dir = Path(args.output_dir).resolve()

    X, y, source = load_dataset(args)
    source["svm_max_train_rows"] = int(args.svm_max_train_rows)
    X = X.reset_index(drop=True)
    y = pd.Series(y).reset_index(drop=True).astype(int)

    quality = dataset_quality_report(X, y)
    print("Dataset loaded:", json.dumps(quality, default=json_default))

    X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(X, y)
    split_info = {
        "train_rows": int(len(X_train)),
        "validation_rows": int(len(X_val)),
        "test_rows": int(len(X_test)),
    }
    print("Split:", json.dumps(split_info))

    results = run_experiments(
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
        smote_mode=args.smote,
        svm_max_train_rows=args.svm_max_train_rows,
    )
    df = results_dataframe(results)
    save_outputs(output_dir, X, y, source, split_info, results, df)

    best = identify_best_models(df)["best_by_performance_interpretability"]
    print("\nResults saved to:", output_dir)
    print(
        "Best compromise:",
        f"{best['algorithm']} ({best['variant']})",
        f"ROC-AUC={best['roc_auc']:.4f}",
        f"F1={best['f1_score']:.4f}",
    )
    print("\nLatex table:\n")
    print(latex_table(df))


if __name__ == "__main__":
    main()
