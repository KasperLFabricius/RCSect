from __future__ import annotations

import math

import pandas as pd
from st_aggrid import AgGrid


def _coerce_numeric(value):
    if value is None:
        return None
    if pd.isna(value):
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        numeric = float(value)
        if pd.isna(numeric) or not math.isfinite(numeric):
            return None
        return numeric
    except (TypeError, ValueError):
        return None


def build_ordered_points_editor_df(points: list[dict] | None) -> pd.DataFrame:
    ordered_points = sorted(points or [], key=lambda pt: pt.get("id", 0))
    rows = [
        {"id": i, "x": pt.get("x"), "y": pt.get("y")}
        for i, pt in enumerate(ordered_points, start=1)
    ]
    rows.extend(
        [
            {"id": pd.NA, "x": None, "y": None},
            {"id": pd.NA, "x": None, "y": None},
        ]
    )
    df_points = pd.DataFrame(rows, columns=["id", "x", "y"])
    df_points["id"] = df_points["id"].astype("Int64")
    return df_points


def clean_ordered_point_records(records: list[dict]) -> list[dict]:
    cleaned = []
    for row in records:
        x = _coerce_numeric(row.get("x"))
        y = _coerce_numeric(row.get("y"))
        if x is None or y is None:
            continue
        cleaned.append({"id": len(cleaned) + 1, "x": x, "y": y})
    return cleaned


def edit_ordered_points(points, key_prefix) -> list[dict]:
    df_points = build_ordered_points_editor_df(points)

    grid_options = {
        "defaultColDef": {"sortable": False, "filter": False, "resizable": True},
        "rowDragManaged": True,
        "animateRows": False,
        "stopEditingWhenCellsLoseFocus": True,
        "enterMovesDown": True,
        "enterMovesDownAfterEdit": True,
        "singleClickEdit": True,
        "suppressRowClickSelection": True,
        "columnDefs": [
            {
                "headerName": "",
                "field": "drag",
                "rowDrag": True,
                "editable": False,
                "width": 36,
                "pinned": "left",
            },
            {"headerName": "ID", "field": "id", "editable": False, "width": 70},
            {"headerName": "x [m]", "field": "x", "editable": True, "type": "numericColumn"},
            {"headerName": "y [m]", "field": "y", "editable": True, "type": "numericColumn"},
        ],
    }

    result = AgGrid(
        df_points,
        gridOptions=grid_options,
        update_on=["rowDragEnd", "cellEditingStopped"],
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=False,
        key=key_prefix,
        height=260,
    )

    data = result.get("data", df_points)
    records = data.to_dict("records") if hasattr(data, "to_dict") else list(data)

    return clean_ordered_point_records(records)
