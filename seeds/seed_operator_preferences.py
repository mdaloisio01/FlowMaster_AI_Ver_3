# seeds/seed_operator_preferences.py

def seed_operator_preferences():
    return {
        "system": "operator_preferences",
        "description": "Defines preferences, toggles, and environment settings for the operator of this Will instance.",
        "version": "1.0",
        "tags": ["core", "operator", "settings"],
        "values": {
            "preferred_language": "en",
            "debug_mode": True,
            "auto_backup": True,
            "reflex_autoload": True,
            "default_prompt_mode": "structured"
        }
    }