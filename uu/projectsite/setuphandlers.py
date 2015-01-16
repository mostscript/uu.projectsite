
# allowed styles for safe_html:
ALLOWED_STYLES = [
    u'text-align',
    u'list-style-type',
    u'float',
    u'padding-left',
    u'text-decoration',
    u'color',
    u'background-color',
    u'margin-left',
    u'margin-right',
    u'display'
    ]


# formats JSON for TinyMCE:
FORMATS = """
{
    "underline" : {
        "inline" : "span",
        "styles" : {"text-decoration": "underline"},
        "exact" : true
    }
}
""".strip()


def whitelist_safe_styles(context):
    site = context.getSite()
    tool = site.portal_transforms
    plugin = tool.get('safe_html')
    plugin._config['style_whitelist'] = ALLOWED_STYLES
    plugin._p_changed = True


def add_tinymce_formats(context):
    site = context.getSite()
    tool = site.portal_tinymce
    tool.formats = FORMATS

