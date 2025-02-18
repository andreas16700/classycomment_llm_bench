from tqdm import tqdm
import pandas as pd
from openai import OpenAI
import json, torch
from java import java_descriptions, java_types


VERBOSE = False



client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def get_json_format(types):
    format = {
        "type": "json_schema",
        "json_schema": {
            "name": "line_classifications",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "A unique identifier for the line."
                        },
                        "category": {
                            "type": "string",
                            "description": "The classification category for the line.",
                            "enum": types
                        }
                    },
                    "required": ["id", "category"],
                    "additionalProperties": False
                }
            }
        }
    }
    return format





def classify(comment: str, model_id: str, types, missing_ids: list[int]=None):
    comment = "\n".join(f"{i+1} {line}" for i, line in enumerate(comment.splitlines()))
    suppl = ""
    if missing_ids and len(missing_ids) > 0:
        missing_ids = [f"{n}" for n in missing_ids]
        suppl = f"Make sure to especially classify the following lines: {", ".join(missing_ids)}"
    messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": f"""Segment and classify the following code comment into a given taxonomy of code comment categories (summary, expand, rationale, deprecation, usage, ownership, pointer, other).
Here's a brief description of each category:

{java_descriptions}
The comment could in its entirety (or parts of it), belong to none, one, multiple, or every category. Any line of the given text should not be classified to more than one category. Each line begins with its ID and a space. If no category fits, use the 'other' category.
{suppl}
Here's the comment:
\"\"\"
{comment}
\"\"\""""}
]
    format = get_json_format(types)
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

def missing_ids_of_result(comment: str, result):
    max_id = len(comment.splitlines())
    ids = set(range(1, max_id+1))
    found_ids = set()
    for classification in result:
        if "id" not in classification:
            return list(ids)
        found_ids.add(classification["id"])
    missing_ids = ids - found_ids
    return list(missing_ids)

def keep_only_valid_results(result, valid_types, max_id: int):
    to_keep = []
    for classification in result:
        if "category" not in classification:
            if VERBOSE:
                print(f"[INVALID] no category: {classification}")
            continue
        if classification["category"] not in valid_types:
            if VERBOSE:
                print(f"[INVALID] invalid category: {classification}")
            continue
        if "id" not in classification:
            if VERBOSE:
                print(f"[INVALID] no id: {classification}")
            continue
        id = classification["id"]
        try:
            id = int(id)
        except (ValueError, TypeError):
            if VERBOSE:
                print(f"[INVALID] invalid id: {classification["id"]}")
            continue
        if id < 1 or id > max_id:
            if VERBOSE:
                print(f"[INVALID] invalid id: {classification['id']} (must be between 1 and {max_id})")
            continue
        to_keep.append(classification)
    return to_keep


def make_sure_all_classified(func, comment: str, max_retries = 10, valid_types = java_types):
    # let's add some verbosity now.
    result = func(None)
    result = keep_only_valid_results(result, valid_types, max_id=len(comment.splitlines()))
    unclassified_ids = missing_ids_of_result(comment, result)
    retries = 0
    while len(unclassified_ids) > 0:
        retries += 1
        if VERBOSE:
            print(f"[DEBUG] [RETRY {retries}] unclassified ids: {unclassified_ids}. Got: {json.dumps(result, indent=2)}")
        result = func(unclassified_ids)
        unclassified_ids = missing_ids_of_result(comment, result)
        if retries >= max_retries:
            if VERBOSE:
                print(f"[INVALID] exceeded max retries!")
            return result
    return result


if __name__ == '__main__':
    models = [
        "phi-4",
        # "qwen2.5-14b-instruct-mlx",
        # "meta-llama-3.1-8b-instruct",
        # "mistral-nemo-instruct-2407",
        # "granite-3.1-8b-instruct"
    ]

    bench1_name = "bench2.json"
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
                # def make_sure_all_classified(func, comment: str, max_retries=10, valid_types=java_types):
                result_with_retries = make_sure_all_classified(lambda missing_id: classify(comment, model, types=java_types, missing_ids=missing_id), comment=comment, valid_types=java_types)
                # r = classify(comment, model)
                current[class_name][model] = result_with_retries
                save_current(current)