import pandas as pd

from ui.aggrid_points import build_ordered_points_editor_df, clean_ordered_point_records


def test_build_ordered_points_editor_df_uses_nullable_ids_for_placeholders():
    df_points = build_ordered_points_editor_df(
        [
            {"id": 2, "x": 1.0, "y": 2.0},
            {"id": 1, "x": 3.0, "y": 4.0},
        ]
    )

    assert not any(val == "" for val in df_points["id"].tolist() if isinstance(val, str))
    assert pd.api.types.is_integer_dtype(df_points["id"].dtype)
    assert df_points["id"].isna().sum() == 2


def test_clean_ordered_point_records_drops_incomplete_rows_and_renumbers_ids():
    cleaned = clean_ordered_point_records(
        [
            {"id": 7, "x": 0.0, "y": 1.0},
            {"id": pd.NA, "x": 1.5, "y": None},
            {"id": pd.NA, "x": "", "y": 5.0},
            {"id": 4, "x": "2.5", "y": "3.5"},
        ]
    )

    assert cleaned == [
        {"id": 1, "x": 0.0, "y": 1.0},
        {"id": 2, "x": 2.5, "y": 3.5},
    ]
