# SparkPelican Migration Checklist

> A complete step-by-step guide to refactor, validate, and deploy the new SparkPelican structure.

## Step 1 — Prepare the Environment
1. Activate your Python virtual environment:
   ```bash
   cd ~/Documents/github-repo/sparkpelican
   source venv/bin/activate
   ```
2. Ensure all required dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
3. Verify Python version:
   ```bash
   python --version
   ```
   Recommended: `Python 3.12.x`.

## Step 2 — Backup Existing Content
1. Backup the current `content` directory and `output`:
   ```bash
   cp -r content content_backup
   cp -r output output_backup
   ```
2. Optionally backup configuration files:
   ```bash
   cp -r config config_backup
   ```

## Step 3 — Review Current Directory Structure
Your working repo should contain:
```
content/        # posts, pages, images, drafts
config/         # pelicanconf.py, publishconf.py
themes/         # sparkpelican-theme
scripts/        # batch and content processing scripts
src/            # Python modules
venv/           # virtual environment
logs/           # process logs
```
Verify all critical directories exist.

## Step 4 — Run Migration Scripts
1. Make your migration scripts executable if needed:
   ```bash
   chmod +x migrate_structure.sh
   ```
2. Run migration scripts to fix frontmatter, thumbnails, slugs, and titles:
   ```bash
   ./migrate_structure.sh
   ```
3. Review logs in `logs/` to ensure no errors occurred.

## Step 5 — Validate Content Metadata
1. Check that all Markdown/YAML frontmatter is properly formatted:
   - Required fields: `title`, `date`, `slug`, `category`.
   - Ensure no unclosed tags or duplicate slugs.
2. Run tests for validation scripts if present:
   ```bash
   python test_gemini_fix.py
   python test_basic.py
   ```

## Step 6 — Reorganize Media and Images
1. Ensure all images are in `content/images/`.
2. Update Markdown files to reference images relative to `content/`:
   ```markdown
   ![Alt text](../images/my-image.jpg)
   ```
3. Run `fix_thumbnail_path.py` or `fix_thumbnail_relpath.py` if needed.

## Step 7 — Update Configuration Files
1. Check `config/pelicanconf.py` for:
   - `PATH = 'content'`
   - `OUTPUT_PATH = 'output/'`
   - Theme settings
2. Check `config/publishconf.py` for publishing options.

## Step 8 — Generate the Site Locally
1. Build the site:
   ```bash
   pelican content -s config/pelicanconf.py
   ```
2. Preview with live server:
   ```bash
   livereload output/
   ```
3. Confirm that all pages, posts, tags, categories, and media render correctly.

## Step 9 — Verify Output Files
1. Inspect `output/` directory:
   - HTML pages correspond to Markdown content.
   - Tags, categories, and archives generate properly.
   - Static assets (images, CSS, JS) are correctly linked.

## Step 10 — Run Automated Tests
1. Test Python scripts and migrations:
   ```bash
   pytest tests/
   ```
2. Ensure no failing tests before deployment.

## Step 11 — Commit Changes
1. Stage and commit migration changes:
   ```bash
   git add content config scripts src
   git commit -m "Refactor: apply migration scripts and restructure SparkPelican"
   ```

## Step 12 — Deploy
1. Use `ghp-import` or your preferred deployment workflow:
   ```bash
   ghp-import -b main -p output
   ```
2. Validate live deployment and spot-check pages for correctness.

> ✅ **Note:** Keep your backup (`content_backup`, `output_backup`) until deployment is fully verified.
