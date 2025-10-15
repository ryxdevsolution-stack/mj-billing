import psycopg2
from config import Config

def check_database():
    """Check if all tables exist in the database"""
    try:
        # Connect to database
        conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
        cur = conn.cursor()

        print("=" * 60)
        print("DATABASE VERIFICATION REPORT")
        print("=" * 60)

        # Get all tables
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()

        # Expected tables
        expected_tables = [
            'audit_log',
            'client_entry',
            'gst_billing',
            'non_gst_billing',
            'payment_type',
            'report',
            'stock_entry',
            'users'
        ]

        print(f"\nTotal tables found: {len(tables)}")
        print(f"Expected tables: {len(expected_tables)}")
        print("-" * 60)

        if len(tables) == 0:
            print("\nSTATUS: NO TABLES FOUND")
            print("ACTION REQUIRED: Run migrations 001-009")
            print("-" * 60)
        else:
            print("\nTables in database:")
            found_tables = [t[0] for t in tables]

            for expected in expected_tables:
                if expected in found_tables:
                    print(f"  [OK] {expected}")
                else:
                    print(f"  [MISSING] {expected}")

            # Show extra tables (if any)
            extra_tables = set(found_tables) - set(expected_tables)
            if extra_tables:
                print("\nExtra tables found:")
                for table in extra_tables:
                    print(f"  [EXTRA] {table}")

        # Check for triggers
        print("\n" + "=" * 60)
        print("CHECKING TRIGGERS")
        print("=" * 60)

        cur.execute("""
            SELECT trigger_name, event_object_table
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
            ORDER BY trigger_name;
        """)
        triggers = cur.fetchall()

        if triggers:
            print(f"\nTriggers found: {len(triggers)}")
            for trigger in triggers:
                print(f"  - {trigger[0]} on {trigger[1]}")
        else:
            print("\nNo triggers found (migration 009 may not be run)")

        # Check test data
        print("\n" + "=" * 60)
        print("CHECKING TEST DATA")
        print("=" * 60)

        if 'client_entry' in found_tables:
            cur.execute("SELECT COUNT(*) FROM client_entry;")
            client_count = cur.fetchone()[0]
            print(f"\nClients in database: {client_count}")

            if client_count > 0:
                cur.execute("SELECT client_name, email FROM client_entry LIMIT 5;")
                clients = cur.fetchall()
                for client in clients:
                    print(f"  - {client[0]} ({client[1]})")

        if 'users' in found_tables:
            cur.execute("SELECT COUNT(*) FROM users;")
            user_count = cur.fetchone()[0]
            print(f"\nUsers in database: {user_count}")

            if user_count > 0:
                cur.execute("SELECT email, role FROM users LIMIT 5;")
                users = cur.fetchall()
                for user in users:
                    print(f"  - {user[0]} (Role: {user[1]})")

        print("\n" + "=" * 60)

        # Final summary
        if len(tables) == len(expected_tables):
            print("STATUS: ALL TABLES CREATED SUCCESSFULLY!")
        elif len(tables) == 0:
            print("STATUS: DATABASE IS EMPTY - RUN MIGRATIONS")
        else:
            print(f"STATUS: PARTIAL - {len(tables)}/{len(expected_tables)} tables found")

        print("=" * 60)

        conn.close()

    except Exception as e:
        print("=" * 60)
        print("ERROR CONNECTING TO DATABASE")
        print("=" * 60)
        print(f"Error: {e}")
        print("\nPossible causes:")
        print("1. Database migrations not run yet")
        print("2. Connection string incorrect")
        print("3. Database not accessible")
        print("=" * 60)

if __name__ == "__main__":
    check_database()
