AUTHOR = 'Infinity Spark'
SITENAME = 'sparkpelican'
SITEURL = ''

PATH = 'content'
TIMEZONE = 'America/Toronto'
DEFAULT_LANG = 'en'

# Theme settings
THEME = 'themes/sparkpelican-theme'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Social widget
LINKS = ()
SOCIAL = ()

# Smart pagination: 12 posts per page (works well with 3-column grid: 4 rows x 3 columns)
DEFAULT_PAGINATION = 12

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

JINJA_FILTERS = {
    'raw_url': lambda x: x,
}
