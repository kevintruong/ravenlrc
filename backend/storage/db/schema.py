from backend.storage.db.helper import connect


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
        CREATE TABLE tbl_files (
            createdDate TEXT,
            description TEXT,
            downloadUrl TEXT,
            etag TEXT,
            fileExtension TEXT,
            fileSize TEXT,
            id TEXT PRIMARY KEY,
            kind TEXT,
            lastViewedDate TEXT,
            md5Checksum TEXT,
            mimeType TEXT,
            modifiedByMeDate TEXT,
            modifiedDate TEXT,
            title TEXT
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
