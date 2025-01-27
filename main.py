from tree_sitter import Language, Parser
import os

# Load the shared language library
LANGUAGE_LIB = 'languages/language.so'

# Supported languages
LANGUAGES = {
    'c': Language(LANGUAGE_LIB, 'c'),
    'python': Language(LANGUAGE_LIB, 'python'),
    'javascript': Language(LANGUAGE_LIB, 'javascript'),
    'java': Language(LANGUAGE_LIB, 'java'),
    'go': Language(LANGUAGE_LIB, 'go'),
}

# Initialize parsers
PARSERS = {lang: Parser() for lang in LANGUAGES}
for lang, parser in PARSERS.items():
    parser.set_language(LANGUAGES[lang])


# Extract metadata from the AST
def extract_metadata(node, source_code):
    metadata = []
    if node.type in {'function_definition', 'method_declaration'}:
        func_name = None
        params = []
        return_type = None

        for child in node.children:
            if child.type == 'identifier':
                func_name = source_code[child.start_byte:child.end_byte].decode()
            elif child.type == 'parameter_list':
                params = [
                    source_code[param.start_byte:param.end_byte].decode()
                    for param in child.children
                ]
            elif child.type == 'type_identifier':
                return_type = source_code[child.start_byte:child.end_byte].decode()

        metadata.append({
            'function_name': func_name,
            'return_type': return_type,
            'parameters': params,
        })

    for child in node.children:
        metadata.extend(extract_metadata(child, source_code))

    return metadata


# Analyze a single file
def analyze_file(filepath, language):
    with open(filepath, 'rb') as f:
        code = f.read()

    tree = PARSERS[language].parse(code)
    metadata = extract_metadata(tree.root_node, code)
    return metadata


# Run tests
def run_tests():
    test_dir = 'test_code'
    results = {}

    for filename in os.listdir(test_dir):
        if not filename.endswith(('.c', '.py', '.js', '.java', '.go')):
            continue

        filepath = os.path.join(test_dir, filename)
        lang = filename.split('_')[0]
        metadata = analyze_file(filepath, lang)
        results[filename] = metadata

    return results


if __name__ == '__main__':
    results = run_tests()
    for filename, metadata in results.items():
        print(f"File: {filename}")
        for func in metadata:
            print("  Function Name:", func['function_name'])
            print("  Return Type:", func['return_type'])
            print("  Parameters:", func['parameters'])
        print("---")
