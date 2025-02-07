# Classifying class comments


### *Note: this is a modified version of the benchmarking library for a similar task I made for [Paraphrasus](https://github.com/impresso/paraphrasus). A lot of files are unrelated. The reason for this is that this project needs similar functionality. As the approach matures, the relevant reusable parts will become more apparent, and the codebase more coherent.*


## Classification Approach

The model is given the comment type categories, along with a short description (taken from the appropriate paper where each taxonomy is defined (Pascarella and Bacchelli,2017; Zhang et al.,
2018; Ranietal.,2021)

Using [structured output](https://github.com/dottxt-ai/outlines), the model responds with a json object containing the comment, segmented into relevant types.

The prompt and corresponding categories are language-dependant. For context, since this is intended for an IDE plugin, the programming language is known (Python/Pharo/Java).


For example, for classifying a comment in Java, the model is given this prompt:

```markdown


Segment and classify the following code comment into a given taxonomy of code comment categories (summary, expand, rationale, deprecation, usage, ownership, pointer, other).
Here's a brief description of each category:

- **summary**: The comment describes a brief description of the code. It answers the "what" of the code.
- **expand**: Similar to the summary category, this label indicates that the comment provides a more detailed description of the code. It answers the "how" of the code.
- **rationale**: The comment explains the reasoning behind certain choices, patterns, or options in the code. It answers the "why" of the code.
- **deprecation**: The comment contains explicit warnings regarding deprecated interface artifacts. It includes information about alternative methods or classes (e.g., “do not use [this]”, “is it safe to use?” or “refer to: [ref]”), future deprecation plans, or scheduled changes. Tags like @version, @deprecated, or @since may also be present.
- **usage**: The comment offers explicit suggestions, examples, or use cases for users planning to use a functionality. It might include code snippets or metadata marks such as @usage, @param, or @return.
- **ownership**: The comment identifies the authors or ownership details, possibly including external references or credentials (commonly marked with @author).
- **pointer**: The comment contains references to linked resources, using tags like @see, @link, or @url, or even identifiers such as “FIX #2611” or “BUG #82100.”
- **other**: Use this category for any comment that doesn't fit into any of the above types.

The comment could in its entirety (or parts of it), belong to none, one, multiple, or every category. Any segment of the given text should not be classified to more than one category. If no category fits, use the 'other' category.
Here's the comment:
"""
Azure Blob File System implementation of AbstractFileSystem.
This impl delegates to the old FileSystem
"""
```
Along with this, the model is given this JSON schema:
```json
{
        "name": "Segmented and Classified Code Comment",
        "schema": {
            "type": "object",
            "properties": {
    "summary": {
      "type": "array",
      "description": "Comment describes a brief description of the code. It answers the 'what' of the code.",
      "items": {
        "type": "string"
      }
    },
    "expand": {
      "type": "array",
      "description": "Comment provides more details about the code's behavior. It answers the 'how' of the code.",
      "items": {
        "type": "string"
      }
    },
    "rationale": {
      "type": "array",
      "description": "Comment explains the reasoning behind certain choices, patterns, or options in the code. It answers the 'why' of the code.",
      "items": {
        "type": "string"
      }
    },
    "deprecation": {
      "type": "array",
      "description": "Comment contains explicit warnings regarding deprecated artifacts, alternative suggestions, or future deprecation notes (including tags like @deprecated, @version, or @since).",
      "items": {
        "type": "string"
      }
    },
    "usage": {
      "type": "array",
      "description": "Comment includes explicit suggestions, use cases, examples, or code snippets aimed at the user (often marked with metadata such as @usage, @param, or @return).",
      "items": {
        "type": "string"
      }
    },
    "ownership": {
      "type": "array",
      "description": "Comment details authorship, credentials, or external references about the developers (e.g., using the @author tag).",
      "items": {
        "type": "string"
      }
    },
    "pointer": {
      "type": "array",
      "description": "Comment contains references to linked resources, external references, or tags such as @see, @link, @url, or even identifiers like FIX #2611.",
      "items": {
        "type": "string"
      }
    },
    "other": {
      "type": "array",
      "description": "for any comment that doesn't fit any other comment type.",
      "items": {
        "type": "string"
      }
    }
  },
            "required": []
        }
    }
```

The model responds with this object:
```json
{
  "summary": [
    "Azure Blob File System implementation of AbstractFileSystem."
  ],
  "expand": [
    "This impl delegates to the old FileSystem"
  ],
  "rationale": [],
  "deprecation": [],
  "usage": [],
  "ownership": [],
  "pointer": [],
  "other": []
}
```
*in this case this is from the 4-bit quantized version of Phi-4*
