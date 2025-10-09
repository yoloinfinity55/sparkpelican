# Pelican Blog Title Validation System

This project includes an automated system to ensure all blog post titles are properly formatted in their front matter.

## Problem
Pelican blog posts should have titles **without quotes** in their front matter:
```markdown
---
title: Your Post Title  # ✅ Correct - no quotes
---
```

But sometimes titles are written with quotes:
```markdown
---
title: "Your Post Title"  # ❌ Incorrect - has quotes
---
```

## Solution
We've implemented a comprehensive title validation system with multiple ways to check and fix title formatting.

## Available Tools

### 1. Manual Validation
Check if all titles are properly formatted:
```bash
python scripts/validate-titles.py
```

**Output when issues found:**
```
🔍 Checking 19 markdown files...

❌ Found 3 title formatting issues:
============================================================

📄 second-post.md (line 114):
   Current: Title has quotes: title: "我的未来文章"
   Fix to: Should be: title: 我的未来文章

📄 2025-10-08-project-sparkpelican-summary-v2.md (line 137):
   Current: Title has quotes: title: "Your Post Title"
   Fix to: Should be: title: Your Post Title

============================================================
💡 To fix automatically, run: python scripts/fix-titles.py

❌ Validation failed! Please fix the issues above.
```

**Output when all titles are correct:**
```
🔍 Checking 19 markdown files...
✅ All titles are properly formatted!

✅ All validations passed!
```

### 2. Automatic Fixing
Automatically fix all title formatting issues:
```bash
python scripts/fix-titles.py
```

**Output:**
```
🔧 Fixing titles in 19 markdown files...
   ✅ Fixed: second-post.md (line 114)
   ✅ Fixed: 2025-10-08-project-sparkpelican-summary-v2.md (line 137)
   ✅ Fixed: 2025-10-08-project-sparkpelican-summary.md (line 136)

✅ Successfully fixed 3 files:
   • second-post.md
   • 2025-10-08-project-sparkpelican-summary-v2.md
   • 2025-10-08-project-sparkpelican-summary.md

✅ All title formatting issues have been fixed!
💡 Run 'python scripts/validate-titles.py' to verify all titles are correct.
```

### 3. Integrated Build Process
Title validation is automatically integrated into the build process:

```bash
invoke build      # Validates titles before building
invoke preview    # Validates titles before production build
```

If titles are incorrectly formatted, the build will stop and show errors:
```
🔍 Validating blog post titles...
❌ Found 3 title formatting issues:
...
❌ Title validation failed! Please fix the issues above.
💡 To fix automatically, run: python scripts/fix-titles.py
```

### 4. Git Pre-commit Hook (Optional)
Prevent commits when titles are incorrectly formatted:

**Installation:**
```bash
# Copy the hook to the correct location
cp .git-hooks/pre-commit .git/hooks/pre-commit

# Make it executable
chmod +x .git/hooks/pre-commit
```

**Usage:**
Now every commit will automatically validate titles:
```bash
git add .
git commit -m "Add new post"

# If titles are incorrect, you'll see:
🔍 Validating blog post titles before commit...
❌ Found 2 title formatting issues:
...
❌ Commit blocked due to title formatting issues!
💡 To fix automatically, run: python scripts/fix-titles.py
🔄 After fixing, try committing again.
```

## Workflow Recommendations

### For Development
1. **Write your post** with proper title formatting from the start
2. **Run validation** before committing: `python scripts/validate-titles.py`
3. **Auto-fix if needed**: `python scripts/fix-titles.py`
4. **Build and test**: `invoke build` then `invoke serve`

### For Teams
1. **Install the pre-commit hook** to prevent title formatting issues
2. **Use the build integration** to catch issues in CI/CD
3. **Run validation** as part of code review process

### For CI/CD Integration
Add title validation to your deployment pipeline:

```yaml
# In your GitHub Actions workflow
- name: Validate titles
  run: python scripts/validate-titles.py

- name: Build site
  run: invoke preview
```

## Files Overview

- **`scripts/validate-titles.py`** - Validation script that checks for issues
- **`scripts/fix-titles.py`** - Auto-fix script that corrects formatting
- **`tasks.py`** - Updated with integrated validation in build tasks
- **`.git-hooks/pre-commit`** - Optional git hook for commit validation

## Best Practices

1. **Consistent Formatting**: Always use `title: Your Title` (no quotes)
2. **Early Validation**: Check titles before committing or deploying
3. **Automated Checks**: Use the build integration and git hooks
4. **Team Communication**: Share these tools with your team

## Troubleshooting

### "No markdown files found"
- Check that you're running the script from the project root
- Verify files exist in `content/posts/` directory

### "Permission denied" errors
- Make sure the scripts have execute permissions: `chmod +x scripts/*.py`
- Check that Python can access the content directory

### Build fails with title errors
- Run `python scripts/fix-titles.py` to auto-fix issues
- Or manually edit the files listed in the error output
- Re-run the build command

## Future Enhancements

The system can be extended to validate other front matter fields:
- Author formatting
- Date formats
- Tag consistency
- Description length limits

This title validation system ensures consistent, high-quality blog posts and prevents common formatting mistakes from reaching production.
