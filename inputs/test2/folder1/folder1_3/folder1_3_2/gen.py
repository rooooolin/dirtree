import os
import random
import string

def generate_random_file(file_size):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=file_size))
    file_name = f"random_file_{file_size}MB.txt"
    with open(file_name, 'w') as file:
        file.write(random_string)

file_size = 1024 * 1024  # 1MB

generate_random_file(file_size)