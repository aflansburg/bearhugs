import argparse
import os
import glob

from bearhugs.notes import export_notes_as_json
from bearhugs.notes import export_notes_as_markdown
from bearhugs.json_toolchain import load_and_execute_json_chain
from bearhugs.utils import get_open_ai_key


def main():
    open_ai_api_key = get_open_ai_key()

    export_files = sorted(glob.glob(os.path.join(
        'data', 'note_exports', 'json', 'bear_export_*.json')), reverse=True)

    if export_files:
        user_input = input(
            f"An existing Bear notes export '{export_files[0]}' was found. Would you like to use it? (yes/no): ")
        if user_input.lower() in ['yes', 'y']:
            notes_filepath = export_files[0]
        else:
            notes_filepath = perform_export()
    else:
        notes_filepath = perform_export()

    while True:
        try:
            query = input('Enter a query (or press CTRL+C to exit): ')

            response = load_and_execute_json_chain(
                file_path=notes_filepath,
                open_ai_api_key=open_ai_api_key,
                query=query
            )

            print(response)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


def perform_export():
    """Handles the note exporting process and returns the export file path."""
    export_result = export_notes_as_json()

    if not export_result['note_count'] or not os.path.exists(export_result['export_file']):
        print("No note export found. Check to ensure Bear is installed and has notes.")
        exit()

    print(
        f"Exported {export_result['note_count']} notes to {export_result['export_file']}")
    return export_result['export_file']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Export notes to markdown.")

    parser.add_argument(
        "command",
        nargs='?',
        default="default-command",
        help="Command to run. Use 'export-markdown' to export notes as markdown files or provide no argument to run the main app."
    )

    args = parser.parse_args()

    if args.command == "export-markdown":
        md_export_result = export_notes_as_markdown()
        print(
            f'Exported {md_export_result["note_count"]} notes as markdown to {md_export_result["export_directory"]}.'
        )
    else:
        main()
