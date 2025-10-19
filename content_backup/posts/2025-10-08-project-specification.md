---
title: Under the Hood: The SparkPelican Project Specification
date: 2025-10-08
author: Infinity Spark
---

This document outlines the project specification for the SparkPelican website, a modern static site built with a focus on simplicity, performance, and a streamlined content workflow. This specification serves as a guide for understanding the project's architecture, technologies, and conventions.

### Core Technologies

The SparkPelican project is built upon a foundation of powerful and flexible open-source technologies:

*   **Pelican:** A static site generator written in Python. It's used to convert Markdown content into a fully functional HTML website.
*   **Tailwind CSS:** A utility-first CSS framework for rapidly building custom user interfaces. It's used for all styling and theming.
*   **Python:** The primary programming language for the backend and build process, utilizing the Pelican and Invoke libraries.
*   **Node.js:** Used for managing the Tailwind CSS dependency and running the CSS build process.
*   **Invoke:** A Python task execution tool used to automate common development tasks like building the site and serving it locally.
*   **GitHub Actions:** A CI/CD platform used to automate the deployment of the website to GitHub Pages.

### Project Structure

The project is organized into the following key directories and files:

*   `content/posts/`: This directory contains all the website's content in the form of Markdown files. Each file represents a single blog post.
*   `themes/sparkpelican-theme/`: This directory contains the theme for the website, including all templates and static assets.
    *   `templates/`: Contains the Jinja2 templates that define the structure and layout of the site.
    *   `static/css/`: Contains the CSS files, including the input for Tailwind CSS and the final generated output.
*   `pelicanconf.py`: The main configuration file for Pelican, used for development settings.
*   `publishconf.py`: The configuration file for Pelican, used for production settings.
*   `tasks.py`: An Invoke script that defines a set of commands for automating common tasks.
*   `package.json`: The Node.js configuration file, which defines the project's npm dependencies (primarily Tailwind CSS).
*   `requirements.txt`: The Python configuration file, which lists the project's Python dependencies.
*   `.github/workflows/deploy.yml`: The GitHub Actions workflow file that defines the automated deployment process.

### Content Management

All content for the website is written in Markdown and stored in the `content/posts/` directory. To create a new post, simply add a new `.md` file to this directory. The file should include the following metadata at the top:

```markdown
---
title: Your Post Title
date: YYYY-MM-DD
author: Your Name
---

Your post content goes here...
```

### Styling and Theming

The website's styling is managed by Tailwind CSS. The main input file is located at `themes/sparkpelican-theme/static/css/input.css`. When the site is built, this file is processed by Tailwind CSS to generate the final `output.css` file, which is then used by the website.

The theme's HTML structure is defined by a set of Jinja2 templates in the `themes/sparkpelican-theme/templates/` directory. These templates are used by Pelican to generate the final HTML pages.

### Automation and Deployment

The project uses a combination of Invoke and GitHub Actions to automate the development and deployment workflow.

*   **Local Development:** The `tasks.py` file provides a set of commands for common development tasks, such as:
    *   `invoke build`: Builds the Pelican site.
    *   `invoke serve`: Serves the site locally for testing.
    *   `invoke livereload`: Automatically rebuilds the site and reloads the browser when changes are made.
*   **Deployment:** The website is automatically deployed to GitHub Pages whenever a new commit is pushed to the `main` branch. The deployment process is defined in the `.github/workflows/deploy.yml` file and consists of the following steps:
    1.  Checkout the code.
    2.  Set up the Python and Node.js environments.
    3.  Install the required dependencies.
    4.  Build the Tailwind CSS.
    5.  Build the Pelican site.
    6.  Deploy the generated `output` directory to GitHub Pages.
