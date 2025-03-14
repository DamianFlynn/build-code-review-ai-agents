# .github/scripts/process_pr_review.py

import os
import sys
import subprocess
from icecream import ic

# Add root directory to Python path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

# Now import from the root directory
from build_code_review_ai_agents import PRReviewAgent

def main():
    pr_number = os.getenv('PR_NUMBER')
    if not pr_number:
        ic("Error: PR_NUMBER environment variable not set")
        exit(1)

    try:
        ic(f"Root directory: {root_dir}")
        ic(f"Current working directory: {os.getcwd()}")

        # List directory contents for debugging
        ic("Directory contents:", os.listdir("."))
        if os.path.exists("recommit"):
            ic("recommit directory contents:", os.listdir("recommit"))

        # Initialize PR Review Agent
        pr_reviewer = PRReviewAgent(
            "pr reviewer",
            "Review and manage pull request",
            "recommit/main.tf"
        )

        # Handle PR review process
        pr_reviewer.handle_pr(pr_number)

    except Exception as e:
        ic(f"Error in PR review process: {e}")
        exit(1)

if __name__ == "__main__":
    main()
