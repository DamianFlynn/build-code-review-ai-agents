
# build code review ai agents youtube series!

This repository contains code for building custom AI AGENTS to automate code reviews on Infrastructure-as-Code (IaC) files, and starting with Terraform code. The AI agents are built using custom classes in Python and use the OpenAI API to generate comments on syntax, best practices, and optimization suggestions. This project serves as the codebase for the video tutorial series, “How to Build AI Agents to Review Your Code Using Custom Python Classes Only!”

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Example Terraform Code](#example-terraform-code)
- [Part 1: Running Locally](#part-1-running-locally)
- [Part 2: GitHub Actions Pipeline Setup](#part-2-github-actions-pipeline-setup)
- [Part 3: PR Review and Full Automation](#part-3-pr-review-and-full-automation)
- [Next Steps](#next-steps)

## Overview
This repository includes a complete automation pipeline for AI-driven code reviews:
1. **Part 1**: Local setup of AI review agents in Python to analyze and comment on Terraform code.
2. **Part 2**: GitHub Actions pipeline to automate code reviews and generate pull requests with the reviewed code.
3. **Part 3**: PR Review Agent to validate inline comments and fully automate PR reviews and merges.

## Features
- Automated syntax checks, best practice validation, and optimization suggestions.
- Uses the OpenAI API to generate human-readable comments.
- Adds inline comments to Terraform code for easy review.
- Custom AI AGENTS including a PR Review Agent for full pipeline automation against pull request and merging to main branch!

## Prerequisites
- Python 3.7 or later
- An OpenAI API key (set as an environment variable)
- GitHub CLI (`gh`) installed and authenticated

## Bonus
- Copilot subscription

## Tools Used

This project was developed and tested using the following tools:

- **Python**: v3.13
- **pip**: v24.2
- **Nushell**: A modern shell environment for productivity
- **Zed IDE**: A lightweight and efficient code editor for streamlined development
- **Git**: 2.47.0
- **GitHub CLI**: For pull request and repository management
- **GitHub Copilot**: subscription

Make sure to have similar versions or compatible setups for the best results when following along.

## Setup Instructions

### Step 1: Clone the Repository
First, clone this repository to your local machine:
```bash
git clone https://github.com/talkitdoit/build-code-review-ai-agents.git
cd build-code-review-ai-agents
```

### Step 2: Create Required Directories and Files
Make sure the required directories and input files are set up:
```bash
# Create necessary directories
mkdir -p inputs recommit outputs && touch inputs/main.tf

# Place your Terraform code in `inputs/main.tf`
# An example Terraform file is provided in this repository.
```

### Step 3: Install Python and pip (if not already installed)
Ensure you have Python and pip installed. You can verify with:
```bash
python3 --version
pip3 --version
```

If not installed, follow [Python’s official installation guide](https://www.python.org/downloads/).

### Step 4: Set the OpenAI API Key
Export your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY='your_openai_api_key'
```

### Step 5: Set Up Python Virtual Environment
Create a virtual environment to manage dependencies:
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### Step 6: Install Required Python Packages
Install the necessary packages using pip:
```bash
pip install -r requirements.txt
```

> Note: The `requirements.txt` file should include dependencies like `openai`, `icecream`, and `tiktoken`.

## Usage

### Part 1: Running Locally
To test the AI agents locally:
```bash
python build_code_review_ai_agents.py
```

### Part 2: GitHub Actions Pipeline Setup
Follow these steps to integrate the AI agents into a GitHub Actions pipeline:
1. Add the GitHub Actions workflow to `.github/workflows/build-code-review.yml`.
2. Push the workflow to the repository.
3. Trigger the workflow by pushing a code change to `main`.

### Part 3: PR Review and Full Automation
In Part 3, we added the `PR Review Agent` and fully automated the PR review and merge process. Here’s what happens:
1. The PR Review Agent checks `recommit/main.tf` for valid inline comments.
2. If validation passes, the pull request is merged automatically.
3. The review process is handled by the `process_pr_review.py` script.

#### Example GitHub Actions Workflow Addition:
```yaml
- name: Process PR Review
  if: |
    github.event_name == 'pull_request' ||
    (github.event_name == 'push' && steps.create-pr.outputs.pr_number != '')
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    python .github/scripts/process_pr_review.py
```

---

## Example Terraform Code
<details>
  <summary>Click to expand Terraform code example</summary>

```hcl
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  tags = {
    Name = "example-instance"
  }
}

module "storage_account" {
  source                      = "./modules/storage_account"
  name                        = "${local.storage_account_prefix}${random_string.storage_account_suffix.result}"
  location                    = var.location
  resource_group_name         = azurerm_resource_group.rg.name
  account_kind                = var.storage_account_kind
  account_tier                = var.storage_account_tier
  replication_type            = var.storage_account_replication_type
  tags                        = var.tags
}
```

</details>

### Expected Outcomes
1. A pull request (ai-generated-changes-pr) containing the updated Terraform code with AI-generated comments and a review report.
2. The review artifacts (e.g., review_report.md, tokenforecasts.log) are created in a seperate branch, in readiness for setting up GitHub Pages.
3. The created Pull Request, gets checked and validate, and auto-merged to the main branch. Full automation lifecycle.


## Next Steps
1. Explore the **GitHub Copilot** API for deeper automation and review capabilities.
2. Expand functionality to review additional IaC formats (e.g., CloudFormation, ARM templates).
3. Integrate analytics to track code review performance over time.

Subscribe to the YouTube channel for notification of the next videos!

## License
This project is licensed under the MIT License.

## Contact
For questions or feedback, please contact via GitHub issues or on the socials
* [youtube.com/@talkitdoit](https://youtube.com/@talkitdoit)
* [x.com/talkitdoit](https://x.com/talkitdoit)
* [tiktok.com/@talkitdoit1](https://tiktok.com/@talkitdoit1)

---

Enjoy building your AI-driven code review agents!
