
java_types = [
    "summary",
    "expand",
    "rationale",
    "deprecation",
    "usage",
    "ownership",
    "pointer",
    "other"
]
java_descriptions = """- **summary**: The comment describes a brief description of the code. It answers the "what" of the code.
- **expand**: Similar to the summary category, this label indicates that the comment provides a more detailed description of the code. It answers the "how" of the code.
- **rationale**: The comment explains the reasoning behind certain choices, patterns, or options in the code. It answers the "why" of the code.
- **deprecation**: The comment contains explicit warnings regarding deprecated interface artifacts. It includes information about alternative methods or classes (e.g., “do not use [this]”, “is it safe to use?” or “refer to: [ref]”), future deprecation plans, or scheduled changes. Tags like @version, @deprecated, or @since may also be present.
- **usage**: The comment offers explicit suggestions, examples, or use cases for users planning to use a functionality. It might include code snippets or metadata marks such as @usage, @param, or @return.
- **ownership**: The comment identifies the authors or ownership details, possibly including external references or credentials (commonly marked with @author).
- **pointer**: The comment contains references to linked resources, using tags like @see, @link, or @url, or even identifiers such as “FIX #2611” or “BUG #82100.”
- **other**: Use this category for any comment that doesn't fit into any of the above types."""