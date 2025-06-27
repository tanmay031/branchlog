# File: branchlog/__main__.py
import argparse
from datetime import datetime, timedelta
from branchlog.local_git import GitRepository
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s") 

def parse_args():
    parser = argparse.ArgumentParser(description="List Git branches you worked on in the last N days.")
    parser.add_argument("--days", type=int, default=7, help="Number of past days to check")
    parser.add_argument("--author", type=str, help="Git author name (default: git config user.name)")
    parser.add_argument("--output", choices=["plain", "markdown"], default="plain", help="Output format")
    return parser.parse_args()


def render_output(summary, author, days, output_format):
    if not summary:
        logging.info(f"No commits found by '{author}' in the last {days} days.")
        return

    if output_format == "plain":
        logging.info(f"\nBranches with commits by '{author}' in the last {days} days:\n")
        for branch, count, preview in summary:
            logging.info(f"- {branch} ({count} commits, latest: {preview})")
    elif output_format == "markdown":
        logging.info(f"\n### BranchLog Report for `{author}` (last {days} days)\n")
        for branch, count, preview in summary:
            logging.info(f"- **{branch}**: {count} commits (latest: _{preview}_)\n")


def main():
    args = parse_args()
    repo = GitRepository()

    if not repo.is_valid_repo():
        logging.info("Not inside a Git repository.")
        return

    author = args.author or repo.get_user()
    since_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    branches = repo.get_local_branches()

    summary = []
    for branch in branches:
        commits = repo.get_commits(branch, author, since_date)
        if commits:
            summary.append((branch, len(commits), commits[0][:50]))

    render_output(summary, author, args.days, args.output)


if __name__ == "__main__":
    main()
