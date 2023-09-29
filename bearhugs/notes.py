import datetime
import glob
import json
import os
import re
import sqlite3
import uuid

from langchain.document_loaders import JSONLoader


HOME = os.getenv('HOME', '')
bear_db = os.path.join(
    HOME, 'Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite')


def contains_sensitive_info(note_text: str) -> bool:
    sensitive_keywords = [
        'keys',
        'password',
        'passwords',
        'pw',
        'login',
        'username',
        'credentials',
        'secret',
        'auth',
        'token',
        'api_key',
        'access_token',
        'bearer',
        'passwd',
        'pwd',
        'credit card',
        'cc',
        'creditcard'
    ]

    lower_text = note_text.lower()

    for keyword in sensitive_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', lower_text):
            return True
    return False


def get_notes() -> dict:
    notes = []
    note_count = 0
    sensitive_note_count = 0
    with sqlite3.connect(bear_db) as conn:
        conn.row_factory = sqlite3.Row
        query = "SELECT * FROM `ZSFNOTE` WHERE `ZTRASHED` LIKE '0'"
        c = conn.execute(query)
    for row in c:
        title = row['ZTITLE']
        md_text = row['ZTEXT']
        creation_date = row['ZCREATIONDATE']
        modified = row['ZMODIFICATIONDATE']
        uuid = row['ZUNIQUEIDENTIFIER']

        if md_text and not contains_sensitive_info(md_text):
            notes.append({
                "title": title,
                "text": md_text,
                "creation_date": creation_date,
                "modified": modified,
                "uuid": uuid
            })
            note_count += 1
        else:
            sensitive_note_count += 1

    print(f'\nRetrieved {note_count} notes from Bear. Omitted {sensitive_note_count} notes containing potentially sensitive information.\n')
    return {'notes': notes, 'note_count': note_count}

# get all notes from the local sqlite database on MacOS


def export_notes_as_json() -> dict:
    notes_response = get_notes()
    note_count = notes_response['note_count']
    notes = notes_response['notes']

    file_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    export_directory = os.path.join('data', 'note_exports')
    if not os.path.exists(export_directory):
        os.makedirs(export_directory)

    export_file = os.path.join(export_directory,
                               f'bear_export_{file_timestamp}.json')

    with open(export_file, 'w') as json_file:
        json.dump(notes, json_file, indent=4)

    return {'note_count': note_count, 'export_file': export_file}


def export_notes_as_markdown() -> dict:
    notes_response = get_notes()
    note_count = notes_response['note_count']
    notes = notes_response['notes']

    export_directory = os.path.join('data', 'note_exports', 'markdown')
    if not os.path.exists(export_directory):
        os.makedirs(export_directory)

    # purge old files
    print('Purging old markdown files...')
    for old_file in glob.glob(os.path.join(export_directory, "*.md")):
        os.remove(old_file)

    for note in notes:
        if 'aws keys' in note.get('title').lower():
            print(note)
        filename = f"note_{uuid.uuid4().hex}.md"
        filepath = os.path.join(export_directory, filename)

        with open(filepath, "w") as file:
            if note.get("text"):
                file.write(note["text"])

    return {'note_count': note_count, 'export_directory': export_directory}
