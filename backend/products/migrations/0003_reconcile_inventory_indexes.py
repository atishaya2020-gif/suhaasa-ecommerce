from django.db import migrations


OLD_VARIANT_INDEX = "products_inve_variant__e8a8f8_idx"
NEW_VARIANT_INDEX = "products_in_variant_6de66e_idx"
OLD_REASON_INDEX = "products_inve_reason_2c1a8d_idx"
NEW_REASON_INDEX = "products_in_reason_e37113_idx"


def _rename_index(schema_editor, old_name, new_name, columns):
    """Rename an index across supported databases, including SQLite."""
    connection = schema_editor.connection
    old_quoted = schema_editor.quote_name(old_name)
    new_quoted = schema_editor.quote_name(new_name)

    if connection.vendor == "sqlite":
        # SQLite does not support ALTER INDEX ... RENAME TO. Recreate the
        # non-unique index with the same definition under the new name.
        schema_editor.execute(f"DROP INDEX {old_quoted}")
        quoted_columns = ", ".join(
            f"{schema_editor.quote_name(column)} DESC" if descending else schema_editor.quote_name(column)
            for column, descending in columns
        )
        schema_editor.execute(
            f"CREATE INDEX {new_quoted} ON {schema_editor.quote_name('products_inventoryadjustment')} ({quoted_columns})"
        )
        return

    schema_editor.execute(
        schema_editor.sql_rename_index
        % {"old_name": old_quoted, "new_name": new_quoted}
    )


def reconcile_inventory_indexes(apps, schema_editor):
    """Reconcile index names without assuming the local DB is pristine.

    Some existing databases already contain Django's newer auto-generated names,
    while the historical 0002 migration records the older explicit names.
    Fresh databases need the old -> new rename; upgraded databases with the new
    names already present need no database operation.
    """
    connection = schema_editor.connection
    table = "products_inventoryadjustment"
    if table not in connection.introspection.table_names():
        return

    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, table)
        index_names = {
            name for name, details in constraints.items() if details.get("index")
        }

    if OLD_VARIANT_INDEX in index_names and NEW_VARIANT_INDEX not in index_names:
        _rename_index(
            schema_editor,
            OLD_VARIANT_INDEX,
            NEW_VARIANT_INDEX,
            [("variant_id", False), ("created_at", True)],
        )

    if OLD_REASON_INDEX in index_names and NEW_REASON_INDEX not in index_names:
        _rename_index(
            schema_editor,
            OLD_REASON_INDEX,
            NEW_REASON_INDEX,
            [("reason", False), ("created_at", True)],
        )


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_productvariant_low_stock_threshold_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    reconcile_inventory_indexes,
                    reverse_code=migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.RenameIndex(
                    model_name="inventoryadjustment",
                    old_name=OLD_VARIANT_INDEX,
                    new_name=NEW_VARIANT_INDEX,
                ),
                migrations.RenameIndex(
                    model_name="inventoryadjustment",
                    old_name=OLD_REASON_INDEX,
                    new_name=NEW_REASON_INDEX,
                ),
            ],
        ),
    ]
