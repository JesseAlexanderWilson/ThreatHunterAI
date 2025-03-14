import csv
import json
import random
from collections import defaultdict

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

def generate_interrogation_scenario(attack):
    """Generates an interrogation-style scenario based on the selected attack and user skill level."""
    difficulty_level = attack_stats.get(attack, {}).get("correct", 0)  # Track correct answers
    
    # Victim scenarios
    victim_easy = [
        f"My account was drained right after I entered my banking password on a link I got via email...",
        f"I got an email saying I needed to reset my work password. It looked real, but now I’m locked out...",
        f"Our website suddenly has pop-ups for sketchy ads. We never put those there!"
    ]
    
    victim_harder = [
        f"My company’s internal documents were leaked, but no one noticed a breach. Could something be wrong with our email system?",
        f"I received a phone call from ‘IT Support’ asking me to confirm my credentials. It seemed legit, but now I can’t log in...",
        f"A customer reported that they entered their login details on our website, but they’re getting errors now..."
    ]
    
    # Attacker confession scenarios
    attacker_easy = [
        f"It was simple. I sent them a phishing email, and they just gave me their password. Too easy.",
        f"I replaced some JavaScript on their site, so every visitor gave me their credentials without realizing.",
        f"They stored their API keys in a public repo. I just used them to access their cloud storage."
    ]
    
    attacker_harder = [
        f"You think you know what I did? Maybe I used malware… or maybe it was just social engineering. You’ll have to figure that out.",
        f"Hah, I didn’t do anything illegal. I just took what they left open. Who leaves admin access exposed like that?",
        f"Maybe I injected my code into their login page. Or maybe I just guessed their weak passwords. You tell me."
    ]
    
    attacker_deceptive = [
        f"You think I stole credentials? Nah, I just… convinced them to hand them over willingly.",
        f"Look, all I did was ‘borrow’ their login session. No need for a hack when they left the door open.",
        f"Pfft, you’re barking up the wrong tree. Maybe their IT guy did it. Or was it an insider?"
    ]

    # Select difficulty-based responses
    if difficulty_level < 2:
        return random.choice(victim_easy + attacker_easy)
    elif difficulty_level < 5:
        return random.choice(victim_harder + attacker_harder)
    else:
        return random.choice(attacker_deceptive)  # Misleading responses for experts

def run_interrogation():
    """Runs the cyber attack interrogation process."""
    attack = get_next_attack()
    print("\n🔍 **INTERROGATION SCENARIO:**")
    print(generate_interrogation_scenario(attack))
    
    # User's guess
    guess = input("\nWhat type of attack do you think this is? ").strip()

    # Check the answer
    correct = guess.lower() == attack.lower()
    update_attack_progress(attack, correct, guessed_attack=guess if not correct else None)

    if correct:
        print("\n✅ Correct! You identified the attack.")
    else:
        print(f"\n❌ Incorrect. The correct answer was: {attack}")

def show_performance_report():
    """Displays a summary of the user's progress."""
    print("\n📊 **Performance Report** 📊")
    print(f"{'Attack':<30} {'Correct':<10} {'Incorrect':<10} {'Mistaken For'}")
    print("=" * 70)
    
    for attack, stats in attack_stats.items():
        incorrect_guesses = "; ".join(stats["incorrect_guesses"]) if stats["incorrect_guesses"] else "-"
        print(f"{attack:<30} {stats['correct']:<10} {stats['incorrect']:<10} {incorrect_guesses}")
    
    print("\n✅ Keep going! The system will continue adapting to challenge you.")

# run_interrogation()
show_performance_report()