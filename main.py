import csv
import json
import random
from collections import defaultdict
from flask import Flask, jsonify, request # type: ignore

# Flask app setup
app = Flask(__name__)

# Load attack dataset from CSV
attack_data_file = "Cyber Attack Types.csv"
attack_stats_file = "attack_progress.json"

# Initialize tracking structure
attack_stats = defaultdict(lambda: {"correct": 0, "incorrect": 0, "incorrect_guesses": []})

def load_attack_data():
    """Loads the attack dataset from the CSV file."""
    attacks = []
    with open(attack_data_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            attacks.append(row["Attack"].strip())  # Ensure column name matches your CSV
    return attacks

def load_attack_stats():
    """Loads user progress from a JSON file (if exists)."""
    try:
        with open(attack_stats_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_attack_stats():
    """Saves the current attack progress to a JSON file."""
    with open(attack_stats_file, "w") as f:
        json.dump(attack_stats, f, indent=4)

def update_attack_progress(attack, correct, guessed_attack=None):
    """Updates the stats for a given attack based on user's response."""
    if correct:
        attack_stats[attack]["correct"] += 1
    else:
        attack_stats[attack]["incorrect"] += 1
        if guessed_attack and guessed_attack not in attack_stats[attack]["incorrect_guesses"]:
            attack_stats[attack]["incorrect_guesses"].append(guessed_attack)
    save_attack_stats()

def get_next_attack():
    """Selects the next attack based on user's progress to optimize learning."""
    min_attempts = 2  # Minimum incorrect attempts before prioritizing an attack
    high_correct_threshold = 5  # If answered correctly this many times, deprioritize

    # Filter attacks into categories
    new_attacks = [a for a in attack_list if a not in attack_stats]
    struggling_attacks = [a for a in attack_stats if attack_stats[a]["incorrect"] >= min_attempts]
    mastered_attacks = [a for a in attack_stats if attack_stats[a]["correct"] >= high_correct_threshold]

    # Select from priority order: 1) New attacks 2) Struggled attacks 3) Random fallback
    if new_attacks:
        return random.choice(new_attacks)
    elif struggling_attacks:
        return random.choice(struggling_attacks)
    else:
        available_attacks = list(set(attack_list) - set(mastered_attacks))
        return random.choice(available_attacks) if available_attacks else random.choice(attack_list)

# Load initial data
attack_list = load_attack_data()
attack_stats.update(load_attack_stats())

@app.route("/next_attack", methods=["GET"])
def api_get_next_attack():
    """API endpoint to get the next attack to test."""
    return jsonify({"next_attack": get_next_attack()})

@app.route("/update_progress", methods=["POST"])
def api_update_progress():
    """API endpoint to update the attack progress."""
    data = request.json
    attack = data.get("attack")
    correct = data.get("correct", False)
    guessed_attack = data.get("guessed_attack", None)
    
    if not attack:
        return jsonify({"error": "Missing attack name"}), 400
    
    update_attack_progress(attack, correct, guessed_attack)
    return jsonify({"message": "Progress updated successfully"})

@app.route("/performance_report", methods=["GET"])
def api_performance_report():
    """API endpoint to fetch the user's performance report."""
    report = {}
    for attack, stats in attack_stats.items():
        report[attack] = {
            "correct": stats["correct"],
            "incorrect": stats["incorrect"],
            "incorrect_guesses": "; ".join(stats["incorrect_guesses"]) if stats["incorrect_guesses"] else "-"
        }
    return jsonify(report)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
