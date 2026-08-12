import os
import sys
import time
import subprocess

def countdown():
    count = 3
    while count > 0:
        print(f"{count} ", end='', flush=True)
        time.sleep(1)
        count -= 1
    print("Exiting the script...")
    time.sleep(0.5)
    os.system('clear')

def navigate(directory):
    while True:
        entries = sorted(os.listdir(directory))
        folders = [e for e in entries if os.path.isdir(os.path.join(directory, e))]
        files   = [e for e in entries if os.path.isfile(os.path.join(directory, e)) and e.endswith('.txt')]
        items   = folders + files

        if not items:
            print(f"No folders or files found in: {directory}")
            return

        print(f"\nCurrent directory: {directory}")
        print("------------------------------------------")
        for i, item in enumerate(items):
            tag = "[DIR] " if os.path.isdir(os.path.join(directory, item)) else "[FILE]"
            print(f"{i+1}. {tag} {item}")

        print("---------------------------------------------------------------")
        user_input = input("Enter the option number, 'q' for quick exit, or 'exit' to quit: ").strip()

        if user_input == 'exit':
            countdown()
            return
        elif user_input.lower() == 'q':
            os.system('clear')
            print("Quick exit. Bye!")
            return
        elif user_input.isdigit():
            num_input = int(user_input)
            if 1 <= num_input <= len(items):
                selected_path = os.path.join(directory, items[num_input - 1])
                if os.path.isdir(selected_path):
                    directory = selected_path  # go deeper
                else:
                    print(f"Running: {selected_path}")
                    return selected_path
            else:
                print("Invalid option. Please enter a valid number.")
        else:
            print("Invalid input. Please enter a valid number, 'q' for quick exit, or 'exit' to quit.")

os.system('clear')
directory = input("What directory are you using? ").strip()
if not os.path.isdir(directory):
    print(f"Directory not found: {directory}")
else:
    df = navigate(directory)
    df_name = os.path.splitext(os.path.basename(df))[0]
    print(df_name)
    

# df = navigate(directory)

# print(df)