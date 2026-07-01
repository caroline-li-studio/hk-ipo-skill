#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_PROJECT_CANDIDATES = [
    Path("/Users/jialu/Documents/Codex/HK IPO"),
    Path("/Users/jialu/Documents/Code/HK IPO"),
    Path.cwd(),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract active Hong Kong IPO subscription evidence.")
    parser.add_argument("--as-of", required=True, help="Date or datetime, e.g. 2026-03-23 or 2026-03-23T10:00.")
    parser.add_argument("--project", help="Path to the HK IPO project. Defaults to HK_IPO_PROJECT or known local paths.")
    parser.add_argument("--active-window-days", type=int, default=7)
    parser.add_argument("--top", type=int, default=0, help="Limit rows after deterministic pre-sorting. 0 means all.")
    parser.add_argument("--format", choices=["markdown", "json", "csv"], default="markdown")
    parser.add_argument("--output", help="Optional output file.")
    return parser.parse_args()


def find_project(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    env_path = os.environ.get("HK_IPO_PROJECT")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.extend(DEFAULT_PROJECT_CANDIDATES)
    for path in candidates:
        if (path / "data" / "processed").exists():
            return path.resolve()
    raise SystemExit("Could not find HK IPO project. Set HK_IPO_PROJECT or pass --project.")


def normalize_stock_code(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    digits = re.sub(r"\D", "", str(value).strip().upper())
    if not digits:
        return None
    if len(digits) < 5:
        digits = digits.zfill(5)
    return f"{digits}.HK"


def clean_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def parse_numeric(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float, np.number)) and not isinstance(value, bool):
        return None if pd.isna(value) else float(value)
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "na", "n/a", "--", "-", "—"}:
        return None
    text = text.replace(",", "").replace("%", "").replace("HKD", "").replace("$", "")
    text = re.sub(r"\s+", "", text)
    try:
        return float(text)
    except ValueError:
        return None


def parse_date(value: Any) -> pd.Timestamp | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.normalize()
    dt = pd.to_datetime(str(value).strip(), errors="coerce")
    if pd.isna(dt):
        return None
    return pd.Timestamp(dt).normalize()


def load_dataset(project: Path) -> pd.DataFrame:
    processed = project / "data" / "processed"
    for name in ("ipo_clean_enriched.csv", "ipo_deals.csv", "ipo_eastmoney_strict.csv"):
        path = processed / name
        if path.exists():
            df = pd.read_csv(path)
            df["_dataset_name"] = name
            return df
    raise SystemExit(f"No usable processed IPO dataset found under {processed}")


def first_existing(df: pd.DataFrame, names: list[str]) -> str | None:
    for name in names:
        if name in df.columns:
            return name
    return None


def ensure_column(df: pd.DataFrame, target: str, aliases: list[str]) -> None:
    if target in df.columns:
        return
    source = first_existing(df, aliases)
    if source:
        df[target] = df[source]
    else:
        df[target] = np.nan


def coerce_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ensure_column(df, "stock_code", ["股票代码", "股号", "代號", "code"])
    ensure_column(df, "stock_name_zh", ["股票名称", "中文简称", "中文名称", "公司名称", "名稱", "stock_name"])
    ensure_column(df, "listing_date", ["上市日期", "上市日", "listing_date_moomoo"])
    ensure_column(df, "apply_start_date", ["招股起始日期", "招股日期", "申请日期", "申請日期"])
    ensure_column(df, "apply_end_date", ["招股截止日期", "截止日期"])

    alias_map = {
        "public_sub_multiple": ["超额认购倍数", "公开认购倍数", "認購倍數"],
        "lot_success_rate_pct": ["一手中签率", "一手 中籤率", "1手中签率\n(%)"],
        "intl_placing_multiple": ["国配认购倍数", "國配認購倍數"],
        "day1_return_pct": ["首日涨跌幅", "首日升跌", "首日涨跌幅\n(%)", "first_day_pct"],
        "gray_market_return_pct": ["暗盘涨跌幅", "暗盘涨跌幅\n(%)", "dark_change_ratio"],
        "ipo_price_low": ["招股价下限", "发售价下限"],
        "ipo_price_high": ["招股价上限", "发售价上限", "发售价上限"],
        "ipo_price": ["发行价", "上市价", "issue_price"],
        "entrance_fee_hkd": ["入场费", "入場費"],
        "raise_amount_hkd_bn": ["募集资金_亿港元", "募资额\n(亿港元)"],
        "issue_market_cap_hkd_bn": ["发行市值", "發行市值"],
        "sponsors": ["保荐人", "保薦人"],
        "industry_label": ["行业", "行業"],
        "cornerstone_investors": ["基石投资者", "基石投資者"],
    }
    for target, aliases in alias_map.items():
        ensure_column(df, target, aliases)

    df["stock_code"] = df["stock_code"].map(normalize_stock_code)
    df["stock_name_zh"] = df["stock_name_zh"].map(clean_text)
    for col in ("apply_start_date", "apply_end_date", "listing_date", "allotment_result_date"):
        if col not in df.columns:
            df[col] = pd.NaT
        df[col] = df[col].map(parse_date)

    numeric_cols = [
        "raise_amount_hkd_bn",
        "issue_market_cap_hkd_bn",
        "issue_ratio_pct",
        "lot_success_rate_pct",
        "subscriber_count",
        "public_sub_multiple",
        "intl_placing_multiple",
        "gray_market_return_pct",
        "day1_return_pct",
        "ipo_price",
        "ipo_price_low",
        "ipo_price_high",
        "lot_size",
        "entrance_fee_hkd",
        "margin_rate_pct",
        "offer_public_pct",
        "offer_placing_pct",
    ]
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = df[col].map(parse_numeric)
    for col in ("sponsors", "industry_label", "cornerstone_investors", "source_name"):
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].map(clean_text)

    return df.dropna(subset=["stock_code", "listing_date"]).reset_index(drop=True)


