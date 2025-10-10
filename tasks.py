import os
import shlex
import shutil
import sys
import datetime

from invoke import task
from invoke.main import program
from pelican import main as pelican_main
from pelican.server import ComplexHTTPRequestHandler, RootedHTTPServer
from pelican.settings import DEFAULT_CONFIG, get_settings_from_file

OPEN_BROWSER_ON_SERVE = True
SETTINGS_FILE_BASE = "pelicanconf.py"
SETTINGS = {}
SETTINGS.update(DEFAULT_CONFIG)
LOCAL_SETTINGS = get_settings_from_file(SETTINGS_FILE_BASE)
SETTINGS.update(LOCAL_SETTINGS)

CONFIG = {
    "settings_base": SETTINGS_FILE_BASE,
    "settings_publish": "publishconf.py",
    # Output path. Can be absolute or relative to tasks.py. Default: 'output'
    "deploy_path": SETTINGS["OUTPUT_PATH"],
    # Github Pages configuration
    "github_pages_branch": "gh-pages",
    "commit_message": f"'Publish site on {datetime.date.today().isoformat()}'",
    # Host and port for `serve`
    "host": "localhost",
    "port": 8001,
}


@task
def clean(c):
    """Remove generated files"""
    if os.path.isdir(CONFIG["deploy_path"]):
        shutil.rmtree(CONFIG["deploy_path"])
        os.makedirs(CONFIG["deploy_path"])


@task
def validate_titles(c):
    """Validate that all blog post titles are properly formatted (no quotes)"""
    print("🔍 Validating blog post titles...")
    result = c.run("python scripts/validate-titles.py", warn=True)
    if result.failed:
        print("❌ Title validation failed! Please fix the issues above.")
        print("💡 To fix automatically, run: python scripts/fix-titles.py")
        sys.exit(1)
    else:
        print("✅ All titles are properly formatted!")


@task
def build(c):
    """Build local version of site"""
    validate_titles(c)  # Validate titles before building
    pelican_run("-s {settings_base}".format(**CONFIG))


@task
def rebuild(c):
    """`build` with the delete switch"""
    pelican_run("-d -s {settings_base}".format(**CONFIG))


@task
def regenerate(c):
    """Automatically regenerate site upon file modification"""
    pelican_run("-r -s {settings_base}".format(**CONFIG))


