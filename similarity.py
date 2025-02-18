import torch
from sentence_transformers import SentenceTransformer, util



def find_most_similar(q: str, corpus: list[str], debug=False):
    # Load the text embedding model
    model = SentenceTransformer('all-mpnet-base-v2')
    # Encode all strings into embeddings
    embeddings = model.encode(corpus, convert_to_tensor=True)

    # Use the first string (comment) as the query
    query_embedding = model.encode(q, convert_to_tensor=True)

    # Compute cosine similarities between the query and all strings
    cos_scores = util.cos_sim(query_embedding, embeddings)[0]

    # Sort the indices by decreasing similarity
    sorted_indices = torch.argsort(cos_scores, descending=True)

    # Print the strings in order of decreasing similarity along with their scores

    if debug:
        for idx in sorted_indices:
            print(corpus[idx], f"(Score: {cos_scores[idx]:.4f})")
    return corpus[sorted_indices[0]], cos_scores[sorted_indices[0]].item()

