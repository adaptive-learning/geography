# -*- coding: utf-8 -*-
import csv


def dump_cursor(cursor, dest_file, append=False, **field_mapping):
    headers = [field_mapping.get(col[0], col[0]) for col in cursor.description]
    with open(dest_file, 'a' if append else 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in cursor:
            row = [val.encode('utf-8') if isinstance(val, unicode) else val for val in row]
            writer.writerow(row)
            row = cursor.fetchone()
