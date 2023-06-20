from git import Repo
from collections import defaultdict
import datetime
from dateutil.relativedelta import relativedelta
from os import path

def main():
    repo = Repo("/Users/sladynnunes/Rust/rust")

    # Generate the cutoff date for one year ago
    cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=365)

    # Create a defaultdict to count directory changes
    directory_changes = defaultdict(int)

    dirs_of_interest = {"compiler", "library", "src/boostrap", "src/ci", "tests"}

    # Initialize total commit count
    total_commits = 0

    # Loop through all commits in the repository
    for commit in repo.iter_commits('master'):

        print(commit.committed_datetime, commit)
        # Check if the commit date is older than the cutoff
        if commit.committed_datetime < cutoff_date:
            break

        # Check if the commit author is 'bors' and the message starts with "Auto merge" or "Rollup merge"
        if commit.author.name != 'bors' or (not commit.message.startswith("Auto merge") and not commit.message.startswith("Rollup merge")):
            continue

        # Increment total commit count
        total_commits += 1

        # Track if a directory of interest has been changed in this commit
        dir_changes_in_commit = {dir: False for dir in dirs_of_interest}
        dir_changes_in_commit["rest"] = False

        # Check each changed file in the commit
        for changed_file in commit.stats.files:
            directory = path.dirname(changed_file)
            
            # Check for each directory of interest
            for dir_of_interest in dirs_of_interest:
                if directory.startswith(dir_of_interest):
                    dir_changes_in_commit[dir_of_interest] = True
                    break
            else:
                # If none of the directories of interest were found, categorize as 'other'
                dir_changes_in_commit["rest"] = True

        # Increment the change count for directories that had changes in this commit
        for dir_of_interest, changed in dir_changes_in_commit.items():
            if changed:
                directory_changes[dir_of_interest] += 1

    # Print directories and their change count, sorted by the count
    sorted_changes = sorted(directory_changes.items(), key=lambda x: x[1], reverse=True)
    for directory, count in sorted_changes:
        percentage = (count / total_commits) * 100
        print(f'{directory}: {count} ({percentage:.2f}%)')

    # Print total number of analyzed commits
    print(f'Total analyzed commits: {total_commits}')

if __name__ == "__main__":
    main()
