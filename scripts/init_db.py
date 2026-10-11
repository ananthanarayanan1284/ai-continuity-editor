"""Connect to Neo4j and create the story-bible constraints and indexes.

Safe to run repeatedly: every statement uses IF NOT EXISTS.

    python scripts/init_db.py
"""

from continuity_editor.graph import Neo4jConnection, apply_schema, describe_schema


def main() -> None:
    with Neo4jConnection() as conn:
        info = conn.verify()
        print(f"Connected to {info['agent']} at {info['address']}")

        added = apply_schema(conn)
        print(f"Constraints added: {added['constraints_added']}, indexes added: {added['indexes_added']}")

        schema = describe_schema(conn)
        print("\nConstraints:")
        for row in schema["constraints"]:
            print(f"  {row['name']:<22} {row['labels']} {row['properties']}")
        print("\nIndexes:")
        for row in schema["indexes"]:
            print(f"  {row['name']:<22} {row['type']:<9} {row['labels']} {row['properties']} {row['state']}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        raise SystemExit(f"Error: {exc}")