@task
def serve(c):
    """Serve site at http://$HOST:$PORT/ (default is localhost:8000)"""

    class AddressReuseTCPServer(RootedHTTPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(
        CONFIG["deploy_path"],
        (CONFIG["host"], CONFIG["port"]),
        ComplexHTTPRequestHandler,
    )

    if OPEN_BROWSER_ON_SERVE:
        # Open site in default browser
        import webbrowser

        webbrowser.open("http://{host}:{port}".format(**CONFIG))

    sys.stderr.write("Serving at {host}:{port} ...\n".format(**CONFIG))
    server.serve_forever()


@task
def reserve(c):
    """`build`, then `serve`"""
    build(c)
    serve(c)


@task
def preview(c):
    """Build production version of site"""
    validate_titles(c)  # Validate titles before production build
    pelican_run("-s {settings_publish}".format(**CONFIG))

@task
def livereload(c):
    """Automatically reload browser tab upon file modification."""
    from livereload import Server

    def simple_build():
        try:
            cmd = "-s {settings_base}"
            pelican_run(cmd.format(**CONFIG))
        except Exception as e:
            print(f"Error during build: {e}")
            return False
        return True

    try:
        simple_build()
        server = Server()
        theme_path = SETTINGS["THEME"]
        watched_globs = [
            CONFIG["settings_base"],
            f"{theme_path}/templates/**/*.html",
        ]

        content_file_extensions = [".md", ".rst"]
        for extension in content_file_extensions:
            content_glob = "{}/**/*{}".format(SETTINGS["PATH"], extension)
            watched_globs.append(content_glob)

        static_file_extensions = [".css", ".js"]
        for extension in static_file_extensions:
            static_file_glob = f"{theme_path}/static/**/*{extension}"
            watched_globs.append(static_file_glob)

        for glob in watched_globs:
            server.watch(glob, simple_build)

        if OPEN_BROWSER_ON_SERVE:
            # Open site in default browser
            import webbrowser

            webbrowser.open("http://{host}:{port}".format(**CONFIG))

        print(f"Serving at {CONFIG['host']}:{CONFIG['port']} with live reload...")
        server.serve(host=CONFIG["host"], port=CONFIG["port"], root=CONFIG["deploy_path"])
    except KeyboardInterrupt:
        print("\nLive reload server stopped.")
    except Exception as e:
        print(f"Error starting live reload server: {e}")
        print("Try running 'invoke build' first, then 'invoke serve' for basic serving.")


@task
def publish(c):
    """Publish to production via rsync"""
    pelican_run("-s {settings_publish}".format(**CONFIG))
    c.run(
        'rsync --delete --exclude ".DS_Store" -pthrvz -c '
        '-e "ssh -p {ssh_port}" '
        "{} {ssh_user}@{ssh_host}:{ssh_path}".format(
            CONFIG["deploy_path"].rstrip("/") + "/", **CONFIG
        )
    )

@task
def gh_pages(c):
    """Publish to GitHub Pages"""
    preview(c)
    c.run(
        "ghp-import -b {github_pages_branch} "
        "-m {commit_message} "
        "{deploy_path} --no-jekyll -p".format(**CONFIG)
    )

@task
def api_validate_posts(c, fix=False):
    """Validate all blog posts for proper FastAPI integration"""
    print("🔍 Validating blog posts for FastAPI compatibility...")
    result = c.run("python scripts/validate-titles.py", warn=True)
    if result.failed:
        print("❌ Post validation failed!")
        if fix:
            print("🔧 Auto-fixing title issues...")
            fix_result = c.run("python scripts/fix-titles.py", warn=True)
            if fix_result.failed:
                print("❌ Auto-fix failed. Please fix manually.")
                sys.exit(1)
            else:
                print("✅ Titles fixed automatically!")
        else:
            print("💡 Run 'invoke api-validate-posts --fix' to auto-fix issues.")
            sys.exit(1)
    else:
        print("✅ All posts are API-compatible!")

@task
def api_server(c, host="localhost", port=8001, reload=True):
    """Start the FastAPI server for AI-powered post generation"""
    print(f"🚀 Starting FastAPI server on {host}:{port}")
    print("Endpoints available:")
    print(f"  Health: http://{host}:{port}/health")
    print(f"  Generate: http://{host}:{port}/generate")
    print(f"  Validate: http://{host}:{port}/validate")
    print("")

    # Ensure environment variables are set
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY=your_key_here")
        print("")

    reload_flag = "--reload" if reload else ""
    cmd = f"uvicorn myapp.main:app --host {host} --port {port} {reload_flag}"
    c.run(cmd)

@task
def api_docs(c, port=8001):
    """Open FastAPI interactive documentation"""
    print("📖 Opening FastAPI documentation...")
    import webbrowser
    docs_url = f"http://localhost:{port}/docs"
    webbrowser.open(docs_url)
    print(f"📋 Documentation: {docs_url}")

@task
def api_generate(c, youtube_url=None, title=None, category="General", tags=""):
    """Generate a blog post from YouTube URL using the API"""
    if not youtube_url:
        print("❌ YouTube URL required. Usage: invoke api-generate --youtube-url='https://youtube.com/...'")
        print("Example: invoke api-generate --youtube-url='https://youtube.com/watch?v=dQw4w9WgXcQ'")
        return

    print(f"🎬 Generating post from: {youtube_url}")

    # Split tags if provided
    tag_list = [tag.strip() for tag in tags.split(',')] if tags else []

    try:
        # Import the FastAPI modules directly
        import asyncio
        from myapp.youtube_transcript import get_transcript_async
        from myapp.ai_generator import generate_post_async
        from myapp.pelican_integrator import save_markdown_post
        from pathlib import Path

        async def generate():
            # Get transcript
            print("📝 Extracting transcript...")
            transcript = await get_transcript_async(youtube_url)

            # Generate post
            print("🤖 Generating AI content...")
            post_data = await generate_post_async(
                transcript=transcript,
                video_id=youtube_url.split('/')[-1].split('=')[-1][:11],
                custom_title=title,
                category=category,
                tags=tag_list
            )

            # Save to Pelican
            print("💾 Saving to Pelican...")
            content_dir = Path("content/posts")
            filename = await save_markdown_post(post_data, content_dir)

            print(f"✅ Post generated and saved: {filename}")
            print(f"📄 Title: {post_data['title']}")
            print(f"🏷️  Tags: {', '.join(post_data['tags'])}")

            return filename

        # Run the async generation
        filename = asyncio.run(generate())

        print("\nNext steps:")
        print(f"  1. Review the generated post: content/posts/{filename}")
        print("  2. Run 'invoke build' to include it in your site")
        print("  3. Run 'invoke serve' to preview the changes")

    except Exception as e:
        print(f"❌ Generation failed: {str(e)}")
        sys.exit(1)

def pelican_run(cmd):
    cmd += " " + program.core.remainder  # allows to pass-through args to pelican
    pelican_main(shlex.split(cmd))
