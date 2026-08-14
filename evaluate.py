import numpy as np
from sklearn.metrics import cohen_kappa_score


def compute_qwk(y_true, y_pred, rescale_pred=True):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    if rescale_pred:
        if y_pred.max() != y_pred.min():
            y_pred = (y_pred - y_pred.min()) / (y_pred.max() - y_pred.min())
            y_pred = y_pred * (y_true.max() - y_true.min()) + y_true.min()
        y_pred = np.round(y_pred)

    y_true_int = np.round(y_true).astype(int)
    y_pred_int = np.round(y_pred).astype(int)
    return cohen_kappa_score(y_true_int, y_pred_int, weights="quadratic")
