from __future__ import annotations

import argparse
import json
import os
import re
import uuid
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import bindparam, create_engine, inspect, text

SMS_NS = uuid.UUID("77777777-7777-7777-7777-777777777777")
SERVICE_NS = uuid.UUID("44444444-4444-4444-4444-444444444444")

EVENT_TYPE_MAP: dict[int, str] = {
    1: "OTP",
    2: "SUBSCRIPTION",
    3: "RENEWAL",
    4: "UNSUBSCRIBE",
    5: "RESUBSCRIBE",
    8: "INSUFFICIENT_CREDIT",
    9: "MARKETING",
    10: "FORGOT_PASSWORD",
    12: "ALREADY_SUBSCRIBED",
    13: "NOT_SUBSCRIBED",
    14: "RECOVER_PASSWORD",
    15: "OTP",
    16: "TRIAL_ENDING",
    17: "RENEWAL_WEEKLY",
}


def uuid5(ns: uuid.UUID, value: str) -> uuid.UUID:
    return uuid.uuid5(ns, value)


class HawalaSmsEtl:
    def __init__(self, source_url: str, target_url: str, batch_size: int, limit: int | None, truncate_target: bool):
        self.source_engine = create_engine(source_url, pool_pre_ping=True)
        self.target_engine = create_engine(target_url, pool_pre_ping=True)
        self.batch_size = batch_size
        self.limit = limit
        self.truncate_target = truncate_target
        self.source_inspector = inspect(self.source_engine)
        self.target_inspector = inspect(self.target_engine)

    def _resolve_join_sql(self) -> tuple[str, str]:
        me_cols = {c["name"] for c in self.source_inspector.get_columns("message_events")}
        mt_cols = {c["name"] for c in self.source_inspector.get_columns("message_templates")}

        if "event_type_id" in mt_cols and "event_id" in me_cols:
            return "mt.event_type_id = me.event_id", "mt.event_type_id=me.event_id"
        if "template_id" in me_cols and "id" in mt_cols:
            return "me.template_id = mt.id", "me.template_id=mt.id"
        if "event_type_id" in me_cols and "id" in mt_cols:
            return "me.event_type_id = mt.id", "me.event_type_id=mt.id"

        return "1=0", "no-join"

    @staticmethod
    def _normalize_event_type(raw_event_type: Any) -> str:
        if raw_event_type is None:
            return "SMS"
        try:
            return EVENT_TYPE_MAP.get(int(raw_event_type), "SMS")
        except Exception:
            txt = str(raw_event_type).strip().upper()
            return txt if txt else "SMS"

    @staticmethod
    def _to_optional_str(value: Any) -> str | None:
        if value is None or pd.isna(value):
            return None
        txt = str(value).strip()
        return txt if txt and txt.lower() != "nan" else None

    @staticmethod
    def _to_json_safe(value: Any) -> Any:
        if value is None:
            return None
        try:
            if pd.isna(value):
                return None
        except Exception:
            pass
        return value

    @staticmethod
    def _is_otp(event_type: str, message_text: str | None, template_code: str | None) -> bool:
        blob = " ".join([event_type or "", message_text or "", template_code or ""]).lower()
        return event_type == "OTP" or any(k in blob for k in ["otp", "verify", "verification", "code", "one-time", "one time"])

    @staticmethod
    def _is_activation(event_type: str, message_text: str | None, template_name: str | None) -> bool:
        if event_type in {"SUBSCRIPTION", "RESUBSCRIBE"}:
            return True
        blob = " ".join([event_type or "", message_text or "", template_name or ""]).lower()
        return any(k in blob for k in ["activation", "activate", "subscribe", "confirm", "optin", "opt-in"])

    def _target_columns(self) -> set[str]:
        return {c["name"] for c in self.target_inspector.get_columns("sms_events")}

    def _truncate_target(self) -> None:
        with self.target_engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE sms_events RESTART IDENTITY CASCADE"))

    def _source_chunks(self, select_sql: str):
        return pd.read_sql_query(text(select_sql), self.source_engine, chunksize=self.batch_size)

    def run(self) -> None:
        source_tables = set(self.source_inspector.get_table_names())
        if "message_events" not in source_tables or "message_templates" not in source_tables:
            raise RuntimeError("Source tables message_events/message_templates are required")

        join_sql, join_strategy = self._resolve_join_sql()
        limit_sql = f" LIMIT {self.limit}" if self.limit else ""
        select_sql = f"""
            SELECT
                mt.id AS template_id,
                mt.service_id,
                mt.event_type_id,
                mt.sms_text,
                mt.created_at AS mt_created_at,
                mt.updated_at AS mt_updated_at,
                mt.marketing_day_number,
                me.id AS message_event_row_id,
                me.event_id AS message_event_id,
                me.key AS message_event_key,
                me.name AS message_event_name,
                me.created_at AS me_created_at
            FROM message_templates mt
            LEFT JOIN message_events me ON {join_sql}
            WHERE mt.sms_text IS NOT NULL
            ORDER BY mt.id
            {limit_sql}
        """

        if self.truncate_target:
            self._truncate_target()

        target_cols = self._target_columns()
        payload_order = [
            "id",
            "user_id",
            "service_id",
            "event_datetime",
            "event_type",
            "message_content",
            "template_name",
            "template_code",
            "is_otp",
            "is_activation",
            "direction",
            "source_system",
            "metadata",
        ]
        active_cols = [c for c in payload_order if c in target_cols]

        if "id" not in active_cols:
            raise RuntimeError("sms_events.id is required")

        placeholders = []
        for col in active_cols:
            if col == "metadata":
                placeholders.append("CAST(:metadata AS jsonb)")
            else:
                placeholders.append(f":{col}")

        update_cols = [c for c in active_cols if c != "id"]
        upsert_sql = text(
            f"""
            INSERT INTO sms_events ({", ".join(active_cols)})
            VALUES ({", ".join(placeholders)})
            ON CONFLICT (id)
            DO UPDATE SET
                {", ".join(f"{c}=EXCLUDED.{c}" for c in update_cols)}
            """
        )

        inserted = 0
        skipped = 0

        for chunk in self._source_chunks(select_sql):
            rows: list[dict[str, Any]] = []
            for rec in chunk.itertuples(index=False):
                message_text = str(getattr(rec, "sms_text", "") or "").strip()
                if not message_text:
                    skipped += 1
                    continue

                event_dt_raw = getattr(rec, "mt_created_at", None) or getattr(rec, "me_created_at", None)
                event_dt = pd.to_datetime(event_dt_raw, utc=True, errors="coerce")
                if pd.isna(event_dt):
                    skipped += 1
                    continue

                template_id = int(getattr(rec, "template_id"))
                source_service_id = getattr(rec, "service_id", None)
                event_type_id = getattr(rec, "event_type_id", None)

                event_type = self._normalize_event_type(event_type_id)
                template_name = self._to_optional_str(getattr(rec, "message_event_name", None))
                template_code = self._to_optional_str(getattr(rec, "message_event_key", None))

                is_otp = self._is_otp(event_type, message_text, template_code)
                is_activation = self._is_activation(event_type, message_text, template_name)

                service_uuid = None
                if source_service_id is not None and str(source_service_id).strip() != "":
                    try:
                        service_uuid = str(uuid5(SERVICE_NS, f"service:{int(source_service_id)}"))
                    except Exception:
                        service_uuid = None

                metadata = {
                    "source_table": "message_templates",
                    "linked_table": "message_events",
                    "join_strategy": join_strategy,
                    "template_id": template_id,
                    "message_event_row_id": self._to_json_safe(getattr(rec, "message_event_row_id", None)),
                    "message_event_id": self._to_json_safe(getattr(rec, "message_event_id", None)),
                    "event_type_id": self._to_json_safe(event_type_id),
                    "source_service_id": self._to_json_safe(source_service_id),
                    "marketing_day_number": self._to_json_safe(getattr(rec, "marketing_day_number", None)),
                    "updated_at": self._to_optional_str(getattr(rec, "mt_updated_at", None)),
                    "contains_code": bool(re.search(r"\\b\\d{4,8}\\b", message_text)),
                }

                payload = {
                    "id": str(uuid5(SMS_NS, f"message_templates:{template_id}")),
                    "user_id": None,
                    "service_id": service_uuid,
                    "event_datetime": event_dt.to_pydatetime(),
                    "event_type": event_type,
                    "message_content": message_text,
                    "template_name": template_name,
                    "template_code": template_code,
                    "is_otp": bool(is_otp),
                    "is_activation": bool(is_activation),
                    "direction": "OUTBOUND",
                    "source_system": "hawala.message_events",
                    "metadata": json.dumps(metadata, ensure_ascii=True),
                }
                rows.append({k: payload.get(k) for k in active_cols})

            if rows:
                with self.target_engine.begin() as conn:
                    conn.execute(upsert_sql, rows)
                inserted += len(rows)

        print(f"join_strategy={join_strategy} inserted_rows={inserted} skipped_rows={skipped}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ETL SMS from Hawala message_events/message_templates")
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--truncate-target", action="store_true")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    source_url = os.getenv("HAWALA_CONN") or os.getenv("HAWALACONN") or os.getenv("PROD_CONN")
    target_url = os.getenv("ANALYTICS_CONN") or os.getenv("ANALYTICSCONN")
    if not source_url or not target_url:
        raise RuntimeError("Missing HAWALA_CONN/HAWALACONN and ANALYTICS_CONN/ANALYTICSCONN")

    etl = HawalaSmsEtl(
        source_url=source_url,
        target_url=target_url,
        batch_size=args.batch_size,
        limit=args.limit,
        truncate_target=args.truncate_target,
    )
    etl.run()


if __name__ == "__main__":
    main()
