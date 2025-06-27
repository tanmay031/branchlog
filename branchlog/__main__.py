# File: branchlog/__main__.py
import argparse
import subprocess
from datetime import datetime, timedelta
import os

def is_git_repo():
    return subprocess.call(["git", "rev-parse", "--is-inside-work-tree"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL) == 0

def get_git_user():
    return subprocess.getoutput("git config user.name")

def get_branches():
    result = subprocess.getoutput("git for-each-ref --format='%(refname:short)' refs/heads")
    return result.strip().split("\n")

def get_commits(branch, author, since_date):
    cmd = f'git log {branch} --since="{since_date}" --author="{author}" --oneline'
    output = subprocess.getoutput(cmd)
    return output.strip().split("\n") if output.strip() else []

def main():
    if not is_git_repo():
        print("❌ Error: Not inside a Git repository.")
        return

    parser = argparse.ArgumentParser(description="List Git branches you worked on in the last N days.")
    parser.add_argument("--days", type=int, default=7, help="Number of past days to check")
    parser.add_argument("--author", type=str, help="Git author name (default: git config user.name)")
    parser.add_argument("--output", choices=["plain", "markdown"], default="plain", help="Output format")
    args = parser.parse_args()

    author = args.author or get_git_user()
    since_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    branches = get_branches()

    summary = []

    for branch in branches:
        commits = get_commits(branch, author, since_date)
        if commits:
            summary.append((branch, len(commits), commits[0][:50]))  # First commit preview

    if not summary:
        print(f"No commits found by '{author}' in the last {args.days} days.")
        return

    if args.output == "plain":
        print(f"\nBranches with commits by '{author}' in the last {args.days} days:\n")
        for b, count, preview in summary:
            print(f"- {b} ({count} commits, latest: {preview})")
    elif args.output == "markdown":
        print(f"\n### BranchLog Report for `{author}` (last {args.days} days)\n")
        for b, count, preview in summary:
            print(f"- **{b}**: {count} commits (latest: _{preview}_)\n")

if __name__ == "__main__":
    main()
