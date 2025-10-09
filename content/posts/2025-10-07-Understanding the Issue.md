---
title: Understanding the Issue
date: 2025-10-07T00:00:00.000Z
layout: post.njk
description: >-
  Fix linter warnings by replacing inline `animation-delay` styles with custom
  Tailwind CSS utilities. A simple guide to cleaner, more maintainable code for
  your Eleventy project.
author: "Infinity Spark"
readingTime: "4 min read"
---

### Understanding the Issue

Your `index.njk` template is a clean, responsive home page for an Eleventy site using Tailwind CSS v4, featuring animated cards, recent posts, and a fallback for empty collections. However, the file has multiple **inline styles** applied via the `style` attribute (e.g., `style="animation-delay: 0.1s;"`). These trigger "no-inline-styles" warnings from linters like webhint because embedding CSS directly in HTML can harm maintainability and caching performance.

Tailwind CSS is designed to solve this by using utility classes. We can refactor these inline styles into custom CSS utilities within a `@layer` or an external file. This guide focuses on a simple, performant fix that aligns with Tailwind's best practices.

Here are the inline styles we'll be replacing:
{% raw %}
| Location | Inline Style | Purpose |
|----------|--------------|---------|
| Feature card 1 | `animation-delay: 0.1s;` | Staggered fade-in animation. |
| Feature card 2 | `animation-delay: 0.2s;` | Staggered fade-in. |
| Feature card 3 | `animation-delay: 0.3s;` | Staggered fade-in. |
| Posts section wrapper | `animation-delay: 0.4s;` | Overall slide-up delay. |
| Each post article | `animation-delay: {{ loop.index * 0.1 }}s;` | Dynamic stagger per post (Nunjucks loop). |
| Bounce dot 2 | `animation-delay: 0.1s;` | Staggered bounce animation. |
| Bounce dot 3 | `animation-delay: 0.2s;` | Staggered bounce. |
{% endraw %}

These are all `animation-delay` properties used for UX polish. Removing them would break the staggered animations, so we will convert them into reusable utility classes instead.

### Step-by-Step Fix

The best approach is to add custom utilities to your main CSS file (e.g., `src/input.css`). This keeps your styling modular and leverages Tailwind's Just-in-Time (JIT) compilation.

**1. Locate Your Main Tailwind CSS File**

  - This is typically a file like `src/input.css` or `src/styles/tailwind.css`.
  - Ensure it contains the base Tailwind directives:
    ```css
    @tailwind base;
    @tailwind components;
    @tailwind utilities;
    ```

**2. Add Custom Animation Delay Utilities**

  - In the same CSS file, add the following `@layer` block. We'll define simple, reusable classes for our delays.
    ```css
    @layer utilities {
      .delay-100 { animation-delay: 0.1s; }
      .delay-200 { animation-delay: 0.2s; }
      .delay-300 { animation-delay: 0.3s; }
      .delay-400 { animation-delay: 0.4s; }
    }
    ```
  - **Why use classes?** They are cacheable, align with Tailwind's methodology, and keep your HTML clean.

**3. Update the HTML in `index.njk`**

  - Replace each `style` attribute with the corresponding new utility class.

**Feature Highlights Section:**
\`\`\`njk
\<div class="... animate-fade-in" style="animation-delay: 0.1s;"\>...\</div\>
\<div class="... animate-fade-in" style="animation-delay: 0.2s;"\>...\</div\>
\<div class="... animate-fade-in" style="animation-delay: 0.3s;"\>...\</div\>

````
 <div class="... animate-fade-in delay-100">...</div>
 <div class="... animate-fade-in delay-200">...</div>
 <div class="... animate-fade-in delay-300">...</div>
 ```
````

**Posts Section Wrapper:**
\`\`\`njk
\<div class="... animate-slide-up" style="animation-delay: 0.4s;"\>

````
 <div class="... animate-slide-up delay-400">
 ```
````

**Bounce Dots (in "No Posts" fallback):**
\`\`\`njk
\<div class="... animate-bounce" style="animation-delay: 0.1s;"\>\</div\>
\<div class="... animate-bounce" style="animation-delay: 0.2s;"\>\</div\>

````
 <div class="... animate-bounce delay-100"></div>
 <div class="... animate-bounce delay-200"></div>
 ```
````

{% raw %}
**4. Handle the Dynamic Post Delays**

- The staggered delay for posts (`animation-delay: {{ loop.index * 0.1 }}s;`) is a special case. Since the number of posts can vary, creating a separate utility class for each is not ideal.
- For this specific dynamic use case, using an **inline `style` attribute is perfectly acceptable and often the cleanest solution**. It avoids generating dozens of unused CSS classes. Modern web performance standards recognize that a minimal, dynamic inline style is better than a bloated stylesheet.
{% endraw %}

{% raw %}
**Update the Post Article Loop:**
Keep the inline style for this dynamic property. It's a pragmatic exception to the rule.
```njk
{% for post in collections.posts %}
  <article class="... animate-fade-in" style="animation-delay: {{ loop.index0 * 0.1 }}s;">
    </article>
{% endfor %}

> **Note:** I've switched to `loop.index0` (which is 0-indexed) to start the animation delay from `0s` for the first post. If you prefer the first post to have a `0.1s` delay, stick with `loop.index` (which is 1-indexed).

**5. Build and Test**

  - Run your build command (`npm run build` or `eleventy --serve`).
  - The output HTML in `_site` will be free of static inline styles, and your animations will still work perfectly.
  - The webhint warnings should now be resolved.

  {% endraw %}
