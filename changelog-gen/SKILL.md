---
name: generate-changelog
description: Automatically generates a Keep-a-Changelog compliant CHANGELOG.md from git commit history, categorizing entries into Added, Fixed, Changed, and Removed.
---

# Generate Changelog Skill

When the user runs `/generate-changelog`, execute the following workflow:

1. Determine the latest git tag using `git describe --tags --abbrev=0`.
2. Extract all commits since the tag (or the entire history if no tags exist) using `git log --format="%h|%an|%as|%s"`.
3. Auto-categorize each commit into:
   - **Added:** New features, additions, or assets (`feat:`, `add:`, `new:`)
   - **Fixed:** Bug fixes, patches, or security remediations (`fix:`, `bug:`, `patch:`)
   - **Changed:** Refactoring, performance improvements, updates, chores, documentation
   - **Removed:** Deprecations, deletions, or removals (`remove:`, `drop:`, `deprecate:`)
4. Output the structured markdown according to the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standard.
5. Write the output to `CHANGELOG.md` at the project root.

### Command Execution
```bash
python -m changelog_gen.cli --output CHANGELOG.md
# OR via bash script:
bash changelog-gen/changelog.sh CHANGELOG.md
```
