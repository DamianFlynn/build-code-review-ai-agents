# from openai import OpenAI
import os
import time
from icecream import ic
import shutil
import tiktoken
import openai
import subprocess
import json

# Configuration
MAX_RETRIES = 5  # Maximum number of retries when rate limit is hit
RETRY_DELAY = 5  # Initial delay in seconds for retrying requests

# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
openai.api_key = os.getenv('OPENAI_API_KEY')

if not openai.api_key:
    raise Exception("OpenAI API key is required to run this script.")

# Tokenizer Setup
encoder = tiktoken.encoding_for_model("gpt-4")

# Tool for reading the file (simulating FileReadTool)
def file_read_tool(file_path):
    # Check if file exists before reading
    if not os.path.exists(file_path):
        ic(f"File {file_path} does not exist. Attempting to create it.")
        # Copy from input if recommit file doesn't exist
        if file_path == "recommit/main.tf":
            if not os.path.exists("inputs/main.tf"):
                raise FileNotFoundError("The source file 'inputs/main.tf' does not exist.")
            if not os.path.exists("recommit"):
                os.makedirs("recommit")
            shutil.copy("inputs/main.tf", "recommit/main.tf")
            ic(f"Copied 'inputs/main.tf' to 'recommit/main.tf'")
        else:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    ic(f"Reading file: {file_path}")
    with open(file_path, 'r') as file:
        content = file.readlines()
    return content

