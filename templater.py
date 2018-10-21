"""
Original code from (rewritten from C to Cython):
    author='Adrian Holovaty',
    author_email='adrian@holovaty.com',
    http://templatemaker.googlecode.com/
longest_match() and longest_match_shifter()
 Returns the length of the longest common substring (LCS) in the strings
 a and b.
 Sets a_offset to the index of a where the LCS begins.
 Sets b_offset to the index of b where the LCS begins.
 If there is NO common substring, it returns 0 and sets both
 a_offset and b_offset to -1.
 The strings do not have to be equal length.
 The algorithm works by comparing one character at a time and "shifting" the
 strings so that different characters are compared. For example, given
 a="ABC" and b="DEF", picture these alignments:
                     (Shift a to the right)
    -------------------------------------------------------
    a             |  ABC            ABC             ABC
    b             |  DEF           DEF            DEF
    shift index   |  0             1              2
    possible LCS  |  3             2              1
    comparisons   |  AD, BE, CF    AE, BF         AF
                     (Shift b to the right)
    -------------------------------------------------------
                  |  ABC           ABC            ABC
                  |  DEF            DEF             DEF
    shift index   |  0             1              2
    possible LCS  |  3             2              1
    comparisons   |  AD, BE, CF    BD, CE         CD
 The algorithm short circuits based on the best_size found so far. For example,
 given a="ABC" and b="ABC", the first cycle of comparisons (AA, BB, CC) would
 result in a best_size=3. Because the algorithm starts with zero shift (i.e.,
 it starts with the highest possible LCS) and adds 1 to the shift index each
 time through, it can safely exit without doing any more comparisons.
 This algorithm is O^(m + m-1 + m-2 + ... + 1 + n + n-1 + n-2 + ... + 1), where
 m and n are the length of the two strings. Due to short circuiting, the
 algorithm could potentially finish after the very
 first set of comparisons. The algorithm is slowest when the LCS is smallest,
 and the algorithm is fastest when the LCS is biggest.
 longest_match_shifter() performs "one side" of the shift -- e.g., "Shift a to
 the right" in the above illustration. longest_match() simply calls
 longest_match_shifter() twice, flipping the strings.
"""


# a_offset and b_offset are relative to the *whole* string, not the substring
# (as defined by a_start and a_end).
# a_end and b_end are (the last index + 1).
def lcs(a, b):
    """
    Given two strings, determines the longest common substring and returns a
    tuple of (best_size, a_offset, b_offset).
    """
    def _shifter(a, b, best_size):
        nonlocal a_offset, b_offset
        for i in range(b_len):
            current_size = 0
            if best_size >= b_len - 1:
                # Short-circuit. See comment above.
                break

            for j, k in zip(range(i, b_len), range(a_len)):
                # k is index of a, j is index of b.
                if a[k] == b[j]:
                    current_size += 1
                    if current_size > best_size:
                        best_size = current_size
                        a_offset = k - current_size + 1
                        b_offset = j - current_size + 1
                else:
                    current_size = 0
        return best_size

    a_len = len(a)
    b_len = len(b)
    a_offset = -1
    b_offset = -1
    best_size = 0
    best_size = _shifter(a, b, best_size)
    best_size = _shifter(b, a, best_size)
    return best_size, a_offset, b_offset


class Templater(object):

    def __init__(self, template=None, marker='|||', min_block_size=1):
        self._template = template
        self._min_block_size = min_block_size
        self._marker = marker
        self._headers = None
        self._named_markers = False

    def learn(self, new_text):
        if self._named_markers:
            raise NotImplementedError("Actually you can't learn in a template "
                                      "with named markers")
        if self._template is None:
            text = new_text
        else:
            text = b'\0\0\0'.join([
                x.encode()
                for x in self._template
                if x is not None
            ])
        self._template = [
            x if x is None else x.decode(errors='replace')
            for x in _create_template(new_text, text,
                                      (0, len(new_text)),
                                      (0, len(text)),
                                      self._min_block_size)
        ]


def _create_template(str_1, str_2, pos_1, pos_2, min_block_size=1):
    start_1, end_1 = pos_1
    start_2, end_2 = pos_2
    lcs_size, lcs_1_start, lcs_2_start = lcs(str_1[start_1:end_1],
                                             str_2[start_2:end_2])
    if lcs_size < min_block_size:
        return [None]
    else:
        return \
            _create_template(str_1, str_2,
                             (start_1, start_1 + lcs_1_start),
                             (start_2, start_2 + lcs_2_start),
                             min_block_size) + \
            [str_1[start_1 + lcs_1_start:start_1 + lcs_1_start + lcs_size]] + \
            _create_template(str_1, str_2,
                             (start_1 + lcs_1_start + lcs_size, end_1),
                             (start_2 + lcs_2_start + lcs_size, end_2),
                             min_block_size)
