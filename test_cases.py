import random
import string

random.seed(42)


def write_case(handle, label, text, pattern) -> None:
    handle.write(f"=== {label}: text ===\n")
    handle.write(text + "\n")
    handle.write(f"=== {label}: pattern ===\n")
    handle.write(pattern + "\n")


generic_cases = [
    ("Generic 1", "hello world", "world"),
    ("Generic 2", "abcdefg", "xyz"),
    ("Generic 3", "abracadabra abracadabra", "abra"),
    ("Generic 4", "aaaaa", "aa"),
    ("Generic 5", "start middle end", "end"),
    ("Generic 6", "Case Sensitive case sensitive", "case"),
    ("Generic 7", "one, two; three.\nnew line here", "two; three"),
    ("Generic 8", "short", "longerpattern"),
]

text1 = "".join(random.choices(string.ascii_letters + string.digits, k=1_000_000))
pattern1 = "xQ7mK9pL2nR8vT4wY6"

text2 = "the quick brown fox jumps over the lazy dog " * 22728
pattern2 = "cryptographic hash function verification process"

text3 = (bytes(range(256)) * 4000).decode("latin-1")
pattern3 = "\xfa\xfb\xfc\xfd\xfe\xff\x01\x02\x03\x04"

text4 = "a" * 1_000_000
pattern4 = "z" * 20 + "b"

text5 = "".join(random.choices("ACGT", k=1_000_000))
pattern5 = "ACGTACGTACGTACGTACGT" * 3

with open("bmh_test_values.txt", "w", encoding="latin-1") as f:
    for label, text, pattern in generic_cases:
        write_case(f, label, text, pattern)

    write_case(f, "Case 1", text1, pattern1)
    write_case(f, "Case 2", text2, pattern2)
    write_case(f, "Case 3", text3, pattern3)
    write_case(f, "Case 4", text4, pattern4)
    write_case(f, "Case 5", text5, pattern5)

print("Saved to bmh_test_values.txt")
