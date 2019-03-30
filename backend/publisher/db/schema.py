from backend.publisher.db.helper import connect


def create_schema():
    conn = connect()
    cursor = conn.cursor()

    """
    tbl_files
        -> tbl_labels
        -> tbl_parentsCollection
        -> tbl_userPermission
    """
    cursor.execute("""
        CREATE TABLE tbl_files if not exists (
            token TEXT,
            username TEXT,
            password TEXT,
        );
        """)

    cursor.execute("""
        CREATE TABLE tbl_pages if not exists (
            token TEXT,
            id  TEXT,
            name TEXT,
        );
        """)
    conn.commit()
    cursor.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        print("creating database")
        create_schema()
        print("done")
    else:
        print("usage: ./schema.py create")
