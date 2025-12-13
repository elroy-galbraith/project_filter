"""
Database migration script to add location fields to existing LiveCall records.

This script safely adds new columns to the database without losing existing data.
"""

import sqlite3
import os

def migrate_database():
    """Add location fields to live_calls table."""

    db_path = "trident_calls.db"

    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("   Creating new database with updated schema...")
        from database import init_db
        init_db()
        print("✅ New database created successfully")
        return

    print(f"🔄 Migrating database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(live_calls)")
    columns = [column[1] for column in cursor.fetchall()]

    migrations_needed = []

    if 'location' not in columns:
        migrations_needed.append("ALTER TABLE live_calls ADD COLUMN location VARCHAR")

    if 'lat' not in columns:
        migrations_needed.append("ALTER TABLE live_calls ADD COLUMN lat FLOAT")

    if 'lng' not in columns:
        migrations_needed.append("ALTER TABLE live_calls ADD COLUMN lng FLOAT")

    if 'category' not in columns:
        migrations_needed.append("ALTER TABLE live_calls ADD COLUMN category VARCHAR")

    if not migrations_needed:
        print("✅ Database already up to date - no migrations needed")
        conn.close()
        return

    print(f"📝 Applying {len(migrations_needed)} migration(s)...")

    try:
        for migration in migrations_needed:
            print(f"   Executing: {migration}")
            cursor.execute(migration)

        conn.commit()
        print("✅ Migration completed successfully")

        # Set default location for existing calls without coordinates
        cursor.execute("""
            UPDATE live_calls
            SET location = 'Jamaica (Location not specified)',
                lat = 18.1096,
                lng = -77.2975,
                category = 'EMERGENCY CALL'
            WHERE location IS NULL
        """)
        conn.commit()

        affected = cursor.rowcount
        if affected > 0:
            print(f"✅ Updated {affected} existing record(s) with default location (Jamaica center)")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

    print("\n✅ Database migration complete!")
    print("   New columns added: location, lat, lng, category")


if __name__ == "__main__":
    migrate_database()
