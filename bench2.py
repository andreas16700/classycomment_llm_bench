from tqdm import tqdm
import pandas as pd
from openai import OpenAI
import json

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
format = {
    "type": "json_schema",
    "json_schema": {
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
        },
    }
}

def classify(comment: str, model_id: str):
    messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": f"""Segment and classify the following code comment into a given taxonomy of code comment categories (summary, expand, rationale, deprecation, usage, ownership, pointer, other).
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
\"\"\"
{comment}
\"\"\""""}
]

    # Get response from AI
    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        response_format=format,
    )

    # Parse and display the results
    content = response.choices[0].message.content

    try:
        results = json.loads(content)
    except json.JSONDecodeError as e:
        results = {
            "error": str(e),
            "response": content
        }
    return results




if __name__ == '__main__':

    models = [
        "phi-4",
        # "qwen2.5-14b-instruct-mlx",
        # "meta-llama-3.1-8b-instruct"
    ]

    bench1_name = "bench1.json"
    current = {}

    try:
        with open(bench1_name, 'r') as f:
            # Try loading the JSON data. If the file is empty or invalid, a JSONDecodeError is raised.
            current = json.load(f)
    except FileNotFoundError:
        # File does not exist, so current remains an empty dict.
        current = {}
    except json.JSONDecodeError:
        # File is empty or contains invalid JSON, so current remains an empty dict.
        current = {}
    except Exception as e:
        current = {}


    def save_current(data):
        """
        Save a JSON object to a file.

        Args:
            data (dict): The JSON-compatible object (typically a dict) to save.
            filename (str): The name of the file to save the data in.
        """
        try:
            with open(bench1_name, "w") as f:
                json.dump(data, f, indent=4)
            # print(f"Data successfully saved to {bench1_name}.")
        except IOError as e:
            print(f"An error occurred while saving to {bench1_name}: {e}")
            exit(1)


    data_path = "java_0_raw.csv"


    print(f"reading {data_path}..")
    df = pd.read_csv(data_path)
    for index, row in tqdm(df.iterrows(), total=len(df)):
        class_name = row["class"]
        comment = row["comment"]

        if not class_name in current:
            current[class_name] = {}
        for model in models:
            if not model in current[class_name]:
                r = classify(comment, model)
                current[class_name][model] = r
                save_current(current)