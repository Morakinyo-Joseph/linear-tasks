"""
Add todo priority — and intentionally drop description from the database while
the ORM model still declares it.

This is a deliberate schema/model drift bug for Insider StarLink demos
(suspect-commit / release blame). Do not copy this pattern into production.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("todos", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="todo",
            name="priority",
            field=models.CharField(
                choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
                db_index=True,
                default="medium",
                max_length=16,
            ),
        ),
        migrations.AddIndex(
            model_name="todo",
            index=models.Index(
                fields=["organization", "priority"],
                name="todos_todo_organiz_prio_idx",
            ),
        ),
        # BUG: removes the DB column but Todo.description remains on the model.
        # Subsequent ORM reads/writes raise OperationalError (no such column).
        migrations.RemoveField(
            model_name="todo",
            name="description",
        ),
    ]