def active_ipos(df: pd.DataFrame, as_of: pd.Timestamp, active_window_days: int) -> pd.DataFrame:
    frame = df[df["apply_start_date"].notna()].copy()
    if frame.empty:
        return frame
    fallback_end = frame["apply_start_date"] + pd.to_timedelta(active_window_days, unit="D")
    listing_limited_end = pd.concat([fallback_end, frame["listing_date"]], axis=1).min(axis=1)
    frame["_active_end_date"] = frame["apply_end_date"].where(frame["apply_end_date"].notna(), listing_limited_end)
    mask = (frame["apply_start_date"] <= as_of) & (as_of <= frame["_active_end_date"])
    active = frame[mask].copy()
    active = active.sort_values(["apply_start_date", "listing_date", "stock_code"])
    return active.drop_duplicates(subset=["stock_code"], keep="last").reset_index(drop=True)


def log_signal(value: float | None, cap: float) -> float:
    if value is None or pd.isna(value) or value <= 0:
        return 0.0
    return min(1.0, math.log1p(value) / math.log1p(cap))


def deterministic_priority(row: pd.Series) -> float:
    priority = 0.0
    priority += 30.0 * log_signal(row.get("public_sub_multiple"), 1000.0)
    priority += 12.0 * log_signal(row.get("subscriber_count"), 500000.0)
    gm = parse_numeric(row.get("gray_market_return_pct"))
    day1 = parse_numeric(row.get("day1_return_pct"))
    if gm is not None:
        priority += max(-20.0, min(20.0, gm * 0.5))
    if day1 is not None:
        priority += max(-15.0, min(15.0, day1 * 0.3))
    lot = parse_numeric(row.get("lot_success_rate_pct"))
    if lot is not None:
        priority += max(-8.0, min(8.0, (30.0 - lot) / 30.0 * 8.0))
    present = sum(
        has_value(row.get(col))
        for col in ["ipo_price_low", "ipo_price_high", "raise_amount_hkd_bn", "sponsors", "industry_label"]
    )
    priority += present * 1.5
    return round(priority, 3)


def evidence_quality(row: pd.Series) -> str:
    key_cols = [
        "ipo_price_low",
        "ipo_price_high",
        "raise_amount_hkd_bn",
        "public_sub_multiple",
        "lot_success_rate_pct",
        "gray_market_return_pct",
        "day1_return_pct",
        "sponsors",
        "industry_label",
    ]
    present = sum(has_value(row.get(col)) for col in key_cols)
    if present >= 7:
        return "high"
    if present >= 4:
        return "medium"
    return "low"


def has_value(value: Any) -> bool:
    if value is None:
        return False
    try:
        if pd.isna(value):
            return False
    except Exception:
        pass
    return bool(str(value).strip())


