from pathlib import Path

# Paths
default_input_dirname = 'input'
default_output_dirname = 'output'

config_filename = 'stablogen.yaml'
templates_dirname = 'templates'
posts_dirname = 'posts'
tags_dirname = 'tags'

# Look for these file extensions in the posts directory
post_file_exts = (
    '.html',
)

# Use Jinja on the following file extentions in the input directory
# Could add css and javascript files here for instance
RENDER_EXTENTIONS = (
    '.html',
)

PYGMENTS_CSS_OUTPUT = 'static/code.css'
