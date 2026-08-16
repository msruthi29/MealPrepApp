"""
Feedback audit logging for meal plan modifications.
"""
import os
from datetime import datetime
from typing import List, Optional
import json


FEEDBACK_FILE = "feedback.txt"


def ensure_feedback_file_exists():
    """Create feedback.txt if it doesn't exist."""
    if not os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "w") as f:
                f.write("")
        except Exception as e:
            print(f"Warning: Could not create feedback.txt: {e}")


def append_feedback_entry(
    plan_type: str,
    feedback_message: str,
    inclusions: Optional[List[str]] = None,
    exclusions: Optional[List[str]] = None,
    plan_regenerated: bool = False
) -> bool:
    """
    Append a feedback entry to the audit log.
    
    Args:
        plan_type: "Baby" or "Adult"
        feedback_message: User's feedback text
        inclusions: Foods to include
        exclusions: Foods to exclude
        plan_regenerated: Whether the plan was regenerated
    
    Returns:
        True if successful
    """
    ensure_feedback_file_exists()
    
    try:
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "plan_type": plan_type,
            "feedback": feedback_message,
            "inclusions": inclusions or [],
            "exclusions": exclusions or [],
            "plan_regenerated": plan_regenerated
        }
        
        with open(FEEDBACK_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return True
    except Exception as e:
        print(f"Error writing to feedback.txt: {e}")
        return False


def load_feedback_entries() -> List[dict]:
    """
    Load all feedback entries from the audit log.
    
    Returns:
        List of feedback entries
    """
    ensure_feedback_file_exists()
    
    entries = []
    try:
        with open(FEEDBACK_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue
    except Exception as e:
        print(f"Error reading feedback.txt: {e}")
    
    return entries


def get_feedback_file_content() -> str:
    """
    Get the raw content of the feedback file for download.
    
    Returns:
        File content as string
    """
    ensure_feedback_file_exists()
    
    try:
        with open(FEEDBACK_FILE, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading feedback file: {e}"


def clear_feedback_file() -> bool:
    """
    Clear the feedback file (rarely needed, but available for testing).
    
    Returns:
        True if successful
    """
    try:
        with open(FEEDBACK_FILE, "w") as f:
            f.write("")
        return True
    except Exception as e:
        print(f"Error clearing feedback.txt: {e}")
        return False
