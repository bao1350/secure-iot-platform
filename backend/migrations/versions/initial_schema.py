"""Create the constrained Secure IoT schema.

Revision ID: 20260716_01
Revises:
Create Date: 2026-07-16
"""

from alembic import op
import sqlalchemy as sa


revision = "20260716_01"
down_revision = None
branch_labels = None
depends_on = None


def _create_schema() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "sensors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("room", sa.String(), nullable=False),
        sa.Column("sensor_type", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "measures",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sensor_id", sa.Integer(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("humidity", sa.Float(), nullable=False),
        sa.Column("battery", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("humidity >= 0 AND humidity <= 100", name="ck_measures_humidity_range"),
        sa.CheckConstraint("battery >= 0 AND battery <= 100", name="ck_measures_battery_range"),
        sa.CheckConstraint("temperature >= -80 AND temperature <= 100", name="ck_measures_temperature_range"),
        sa.ForeignKeyConstraint(["sensor_id"], ["sensors.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_measures_sensor_timestamp", "measures", ["sensor_id", "timestamp"])


def _replace_foreign_key(table_name: str, column_name: str, target: str) -> None:
    inspector = sa.inspect(op.get_bind())
    for foreign_key in inspector.get_foreign_keys(table_name):
        if foreign_key["constrained_columns"] == [column_name]:
            if foreign_key.get("options", {}).get("ondelete") == "CASCADE":
                return
            op.drop_constraint(foreign_key["name"], table_name, type_="foreignkey")
            break

    op.create_foreign_key(
        f"fk_{table_name}_{column_name}",
        table_name,
        target.split(".")[0],
        [column_name],
        [target.split(".")[1]],
        ondelete="CASCADE",
    )


def _upgrade_existing_schema() -> None:
    """Harden the schema created by the former create_all startup path."""
    op.alter_column("users", "email", existing_type=sa.String(), nullable=False)
    op.alter_column("users", "hashed_password", existing_type=sa.String(), nullable=False)

    op.alter_column("sensors", "user_id", existing_type=sa.Integer(), nullable=False)
    _replace_foreign_key("sensors", "user_id", "users.id")

    # Les anciennes versions autorisaient des mesures sans capteur. Elles ne
    # peuvent pas respecter la nouvelle relation obligatoire, mais sont
    # conservées pour audit plutôt que supprimées.
    bind = op.get_bind()
    orphan_count = bind.execute(
        sa.text("SELECT count(*) FROM measures WHERE sensor_id IS NULL")
    ).scalar_one()
    if orphan_count:
        inspector = sa.inspect(bind)
        if "legacy_invalid_measures" not in inspector.get_table_names():
            op.create_table(
                "legacy_invalid_measures",
                sa.Column("id", sa.Integer(), primary_key=True),
                sa.Column("source_measure_id", sa.Integer(), nullable=False, unique=True),
                sa.Column("sensor_id", sa.Integer()),
                sa.Column("temperature", sa.Float()),
                sa.Column("humidity", sa.Float()),
                sa.Column("battery", sa.Float()),
                sa.Column("timestamp", sa.DateTime()),
                sa.Column("rejection_reason", sa.String(), nullable=False),
                sa.Column("quarantined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            )

        op.execute(
            """
            INSERT INTO legacy_invalid_measures
                (source_measure_id, sensor_id, temperature, humidity, battery, timestamp, rejection_reason)
            SELECT id, sensor_id, temperature, humidity, battery, timestamp,
                   'sensor_id absent lors de la migration vers une relation obligatoire'
            FROM measures
            WHERE sensor_id IS NULL
            ON CONFLICT (source_measure_id) DO NOTHING
            """
        )
        op.execute("DELETE FROM measures WHERE sensor_id IS NULL")

    for column_name, column_type in (
        ("sensor_id", sa.Integer()),
        ("temperature", sa.Float()),
        ("humidity", sa.Float()),
        ("battery", sa.Float()),
    ):
        op.alter_column("measures", column_name, existing_type=column_type, nullable=False)

    op.alter_column(
        "measures",
        "timestamp",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    _replace_foreign_key("measures", "sensor_id", "sensors.id")

    inspector = sa.inspect(op.get_bind())
    existing_checks = {check["name"] for check in inspector.get_check_constraints("measures")}
    for name, condition in (
        ("ck_measures_humidity_range", "humidity >= 0 AND humidity <= 100"),
        ("ck_measures_battery_range", "battery >= 0 AND battery <= 100"),
        ("ck_measures_temperature_range", "temperature >= -80 AND temperature <= 100"),
    ):
        if name not in existing_checks:
            op.create_check_constraint(name, "measures", condition)

    existing_indexes = {index["name"] for index in inspector.get_indexes("measures")}
    if "ix_measures_sensor_timestamp" not in existing_indexes:
        op.create_index("ix_measures_sensor_timestamp", "measures", ["sensor_id", "timestamp"])


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "users" not in inspector.get_table_names():
        _create_schema()
    else:
        _upgrade_existing_schema()


def downgrade() -> None:
    op.drop_index("ix_measures_sensor_timestamp", table_name="measures")
    op.drop_table("measures")
    op.drop_table("sensors")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
