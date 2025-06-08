def get_sentence_at_index(lst, length, index):
    # Convert index to base-12 and map to characters
    sentence = []
    base = len(lst)  # Base-12 since there are 12 characters
    for _ in range(length):
        remainder = index % base
        sentence.append(lst[remainder])
        index //= base
    # Reverse the sentence since we computed from least to most significant digit
    return ' '.join(sentence[::-1])

# Input
lst = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
index = (2048**12) - 1
length = 12

# Get the sentence
sentence = get_sentence_at_index(lst, length, index)
print(sentence)