# Base Agent Class
class Agent:
    def __init__(self, role, goal, file_path):
        self.role = role
        self.goal = goal
        self.file_path = file_path
        ic(f"Initializing Agent with role: {self.role}, goal: {self.goal}, file: {self.file_path}")
        self.content = file_read_tool(file_path)

    def review(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def estimate_tokens(self, prompt):
        tokens = len(encoder.encode(prompt))
        ic(f"Estimated tokens for prompt: {tokens}")
        return tokens

    def log_token_forecast(self, tokens):
        log_path = "outputs/tokenforecasts.log"
        if not os.path.exists("outputs"):
            os.makedirs("outputs")
        with open(log_path, 'a') as log_file:
            log_file.write(f"Estimated tokens: {tokens}\n")
        ic(f"Logged token forecast to: {log_path}")

    def generate_comments(self, prompt):
        retry_count = 0
        estimated_tokens = self.estimate_tokens(prompt)
        self.log_token_forecast(estimated_tokens)
        ic(f"Estimated cost for {estimated_tokens} tokens")

        while retry_count < MAX_RETRIES:
            try:
                ic(f"Generating comments with prompt: {prompt[:100]}...")  # Print the first 100 characters of the prompt for debugging
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                ic(f"Received response: {response}")
                return response.choices[0].message.content.strip()

            # except openai.error.RateLimitError as e:
            except openai.error.RateLimitError as e:
                retry_count += 1
                ic(f"Rate limit error occurred (attempt {retry_count}): {e}")
                time.sleep(RETRY_DELAY * retry_count)  # Exponential backoff

        # If all retries are exhausted
        return "Unable to generate comment due to rate limit."

# Specialized Agents

# Syntax Agent
class SyntaxAgent(Agent):
    def review(self):
        ic(f"Reviewing syntax for file: {self.file_path}")
        issues = []
        prompt = "Identify any syntax issues in the following Terraform code:\n\n" + "".join(self.content)
        comments = self.generate_comments(prompt)
        issues.append(comments)
        return issues

# Best Practices Agent
class BestPracticesAgent(Agent):
    def review(self):
        ic(f"Reviewing best practices for file: {self.file_path}")
        issues = []
        prompt = "Check the following Terraform code for best practice violations, such as hardcoded secrets or missing tags:\n\n" + "".join(self.content)
        comments = self.generate_comments(prompt)
        issues.append(comments)
        return issues

# Optimization Agent
class OptimizationAgent(Agent):
    def review(self):
        ic(f"Reviewing optimizations for file: {self.file_path}")
        issues = []
        prompt = "Review the following Terraform code for any optimization suggestions related to resource usage or cost reduction:\n\n" + "".join(self.content)
        comments = self.generate_comments(prompt)
        issues.append(comments)
        return issues

# Markdown Formatter Agent
class MarkdownFormatterAgent(Agent):
    def format_to_markdown(self, content):
        ic(f"Formatting review content to Markdown.")
        prompt = f"Convert the following text into well-formatted Markdown:\n\n{content} and do not include any backticks"
        markdown_content = self.generate_comments(prompt)
        return markdown_content

# Writing Comments to New File
class ReviewAgentWithComments(Agent):
    def comment(self, issues):
        ic(f"Adding comments to file: {self.file_path}")
        report_path = "outputs/review_report.md"
        output_path = "recommit/main.tf"
        report_content = "\n".join(issues)

        # Generate Markdown content
        markdown_agent = MarkdownFormatterAgent("markdown formatter", "Format review report to Markdown", self.file_path)
        markdown_content = markdown_agent.format_to_markdown(report_content)

# Write comments to report file
        with open(report_path, 'w') as report_file:
                report_file.write(markdown_content)
        ic(f"Writing review report to: {report_path}")

        # Add inline comments to the HCL file
        ic("Starting to add inline comments to the HCL file.")
        added_lines = set()

        # Iterate in reverse to avoid affecting line numbers while inserting comments
        for i in range(len(self.content) - 1, -1, -1):
            line = self.content[i]
            ic(f"Processing line {i + 1}: {line.strip()}")
            if (line.strip().startswith("resource") or line.strip().startswith("module") or line.strip().startswith("data")) and i not in added_lines:
                # Extract only the block starting at the current line
                block_lines = [line]
                j = i + 1
                while j < len(self.content) and self.content[j].strip() and not self.content[j].strip().startswith(('resource', 'module', 'data')):
                    block_lines.append(self.content[j])
                    j += 1
                block_content = "".join(block_lines)

                # Generate a concise comment for the current block only
                block_prompt = f"Provide a very short, one-sentence description of the following Terraform block only:\n\n{block_content}"
                comment = self.generate_comments(block_prompt)

                # Insert the generated comment above the current block
                comment_line = f"# {comment}\n"
                self.content.insert(i, comment_line)
                added_lines.add(i)
                ic(f"Added comment to line {i + 1}: {comment.strip()}")

        # Writing the reviewed content to output file
        ic(f"Writing reviewed content to: {output_path}")
        with open(output_path, 'w') as file:
            file.writelines(self.content)
        ic("Finished writing reviewed content to the output file.")

class PRReviewAgent(Agent):
    def __init__(self, role, goal, file_path, model="gpt-4"):
        super().__init__(role, goal, file_path)
        self.model = model

    def ensure_file_exists(self):
        """Ensure the target file exists and has content"""
        ic(f"Checking file: {self.file_path}")

        if not os.path.exists(self.file_path):
            ic(f"File {self.file_path} not found")
            # Check if file exists in PR directory
            pr_file_path = os.path.join(os.getcwd(), self.file_path)
            if os.path.exists(pr_file_path):
                ic(f"Found file at {pr_file_path}")
                self.file_path = pr_file_path
            else:
                raise FileNotFoundError(f"Could not find {self.file_path} in any location")

        with open(self.file_path, 'r') as f:
            content = f.read()
            if not content.strip():
                raise ValueError(f"File {self.file_path} is empty")

        return True

    def validate_comments(self):
        """Check if each Terraform block has a comment"""
        ic("Validating Terraform block comments")

        # Ensure file exists before proceeding
        self.ensure_file_exists()

        # Read the actual content from the PR
        with open(self.file_path, 'r') as f:
            self.file_content = f.read()

        ic(f"File content length: {len(self.file_content)}")
        ic(f"First 100 chars: {self.file_content[:100]}")

        prompt = f"""Review this Terraform code and check ONLY if EACH resource, module, or data block has a # comment directly above it.

    IMPORTANT:
    - ONLY check for the existence of comments above resource, module, or data blocks
    - Ignore comment content/accuracy completely
    - Ignore locals blocks completely
    - Return ONLY 'yes' if ALL resource/module/data blocks have a comment
    - Return ONLY 'no' if ANY resource/module/data block is missing a comment

    Code to review:
    {self.file_content}"""

        validation_result = self.generate_comments(prompt)
        ic(f"Comment validation result: {validation_result}")

        # Simplified return without detailed validation
        return {
            "valid": validation_result.lower().strip() == "yes",
            "details": "All resource, module, and data blocks have comments" if validation_result.lower().strip() == "yes"
                    else "Some resource, module, or data blocks are missing comments"
        }

    def handle_pr(self, pr_number):
        """Handle PR based on comment validation"""
        ic(f"Starting PR review process for PR #{pr_number}")

        try:
            # Get PR details
            pr_info = subprocess.run(
                ['gh', 'pr', 'view', pr_number, '--json', 'author,headRepository'],
                capture_output=True, text=True, check=True
            )
            pr_data = json.loads(pr_info.stdout)

            # Validate comments with detailed feedback
            result = self.validate_comments()

            # Create simplified status message
            status_message = f"""## Terraform Comment Review Results

    {"✅ All resource, module, and data blocks have comments." if result["valid"] else "❌ Some resource, module, or data blocks are missing comments."}

    ### Details
    {result["details"]}

    File reviewed: `{self.file_path}`"""

            # Add comment to PR
            subprocess.run([
                'gh', 'pr', 'comment', pr_number,
                '--body', status_message
            ], check=True)

            # If validation passed, try to merge
            if result["valid"]:
                try:
                    subprocess.run([
                        'gh', 'pr', 'merge', pr_number,
                        '--squash',
                        '--delete-branch'
                    ], check=True)
                    ic("✅ PR approved and merged successfully!")
                except subprocess.CalledProcessError as e:
                    ic(f"Unable to merge PR: {e}")
            else:
                ic("❌ Validation failed - PR needs updates")

        except Exception as e:
            ic(f"Error in PR process: {e}")
            raise

# Testing the Agents
if __name__ == "__main__":
    ic("Starting testing of agents")

    # Initialize agents using the original input file
    syntax_agent = SyntaxAgent("code analyzer", "Identify syntax issues", "inputs/main.tf")
    best_practices_agent = BestPracticesAgent("best practices checker", "Identify best practices violations", "inputs/main.tf")
    optimization_agent = OptimizationAgent("optimization checker", "Suggest optimizations", "inputs/main.tf")

    agents = [syntax_agent, best_practices_agent, optimization_agent]
    all_issues = []
    for agent in agents:
        ic(f"Running review for agent: {agent.role}")
        issues = agent.review()
        all_issues.extend(issues)
        ic(f"Issues found by {agent.role}: {issues}")

    # Adding comments to the file in the recommit directory
    review_agent_with_comments = ReviewAgentWithComments("commenter", "Add comments to file", "recommit/main.tf")
    review_agent_with_comments.comment(all_issues)
    ic(f"completed testing of agent. please check the file output artifacts... thank you")

# end of code... now lets run this thing and see if it works :-)
#
# it worked :-) next video, we will continue to move this to a pipeline, on our way to full lifecycle automation for code reviews...
