import os
import csv
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the directory exists

# 📌 Helper function to get full file path
def get_file_path(filename):
    return os.path.join(DATA_DIR, filename)

# ✅ 1. Create a New JSON or CSV File
@app.route("/create_file", methods=["POST"])
def create_file():
    data = request.json
    filename = data.get("filename")
    filetype = data.get("filetype", "json")  # Default to JSON if not specified

    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    filepath = get_file_path(f"{filename}.{filetype}")

    if os.path.exists(filepath):
        return jsonify({"error": "File already exists"}), 409

    if filetype == "json":
        with open(filepath, "w") as f:
            json.dump({}, f)  # Initialize with an empty JSON object
    elif filetype == "csv":
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID"])  # Start with a default column

    return jsonify({"message": f"{filename}.{filetype} created successfully"}), 201

# ✅ 2. Add Data to an Existing JSON or CSV File
@app.route("/add_data", methods=["POST"])
def add_data():
    data = request.json
    filename = data.get("filename")
    entry = data.get("entry")

    if not filename or not entry:
        return jsonify({"error": "Filename and entry data required"}), 400

    filepath_json = get_file_path(f"{filename}.json")
    filepath_csv = get_file_path(f"{filename}.csv")

    if os.path.exists(filepath_json):  # JSON Mode
        with open(filepath_json, "r+") as f:
            file_data = json.load(f)
            file_data[len(file_data) + 1] = entry  # Append data with a new key
            f.seek(0)
            json.dump(file_data, f, indent=4)
    elif os.path.exists(filepath_csv):  # CSV Mode
        with open(filepath_csv, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(entry.values())  # Append new row
    else:
        return jsonify({"error": "File not found"}), 404

    return jsonify({"message": f"Data added to {filename}"}), 200

# ✅ 3. Remove Data from JSON or CSV File
@app.route("/remove_data", methods=["POST"])
def remove_data():
    data = request.json
    filename = data.get("filename")
    key_to_remove = data.get("key")  # Key (for JSON) or row ID (for CSV)

    if not filename or key_to_remove is None:
        return jsonify({"error": "Filename and key required"}), 400

    filepath_json = get_file_path(f"{filename}.json")
    filepath_csv = get_file_path(f"{filename}.csv")

    if os.path.exists(filepath_json):  # JSON Mode
        with open(filepath_json, "r+") as f:
            file_data = json.load(f)
            if key_to_remove in file_data:
                del file_data[key_to_remove]
                f.seek(0)
                f.truncate()
                json.dump(file_data, f, indent=4)
            else:
                return jsonify({"error": "Key not found"}), 404
    elif os.path.exists(filepath_csv):  # CSV Mode
        rows = []
        with open(filepath_csv, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = [row for row in reader if row[0] != str(key_to_remove)]  # Remove matching row

        with open(filepath_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

    return jsonify({"message": f"Entry removed from {filename}"}), 200

# ✅ 4. Add a New Column to a CSV File
@app.route("/add_column", methods=["POST"])
def add_column():
    data = request.json
    filename = data.get("filename")
    new_column_name = data.get("column_name")

    if not filename or not new_column_name:
        return jsonify({"error": "Filename and column name required"}), 400

    filepath_csv = get_file_path(f"{filename}.csv")

    if os.path.exists(filepath_csv):
        with open(filepath_csv, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if new_column_name in rows[0]:  # Column already exists
            return jsonify({"error": "Column already exists"}), 409

        rows[0].append(new_column_name)  # Add new column to header

        for row in rows[1:]:  # Extend existing rows
            row.append("")

        with open(filepath_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        return jsonify({"message": f"Column '{new_column_name}' added to {filename}.csv"}), 200

    return jsonify({"error": "CSV file not found"}), 404

# ✅ 5. Modify a Specific Entry
@app.route("/modify_entry", methods=["POST"])
def modify_entry():
    data = request.json
    filename = data.get("filename")
    key_to_modify = data.get("key")
    new_value = data.get("new_value")

    if not filename or key_to_modify is None or new_value is None:
        return jsonify({"error": "Filename, key, and new value required"}), 400

    filepath_json = get_file_path(f"{filename}.json")

    if os.path.exists(filepath_json):  # JSON Mode
        with open(filepath_json, "r+") as f:
            file_data = json.load(f)
            if key_to_modify in file_data:
                file_data[key_to_modify] = new_value
                f.seek(0)
                f.truncate()
                json.dump(file_data, f, indent=4)
                return jsonify({"message": f"Entry updated in {filename}.json"}), 200
            return jsonify({"error": "Key not found"}), 404

    return jsonify({"error": "File not found"}), 404

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
