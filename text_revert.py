import re



# Get line number from character index
def get_line_number(text, index):
    return text.count("\n", 0, index) + 1



# Show matches with context and return chosen occurrence
def choose_occurrence_with_context(text, pattern):
    matches = list(re.finditer(pattern, text))

    if not matches:
        print("No matches found.")
        return None

    CONTEXT = 60
    print("\nFound the following matches:\n")

    for i, m in enumerate(matches, start=1):
        start, end = m.start(), m.end()
        line_no = get_line_number(text, start)

        context_start = max(0, start - CONTEXT)
        context_end = min(len(text), end + CONTEXT)

        preview = text[context_start:context_end].replace("\n", " ")
        print(f"[{i}] Line {line_no}: ...{preview}...")

    choice = int(input("\nChoose which occurrence to edit: "))
    if choice < 1 or choice > len(matches):
        print("Invalid choice.")
        return None

    return choice


# Function to make Edits
def apply_command(text, command):
    pattern = command["pattern"]
    occurrence = command["occurrence"]
    operation = command["operation"]
    replacement = command.get("replacement", "")

    matches = list(re.finditer(pattern, text))

    if occurrence <= 0 or occurrence > len(matches):
        return text

    match = matches[occurrence - 1]
    start, end = match.start(), match.end()
    matched_text = text[start:end]

    if operation == "replace":
        new_text = replacement

    elif operation == "insert_after":
        new_text = matched_text + replacement

    elif operation == "insert_before":
        new_text = replacement + matched_text

    elif operation == "delete":
        new_text = ""

    else:
        return text

    return text[:start] + new_text + text[end:]


# Revert to Time T
def reconstruct_document_at_time(original_text, command_stack, target_time):
    current_text = original_text

    for command in command_stack:
        if command["timestamp"] > target_time:
            break
        current_text = apply_command(current_text, command)

    return current_text



# File Handling
def read_document(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_document(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)



def main():
    original_document = read_document("input.txt")
    current_document = original_document

    command_stack = []
    timestamp = 0

    print("\nDocument Loaded:\n")
    print(current_document)

    while True:
        print("\n==============================")
        print("1. Edit document")
        print("2. Revert to old state")
        print("3. Exit")
        print("==============================")

        choice = input("Enter choice: ").strip()

        # EDIT
        if choice == "1":
            print("\nChoose operation:")
            print("replace | insert_before | insert_after | delete")
            operation = input("Operation: ").strip()

            replacement = ""
            if operation in ["replace", "insert_before", "insert_after"]:
                pattern = input("Enter regex pattern to match: ").strip()

                occurrence = choose_occurrence_with_context(current_document, pattern)
                if occurrence is None:
                    continue
                
                print("Enter text (type END on a new line to finish):")
                lines = []
                while True:
                    line = input()
                    if line == "END":
                        break
                    lines.append(line)

                replacement = "\n".join(lines)
            else :
                print("Invalid Command")
                continue

            timestamp += 1

            command = {
                "operation": operation,
                "pattern": pattern,
                "occurrence": occurrence,
                "replacement": replacement,
                "timestamp": timestamp
            }

            command_stack.append(command)
            current_document = apply_command(current_document, command)

            print("\nUpdated Document:\n")
            print(current_document)

        # REVERT
        elif choice == "2":
            if not command_stack:
                print("No edits yet.")
                continue

            print(f"\nAvailable timestamps: 1 to {timestamp}")
            target_time = int(input("Enter timestamp to revert to: "))

            reverted = reconstruct_document_at_time(
                original_document,
                command_stack,
                target_time
            )

            print("\nReverted Document:\n")
            print(reverted)

            decision = input("\nContinue editing from this state? (y/n): ").lower()
            if decision == "y":
                current_document = reverted
                timestamp = target_time
                command_stack = [
                    cmd for cmd in command_stack if cmd["timestamp"] <= target_time
                ]

        # EXIT
        elif choice == "3":
            write_document("output.txt", current_document)
            print("\nFinal document saved to output.txt")
            print("Exiting.")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
