import os
import json
import string
import csv

# Convert each document to inverted index
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
    
# Convert all the files in the folder to one inverted index and one document path id mapping
def generate_inverted_index(folder_path, stop_words):
    inverted_index = {}
    doc_id_path_mapping = {}
    document_id = 1

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            process_document(file_path, document_id, inverted_index, doc_id_path_mapping, stop_words)
            document_id += 1

    return inverted_index, doc_id_path_mapping

# To execute a query on the inverted index and return all related documents
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

# Function used to update the inverted index and document path id mapping, if were already exists
def genarate_inverted_index_and_mapping_as_files(inverted_index_path, mapping_path, folder_path, stop_words):
    existing_inverted_index = load_inverted_index_from_file(inverted_index_path)
    existing_mapping = load_mapping_from_csv(mapping_path)

    inverted_index, doc_id_path_mapping = generate_inverted_index(folder_path, stop_words)
    
    existing_inverted_index = inverted_index
    existing_mapping.update(doc_id_path_mapping)

    save_inverted_index_to_file(existing_inverted_index, inverted_index_path)
    save_mapping_to_csv(existing_mapping, mapping_path)
    
    return existing_inverted_index, existing_mapping

# Function to insert a document data into the inverted index and Mapping Id's and Pathes documents
def insert_document(file_path, doc_id, inverted_index, doc_id_path_mapping, stop_words):
    # Check if the document is already in the index
    if doc_id in doc_id_path_mapping:
        return False
    
    process_document(file_path, doc_id, inverted_index, doc_id_path_mapping, stop_words)
    
    save_inverted_index_to_file(inverted_index, inverted_index_path)
    save_mapping_to_csv(doc_id_path_mapping, mapping_path)
        
    return True

# Function to delete a document from the Inverted Index and Mapping Id's and Pathes documents
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

def generate_stop_words(path):
    with open(path, 'r') as stop_words_file:
        stop_words = set(stop_words_file.read().splitlines())
    return stop_words

def load_inverted_index_from_file(file_path):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        return {}

def load_mapping_from_csv(csv_path):
    try:
        with open(csv_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            return {int(row['doc_id']): row['file_path'] for row in reader}
    except FileNotFoundError:
        return {}

def save_inverted_index_to_file(index, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(index, json_file, indent=2)

def save_mapping_to_csv(mapping, csv_path):
    with open(csv_path, 'w', newline='') as csv_file:
        fieldnames = ['doc_id', 'file_path']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for doc_id, file_path in mapping.items():
            writer.writerow({'doc_id': doc_id, 'file_path': file_path})

# Menu function create a simple demo
def menu(inverted_index, doc_id_path_mapping, stop_words):
    while True:
        print("\n1. Query the index")
        print("2. Insert a new document")
        print("3. Delete a document")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            phrase = input("Enter the phrase to query: ")
            result = excute_query_index(inverted_index, phrase)
            if result:
                print("Documents containing the phrase:")
                for doc_id in result.keys():
                   print(f"Document ID: {doc_id}, File Path: {doc_id_path_mapping[doc_id]}")

            else:
                print("No documents found.")

        elif choice == '2':
            new_doc_path = input("Enter the path of the new document: ")
            new_doc_id = max(doc_id_path_mapping.keys()) + 1 if doc_id_path_mapping else 1
            success = insert_document(new_doc_path, new_doc_id, inverted_index, doc_id_path_mapping, stop_words)
            if success:
                print(f"Document inserted successfully with ID: {new_doc_id}")
            else:
                print("Document already exists.")

        elif choice == '3':
            doc_to_delete = int(input("Enter the document ID to delete: "))
            success = delete_document(doc_to_delete, inverted_index, doc_id_path_mapping)
            if success:
                print(f"Document with ID {doc_to_delete} deleted successfully.")
            else:
                print(f"Document with ID {doc_to_delete} does not exist.")

        elif choice == '4':
            break

        else:
            print("Invalid choice. Please try again.")

def main():
    global stop_words, inverted_index_path, mapping_path
    
    folder_path =  input("Enter the folder path of your data: ") # ex: C:/Users/yasee/Desktop/data
    stop_words_path = input("Enter the path of your stop words file (The file uploaded with the solution): ")  # C:/Users/yasee/Desktop/data/stop_words.txt
    
    inverted_index_path = "pos_inverted_index.json"
    mapping_path = "docId_filePath_mapping.csv"

    stop_words = generate_stop_words(stop_words_path)

    existing_inverted_index, existing_mapping = genarate_inverted_index_and_mapping_as_files(inverted_index_path, mapping_path, folder_path, stop_words)

    menu(existing_inverted_index, existing_mapping, stop_words)

if __name__ == "__main__":
    main()