def make_records(rows: pd.DataFrame, as_of: pd.Timestamp) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for _, row in rows.iterrows():
        drivers = []
        for label, col, suffix in [
            ("公开认购倍数", "public_sub_multiple", "x"),
            ("一手中签率", "lot_success_rate_pct", "%"),
            ("暗盘表现", "gray_market_return_pct", "%"),
            ("首日表现", "day1_return_pct", "%"),
            ("募资规模", "raise_amount_hkd_bn", "亿港元"),
            ("入场费", "entrance_fee_hkd", "港元"),
        ]:
            value = row.get(col)
            if pd.notna(value):
                drivers.append(f"{label} {value:g}{suffix}")
        risk_notes = []
        if evidence_quality(row) == "low":
            risk_notes.append("关键数据较少，需谨慎")
        if pd.isna(row.get("public_sub_multiple")):
            risk_notes.append("未见公开认购热度")
        if pd.isna(row.get("lot_success_rate_pct")):
            risk_notes.append("未见中签率")
        records.append(
            {
                "stock_code": row.get("stock_code"),
                "stock_name_zh": row.get("stock_name_zh"),
                "apply_start_date": str(pd.Timestamp(row["apply_start_date"]).date()) if pd.notna(row.get("apply_start_date")) else None,
                "active_end_date": str(pd.Timestamp(row["_active_end_date"]).date()) if pd.notna(row.get("_active_end_date")) else None,
                "listing_date": str(pd.Timestamp(row["listing_date"]).date()) if pd.notna(row.get("listing_date")) else None,
                "days_to_listing": int((pd.Timestamp(row["listing_date"]).normalize() - as_of).days),
                "ipo_price_low": none_or_float(row.get("ipo_price_low")),
                "ipo_price_high": none_or_float(row.get("ipo_price_high")),
                "ipo_price": none_or_float(row.get("ipo_price")),
                "entrance_fee_hkd": none_or_float(row.get("entrance_fee_hkd")),
                "raise_amount_hkd_bn": none_or_float(row.get("raise_amount_hkd_bn")),
                "issue_market_cap_hkd_bn": none_or_float(row.get("issue_market_cap_hkd_bn")),
                "public_sub_multiple": none_or_float(row.get("public_sub_multiple")),
                "subscriber_count": none_or_float(row.get("subscriber_count")),
                "lot_success_rate_pct": none_or_float(row.get("lot_success_rate_pct")),
                "intl_placing_multiple": none_or_float(row.get("intl_placing_multiple")),
                "gray_market_return_pct": none_or_float(row.get("gray_market_return_pct")),
                "day1_return_pct": none_or_float(row.get("day1_return_pct")),
                "sponsors": clean_text(row.get("sponsors")),
                "industry_label": clean_text(row.get("industry_label")),
                "cornerstone_investors": clean_text(row.get("cornerstone_investors")),
                "source_name": clean_text(row.get("source_name")),
                "evidence_quality": evidence_quality(row),
                "deterministic_priority": deterministic_priority(row),
                "evidence_drivers": drivers,
                "risk_notes": risk_notes,
            }
        )
    return sorted(records, key=lambda item: item["deterministic_priority"], reverse=True)


def none_or_float(value: Any) -> float | None:
    numeric = parse_numeric(value)
    if numeric is None or pd.isna(numeric):
        return None
    return round(float(numeric), 4)


def to_markdown(result: dict[str, Any]) -> str:
    rows = result["rows"]
    lines = [
        f"# HK IPO active subscription evidence as of {result['as_of']}",
        "",
        f"Project: `{result['project']}`",
        f"Dataset: `{result['dataset']}`",
        f"Active candidates: {len(rows)}",
        "",
    ]
    if not rows:
        lines.append("No active IPO subscription candidates found in the local dataset for this date.")
        return "\n".join(lines)
    columns = [
        "rank",
        "stock_code",
        "stock_name_zh",
        "evidence_quality",
        "deterministic_priority",
        "apply_start_date",
        "active_end_date",
        "listing_date",
        "ipo_price_low",
        "ipo_price_high",
        "raise_amount_hkd_bn",
        "public_sub_multiple",
        "lot_success_rate_pct",
        "gray_market_return_pct",
        "day1_return_pct",
        "evidence_drivers",
        "risk_notes",
    ]
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
    for idx, row in enumerate(rows, 1):
        values = []
        for col in columns:
            if col == "rank":
                value = idx
            elif col in {"evidence_drivers", "risk_notes"}:
                value = "; ".join(row.get(col) or [])
            else:
                value = row.get(col)
            values.append("" if value is None else str(value).replace("|", "/"))
        lines.append("| " + " | ".join(values) + " |")
    lines.extend(
        [
            "",
            "Use this as evidence for LLM assessment. Assign the final 0-100 score and explanation from the rubric, not from deterministic_priority alone.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    project = find_project(args.project)
    as_of_raw = pd.to_datetime(args.as_of, errors="coerce")
    if pd.isna(as_of_raw):
        raise SystemExit(f"Invalid --as-of value: {args.as_of}")
    as_of = pd.Timestamp(as_of_raw).normalize()
    dataset = load_dataset(project)
    coerced = coerce_dataset(dataset)
    active = active_ipos(coerced, as_of, args.active_window_days)
    rows = make_records(active, as_of)
    if args.top and args.top > 0:
        rows = rows[: args.top]
    result = {
        "as_of": str(as_of.date()),
        "project": str(project),
        "dataset": str(dataset["_dataset_name"].iloc[0]) if "_dataset_name" in dataset and len(dataset) else None,
        "active_window_days": args.active_window_days,
        "rows": rows,
        "llm_scoring_instruction": "Use the hk-ipo-skill rubric to assign final score/rating and explain each IPO. deterministic_priority is only a sorting hint.",
    }

    if args.format == "json":
        output = json.dumps(result, ensure_ascii=False, indent=2)
    elif args.format == "csv":
        output = pd.DataFrame(rows).to_csv(index=False)
    else:
        output = to_markdown(result)
    if args.output:
        Path(args.output).expanduser().write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")


if __name__ == "__main__":
    main()
