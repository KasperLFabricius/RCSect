from __future__ import annotations

import pandas as pd
from st_aggrid import AgGrid


def _coerce_numeric(value):
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def edit_ordered_points(points, key_prefix) -> list[dict]:
    ordered_points = sorted(points or [], key=lambda pt: pt.get("id", 0))
    rows = [
        {"id": i, "x": pt.get("x"), "y": pt.get("y")}
        for i, pt in enumerate(ordered_points, start=1)
    ]
    rows.extend([
        {"id": "", "x": None, "y": None},
        {"id": "", "x": None, "y": None},
    ])
    df_points = pd.DataFrame(rows, columns=["id", "x", "y"])

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

    cleaned = []
    for row in records:
        x = _coerce_numeric(row.get("x"))
        y = _coerce_numeric(row.get("y"))
        if x is None or y is None:
            continue
        cleaned.append({"id": len(cleaned) + 1, "x": x, "y": y})

    return cleaned
