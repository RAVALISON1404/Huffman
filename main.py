import pickle
from collections import Counter


class Tree:
    def __init__(self, _value, _letter):
        self.left_predecessor = None
        self.right_predecessor = None
        self.successor = None
        self.binary = ''
        self.value = _value
        self.letter = _letter

    def has_left_predecessor(self):
        return self.left_predecessor is not None

    def has_right_predecessor(self):
        return self.right_predecessor is not None


def initialize_tree(_dict):
    _trees = []
    for key in _dict.keys():
        _trees.append(Tree(_dict[key], key))
    return _trees


def setbinary(node):
    if node is None:
        return
    if node.has_left_predecessor():
        node.left_predecessor.binary = node.binary + '0'
        setbinary(node.left_predecessor)
    if node.has_right_predecessor():
        node.right_predecessor.binary = node.binary + '1'
        setbinary(node.right_predecessor)


def print_tree(node, indent=''):
    if node is None:
        return
    print(indent + str(node.value) + ' ' + node.letter)
    print_tree(node.left_predecessor, indent + '  ')
    print_tree(node.right_predecessor, indent + '  ')


def code(trees):
    if len(trees) > 1:
        trees.sort(key=lambda x: x.value)
        tree_l = trees[0]
        tree_r = trees[1]
        _value = tree_l.value + tree_r.value
        _letter = tree_l.letter + tree_r.letter
        new_tree = Tree(_value, _letter)
        new_tree.left_predecessor = tree_l
        new_tree.right_predecessor = tree_r
        tree_l.successor = new_tree
        tree_r.successor = new_tree
        trees[1] = new_tree
        trees.pop(0)
        return code(trees)
    setbinary(trees[0])
    return trees[0]


def collect_leaf(node, _leaf):
    if node is None:
        return
    if node.has_left_predecessor():
        collect_leaf(node.left_predecessor, _leaf)
    if node.has_right_predecessor():
        collect_leaf(node.right_predecessor, _leaf)
    if not node.has_left_predecessor() and not node.has_right_predecessor():
        _leaf.append(node)


def calculate_letter_probabilities(_text):
    letter_counts = Counter(_text)
    total_letters = sum(letter_counts.values())
    letter_probabilities = {_letter: count / total_letters for _letter, count in letter_counts.items()}
    return letter_probabilities


def encode(_text, array):
    trees = initialize_tree(array)
    huffman_tree = code(trees)
    print_tree(huffman_tree)
    leaf = []
    collect_leaf(huffman_tree, leaf)
    for item in leaf:
        print(f'Letter: {item.letter} - Binary: {item.binary}')
    binary = ''
    for letter in _text:
        for item in leaf:
            if item.letter == letter:
                binary += item.binary
    return binary


def binarystring_to_bytes(binary):
    initial = len(binary)
    if len(binary) % 8 != 0:
        binary = binary.zfill((len(binary) // 8 + 1) * 8)
    bytes_list = []
    initial = len(binary) - initial
    for i in range(0, len(binary), 8):
        byte = int(binary[i:i + 8], 2)
        bytes_list.append(byte)
    return initial, bytes(bytes_list)


def bytes_to_binary(_bytes):
    encoded_text = _bytes.decode('latin1')
    encoded_text = ''.join(format(ord(char), '08b') for char in encoded_text)
    return encoded_text


def decode(binary, _dict):
    trees = initialize_tree(_dict)
    huffman_tree = code(trees)
    decoded_text = ''
    current_node = huffman_tree
    for bit in binary:
        if bit == '0' or bit == 48:
            current_node = current_node.left_predecessor
        elif bit == '1' or bit == 49:
            current_node = current_node.right_predecessor
        if not current_node.has_left_predecessor() and not current_node.has_right_predecessor():
            decoded_text += current_node.letter
            current_node = huffman_tree
    return decoded_text


def compress_file(file_path, output_path):
    with open(file_path, 'r') as file:
        content = file.read()
    _probabilities = calculate_letter_probabilities(content)
    encoded = encode(content, _probabilities)
    added, encoded = binarystring_to_bytes(encoded)
    with open('probabilities.dump', 'wb') as file:
        pickle.dump(_probabilities, file)
        pickle.dump(added, file)
    with open(output_path, 'wb') as file:
        file.write(encoded)
    print(f'Compressed file {file_path} saved to {output_path}')


def decompress_file(file_path, output_path):
    with open('probabilities.dump', 'rb') as file:
        probabilities = pickle.load(file)
        added = pickle.load(file)
    with open(file_path, 'rb') as file:
        encoded_text = file.read()
    _decoded_text = decode(bytes_to_binary(encoded_text)[added:], probabilities)
    with open(output_path, 'w') as file:
        file.write(_decoded_text)
    print(f'Decompressed file {file_path} saved to {output_path}')


if __name__ == '__main__':
    compress_file('input.txt', 'compressed.zip')
    decompress_file('compressed.zip', 'output.txt')
