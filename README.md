# Creating_And_Querying_Positional_Indexes
*IR assignment to generate a positional inverted index from a given collection of documents stored in a folder.* <p>
Here are some important functions that do the main functionality in the assignemnt.

* Function to convert each document to inverted index.
```
def process_document(file_path, doc_id, inverted_index, doc_id_path_mapping, stop_words):
    with open(file_path, 'r') as file:
        dictionary = {} 
        current_position = 1

        for line in file:
            for word in line.split():
                # Normalization for each term
                word = word.translate(str.maketrans('', '', string.punctuation)).lower()

                if len(word) >= 3 and word not in stop_words:
                    dictionary.setdefault(word, []).append(current_position)
                current_position += 1

        # Convert my dictionary to inverted index
        for term, term_positions in dictionary.items():
            inverted_index.setdefault(term, {}).setdefault(doc_id, []).extend(term_positions)

    # add file id & path for mapping
    doc_id_path_mapping[doc_id] = file_path
```

* Function to execute a query on the inverted index and return all related documents.

```
def excute_query_index(index, phrase):
    tokens = [word.lower() for word in phrase.split()]

    query_result = {}
    for token in tokens:
        if token in index:
            postings = index[token]
            for doc_id, positions in postings.items():
                if doc_id not in query_result:
                    query_result[doc_id] = positions
                else:
                    query_result[doc_id].extend(positions)

    return query_result
```

* Function to insert a new document into the `Inverted Index` & `Mapping Id's and Pathes documents`.
```
def insert_document(file_path, doc_id, inverted_index, doc_id_path_mapping, stop_words):
    # Check if the document is already in the index
    if doc_id in doc_id_path_mapping:
        return False
    
    process_document(file_path, doc_id, inverted_index, doc_id_path_mapping, stop_words)
    
    save_inverted_index_to_file(inverted_index, inverted_index_path)
    save_mapping_to_csv(doc_id_path_mapping, mapping_path)
        
    return True
```

* Function to delete a document from the `Inverted Index` and `Mapping Id's and Pathes` documents.

```
def delete_document(doc_id, inverted_index, doc_id_path_mapping):
    # Check if the document exists in the index
    if doc_id not in doc_id_path_mapping:
        return False
    
    terms_to_delete = []

    del doc_id_path_mapping[doc_id]
    for term, postings in inverted_index.items():
        if doc_id in postings:
            del postings[doc_id]

        # If the term has no more postings, mark it for deletion
        if not postings:
            terms_to_delete.append(term)

    for term in terms_to_delete:
        del inverted_index[term]
                
    save_inverted_index_to_file(inverted_index, inverted_index_path)
    save_mapping_to_csv(doc_id_path_mapping, mapping_path)

    return True 
```
