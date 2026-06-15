def solution(S):
    max_words = 0
    sentence = []
    for c in S:
        if c in '.?!':
            max_words = max(max_words, count_words(''.join(sentence)))
            sentence = []
        else:
            sentence.append(c)
    max_words = max(max_words, count_words(''.join(sentence)))
    return max_words


def count_words(sentence):
    count = 0
    for word in sentence.split():
        if any(c.isalpha() for c in word):
            count += 1
    return count
