java_categories = {
    "summary": """
comment describes a brief description of the code. It answers the 'what' of the code.
""",
                    "expand": """
similarly to the summary category, this label means that the comment's purpose is a description of the code, but providing more details.
It answers the 'how' of the code. 
""",

"rationale" : """
comment describes the reasoning behind some choices, patterns or options in the code.
It answers the 'why' of the code. 
""",

"deprecation" : """
comment contains explicit warnings used to inform about deprecated interface artifacts.
This subcategory contains comments related to alternative methods or classes that should be used (e.g., “do not use [this]”, “is it safe to use?” or “refer to: [ref]”).
It also includes the description of the future or scheduled deprecation to inform the users of candidate changes.
Sometimes, a tag comment such as @version, @deprecated, or @since is used.
""",

"usage" : """
comment regards explicit suggestions to users that are planning to use a functionality.
It combines pure natural language text with examples, use cases, snippets of code, etc.
Often, the advice is preceded by a metadata mark e.g., @usage, @param or @return
""",

"ownership" : """
comment describes the authors and the ownership with different granularity.
comment may address methods, classes or files.
In addition, this type of comment includes credentials or external references about the developers.
A special tag is often used e.g., “@author”.
""",

"pointer" : """
comment contains references to linked resources.
The common tags are: “@see”, “@link” and “@url”.
Other times developers use custom references such as “FIX #2611” or “BUG #82100” that are examples of traditional external resources.
""",
    "other" : "for any comment that doesn't fit any other comment type."
}
