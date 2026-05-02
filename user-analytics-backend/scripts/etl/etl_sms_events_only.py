from __future__ import annotations

import os
import uuid

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

load_dotenv()

USER_NS = uuid.UUID("11111111-1111-1111-1111-111111111111")
SMS_NS = uuid.UUID("77777777-7777-7777-7777-777777777777")
SERVICE_NS = uuid.UUID("44444444-4444-4444-4444-444444444444")


def uuid5(namespace: uuid.UUID, value: str) -> uuid.UUID:
    return uuid.uuid5(namespace, value)


def clean_phone(value):
    if value is None:
        return None
    phone = str(value).strip()
    if not phone:
        return None
    if phone.startswith("00"):
        phone = phone[2:]
    if phone.startswith("216") and not phone.startswith("+"):
        phone = "+" + phone
    return phone


class SMSETL:
    def __init__(self, source_url: str, target_url: str, truncate_target: bool = True):
        self.source_engine = create_engine(source_url, pool_pre_ping=True)
        self.target_engine = create_engine(target_url, pool_pre_ping=True)
        self.truncate_target = truncate_target
        self.source_inspector = inspect(self.source_engine)
        self.target_inspector = inspect(self.target_engine)
        self.service_map = {}
        self.user_map = {}

    @staticmethod
    def first_existing(columns: set[str], candidates: list[str]) -> str | None:
        for c in candidates:
            if c in columns:
                return c
        return None

    def load_service_map(self):
        with self.target_engine.connect() as conn:
            rows = conn.execute(text('SELECT id, name FROM services')).fetchall()
        self.service_map = {str(r.name).strip().lower(): r.id for r in rows if r.name}

    def load_user_map(self):
        user_cols = {c['name'] for c in self.target_inspector.get_columns('users')}
        phone_col = None
        for cand in ['phone_number', 'phoneNumber', 'phonenumber', 'msisdn', 'mobile']:
            if cand in user_cols:
                phone_col = cand
                break
        if phone_col is None:
            raise RuntimeError('No phone column found in target users table')

        with self.target_engine.connect() as conn:
            rows = conn.execute(text(f'SELECT id, "{phone_col}" AS phone FROM users')).fetchall()
        self.user_map = {clean_phone(r.phone): r.id for r in rows if r.phone}

    def resolve_source_table(self):
        tables = set(self.source_inspector.get_table_names())
        preferred = [
            'message_events',
            'smsevents',
            'sms_events',
            'messagelogs',
            'message_logs',
            'outboundmessages',
            'outbound_messages',
            'messages',
        ]

        id_candidates = ['id', 'sms_id', 'message_id', 'log_id']
        ts_candidates = ['created_at', 'event_datetime', 'sent_at', 'delivered_at', 'updated_at']
        msg_candidates = ['sms_text', 'message', 'message_content', 'content', 'body', 'text']
        phone_candidates = ['phone', 'phone_number', 'phonenumber', 'msisdn', 'mobile']
        subscribed_candidates = ['subscribedclientid', 'subscribed_client_id', 'client_id']

        diagnostics: dict[str, list[str]] = {}
        scored: list[tuple[int, str, set[str], dict[str, str | None]]] = []

        scan_tables = [t for t in preferred if t in tables]
        for t in tables:
            if t not in scan_tables and ('sms' in t.lower() or 'message' in t.lower()):
                scan_tables.append(t)

        for table in scan_tables:
            cols = {c['name'] for c in self.source_inspector.get_columns(table)}
            resolved = {
                'id_col': self.first_existing(cols, id_candidates),
                'ts_col': self.first_existing(cols, ts_candidates),
                'msg_col': self.first_existing(cols, msg_candidates),
                'phone_col': self.first_existing(cols, phone_candidates),
                'subscribed_col': self.first_existing(cols, subscribed_candidates),
            }

            missing = []
            if not resolved['id_col']:
                missing.append('id')
            if not resolved['ts_col']:
                missing.append('timestamp')
            if not resolved['msg_col']:
                missing.append('message_content')
            if not resolved['phone_col'] and not resolved['subscribed_col']:
                missing.append('phone_or_subscribed_client')

            diagnostics[table] = missing
            if not missing:
                score = len(cols)
                if table in preferred:
                    score += 100
                scored.append((score, table, cols, resolved))

        if not scored:
            print('SMS ETL skipped: no usable source SMS table found')
            for table_name, missing in sorted(diagnostics.items()):
                print(f'  - {table_name}: missing {missing}')
            return None, set(), diagnostics, {}

        scored.sort(key=lambda x: x[0], reverse=True)
        _, table, cols, resolved = scored[0]
        print(f'Using source table: {table}')
        return table, cols, diagnostics, resolved

    def fetch_source_services(self):
        tables = set(self.source_inspector.get_table_names())
        if 'services' not in tables:
            return {}
        cols = {c['name'] for c in self.source_inspector.get_columns('services')}
        if 'entitled' in cols:
            q = text('SELECT id, entitled AS service_name FROM services')
        elif 'name' in cols:
            q = text('SELECT id, name AS service_name FROM services')
        else:
            return {}
        df = pd.read_sql_query(q, self.source_engine)
        return {int(r['id']): str(r['service_name']).strip() for _, r in df.iterrows() if pd.notna(r['service_name'])}

    def fetch_phone_lookup(self):
        tables = set(self.source_inspector.get_table_names())
        source_table = None
        if 'subscribedclients' in tables:
            source_table = 'subscribedclients'
        elif 'subscribed_clients' in tables:
            source_table = 'subscribed_clients'
        if source_table is None:
            return {}
        cols = {c['name'] for c in self.source_inspector.get_columns(source_table)}
        phone_col = None
        for cand in ['phoneNumber', 'phone_number', 'phonenumber', 'msisdn', 'mobile']:
            if cand in cols:
                phone_col = cand
                break
        if not phone_col or 'id' not in cols:
            return {}
        q = text(f'SELECT id, "{phone_col}" AS phone FROM {source_table}')
        df = pd.read_sql_query(q, self.source_engine)
        return {int(r['id']): clean_phone(r['phone']) for _, r in df.iterrows() if pd.notna(r['phone'])}

    def map_event_type(self, event_type_id: int):
        mapping = {
            1: ('OTP', True, True),
            2: ('SUBSCRIPTION', False, True),
            3: ('RENEWAL', False, False),
            4: ('UNSUBSCRIBE', False, False),
            5: ('RESUBSCRIBE', False, True),
            8: ('INSUFFICIENT_CREDIT', False, False),
            9: ('MARKETING', False, False),
            10: ('FORGOT_PASSWORD', False, False),
            12: ('ALREADY_SUBSCRIBED', False, False),
            13: ('NOT_SUBSCRIBED', False, False),
            14: ('RECOVER_PASSWORD', False, False),
            15: ('OTP', True, True),
            16: ('TRIAL_ENDING', False, False),
            17: ('RENEWAL_WEEKLY', False, False),
        }
        return mapping.get(int(event_type_id), ('SMS', False, False))

    def ensure_target_columns(self):
        cols = {c['name'] for c in self.target_inspector.get_columns('sms_events')}
        required = ['id', 'user_id', 'service_id', 'event_datetime', 'event_type', 'message_content', 'is_otp', 'is_activation', 'phone_number']
        missing = [c for c in required if c not in cols]
        if missing:
            raise RuntimeError(f'Target sms_events missing required columns: {missing}')

    def truncate(self):
        with self.target_engine.begin() as conn:
            conn.execute(text('TRUNCATE TABLE sms_events RESTART IDENTITY CASCADE'))

    def run(self):
        self.ensure_target_columns()
        self.load_service_map()
        self.load_user_map()
        source_table, source_cols, missing_map, resolved_cols = self.resolve_source_table()
        if source_table is None:
            return

        if self.truncate_target:
            self.truncate()

        source_services = self.fetch_source_services()
        source_phones = self.fetch_phone_lookup()

        id_col = resolved_cols.get('id_col') or 'id'
        ts_col = resolved_cols.get('ts_col') or 'created_at'
        msg_col = resolved_cols.get('msg_col') or 'sms_text'
        phone_col = resolved_cols.get('phone_col')
        subscribed_col = resolved_cols.get('subscribed_col')

        service_col = self.first_existing(source_cols, ['service_id'])
        event_type_col = self.first_existing(source_cols, ['event_type_id', 'event_type', 'type', 'event_id'])

        selected_cols = [id_col, ts_col, msg_col]
        for optional_col in [service_col, event_type_col, phone_col, subscribed_col]:
            if optional_col and optional_col not in selected_cols:
                selected_cols.append(optional_col)

        q = text(
            f'SELECT {", ".join(selected_cols)} '
            f'FROM {source_table} '
            f'WHERE {msg_col} IS NOT NULL '
            f'ORDER BY {id_col}'
        )
        df = pd.read_sql_query(q, self.source_engine)

        rows = []
        for _, r in df.iterrows():
            source_id = int(r[id_col])
            source_service_id = int(r[service_col]) if service_col and pd.notna(r[service_col]) else None
            raw_event_type = r[event_type_col] if event_type_col and pd.notna(r[event_type_col]) else None
            message = str(r[msg_col]).strip() if pd.notna(r[msg_col]) else None
            event_dt = pd.to_datetime(r[ts_col], utc=True, errors='coerce')
            if not message or pd.isna(event_dt):
                continue

            if raw_event_type is None:
                event_type, is_otp, is_activation = ('SMS', False, False)
            else:
                try:
                    event_type, is_otp, is_activation = self.map_event_type(int(raw_event_type))
                except Exception:
                    event_type = str(raw_event_type).strip().upper() or 'SMS'
                    is_otp = 'OTP' in event_type
                    is_activation = event_type in {'SUBSCRIPTION', 'ACTIVATION', 'RESUBSCRIBE'}

            service_name = source_services.get(source_service_id)
            service_uuid = self.service_map.get(service_name.strip().lower()) if service_name else None

            phone_number = clean_phone(r[phone_col]) if phone_col and pd.notna(r[phone_col]) else None
            if phone_number is None and subscribed_col and pd.notna(r[subscribed_col]):
                phone_number = source_phones.get(int(r[subscribed_col]))
            user_uuid = self.user_map.get(phone_number) if phone_number else None

            rows.append({
                'id': str(uuid5(SMS_NS, f'sms:{source_id}')),
                'user_id': str(user_uuid) if user_uuid else None,
                'service_id': str(service_uuid) if service_uuid else (str(uuid5(SERVICE_NS, f'service:{source_service_id}')) if source_service_id is not None else None),
                'event_datetime': event_dt.to_pydatetime(),
                'event_type': event_type,
                'message_content': message,
                'is_otp': bool(is_otp),
                'is_activation': bool(is_activation),
                'phone_number': phone_number,
            })

        if not rows:
            print('No valid SMS rows to insert')
            return

        insert_sql = text("""
            INSERT INTO sms_events (
                id, user_id, service_id, event_datetime, event_type,
                message_content, is_otp, is_activation, phone_number
            ) VALUES (
                :id, :user_id, :service_id, :event_datetime, :event_type,
                :message_content, :is_otp, :is_activation, :phone_number
            )
            ON CONFLICT (id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                service_id = EXCLUDED.service_id,
                event_datetime = EXCLUDED.event_datetime,
                event_type = EXCLUDED.event_type,
                message_content = EXCLUDED.message_content,
                is_otp = EXCLUDED.is_otp,
                is_activation = EXCLUDED.is_activation,
                phone_number = EXCLUDED.phone_number
        """)

        with self.target_engine.begin() as conn:
            conn.execute(insert_sql, rows)

        print(f'source_table={source_table} inserted_rows={len(rows)}')


if __name__ == '__main__':
    source_url = os.getenv('PROD_CONN') or os.getenv('PRODCONN')
    target_url = os.getenv('ANALYTICS_CONN') or os.getenv('ANALYTICSCONN')
    if not source_url or not target_url:
        raise RuntimeError('Missing PROD_CONN/PRODCONN or ANALYTICS_CONN/ANALYTICSCONN in environment')
    SMSETL(source_url, target_url, truncate_target=True).run()

