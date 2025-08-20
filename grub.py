import curses
import sys

def main(stdscr):
    """
    This is the main function for the curses application.
    It creates a text-based GUI with an on-screen keyboard
    navigable by arrow keys, for password entry.
    """
    # Clear the screen
    stdscr.clear()

    # Hide the physical cursor
    curses.curs_set(0)

    # Enable function keys like arrow keys
    stdscr.keypad(True)

    # Define the keyboard layout as a list of lists for easy rendering
    # This layout mimics the one from your GRUB script
    keys_layout = [
        ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "DEL", "ESC"],
        ["TAB", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\", "CAPS"],
        ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "ENTER"],
        ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"],
        ["CTRL", "ALT", "SPACE", "BACK"]
    ]

    # Dimensions for the keyboard layout
    key_pad_y, key_pad_x = 5, 5

    # Cursor position for navigating the on-screen keyboard
    cursor_x = 0
    cursor_y = 0

    password = ""
    caps_lock_on = False

    while True:
        stdscr.clear()
        sh, sw = stdscr.getmaxyx()

        # Display the message
        message_text = "Please enter your password:"
        stdscr.addstr(sh // 2 - 10, sw // 2 - len(message_text) // 2, message_text)

        # Display the password as asterisks
        password_display = "*" * len(password)
        stdscr.addstr(sh // 2 - 8, sw // 2 - len(password_display) // 2, password_display)

        # --- Render the on-screen keyboard ---
        for row_index, row in enumerate(keys_layout):
            col_x = key_pad_x
            for col_index, key in enumerate(row):
                # Check for CAPS lock and convert to uppercase if needed
                if caps_lock_on and len(key) == 1 and key.isalpha():
                    key_display = key.upper()
                else:
                    key_display = key

                # Highlight the selected key with the cursor
                if row_index == cursor_y and col_index == cursor_x:
                    # Highlight the CAPS key differently to indicate it is "on"
                    if key == "CAPS" and caps_lock_on:
                        stdscr.addstr(key_pad_y + row_index, col_x, f" *{key_display}* ", curses.A_STANDOUT | curses.A_REVERSE)
                    else:
                        stdscr.addstr(key_pad_y + row_index, col_x, f" *{key_display}* ", curses.A_REVERSE)
                else:
                    # Render the CAPS key differently to indicate it is "on"
                    if key == "CAPS" and caps_lock_on:
                        stdscr.addstr(key_pad_y + row_index, col_x, f" {key_display} ", curses.A_STANDOUT)
                    else:
                        stdscr.addstr(key_pad_y + row_index, col_x, f" {key_display} ")

                # Adjust column position for the next key
                # This needs to be adjusted because the '*' adds 2 characters to the length
                col_x += len(key_display) + 3 if not (row_index == cursor_y and col_index == cursor_x) else len(key_display) + 5

        stdscr.refresh()

        # Get a single character from the user (arrow key input)
        key = stdscr.getch()

        # Handle keyboard navigation and selection
        if key == curses.KEY_UP:
            cursor_y = max(0, cursor_y - 1)
        elif key == curses.KEY_DOWN:
            cursor_y = min(len(keys_layout) - 1, cursor_y + 1)
        elif key == curses.KEY_LEFT:
            cursor_x = max(0, cursor_x - 1)
        elif key == curses.KEY_RIGHT:
            cursor_x = min(len(keys_layout[cursor_y]) - 1, cursor_x + 1)
        elif key in (10, curses.KEY_ENTER):
            selected_key = keys_layout[cursor_y][cursor_x]
            if selected_key == "ENTER":
                break  # Exit the loop to save the file
            elif selected_key == "DEL":
                password = password[:-1]
            elif selected_key == "CAPS":
                caps_lock_on = not caps_lock_on
            elif selected_key == "SPACE":
                password += " "
            elif selected_key == "BACK":
                 # This key doesn't seem to be mapped in the original, but it's here
                 # to show how to handle special keys.
                pass
            else:
                # Append the selected character to the password string
                if caps_lock_on and len(selected_key) == 1 and selected_key.isalpha():
                    password += selected_key.upper()
                else:
                    password += selected_key

    # --- After the loop: save the password to a file ---

    file_path = "temp_password.txt"
    try:
        with open(file_path, "w") as f:
            f.write(password)

        stdscr.clear()
        success_message = f"Password saved to {file_path}. Exiting."
        stdscr.addstr(sh // 2, sw // 2 - len(success_message) // 2, success_message)
        stdscr.refresh()
        stdscr.getch() # Wait for a final key press before exiting
    except Exception as e:
        stdscr.clear()
        error_message = f"An error occurred: {e}"
        stdscr.addstr(sh // 2, sw // 2 - len(error_message) // 2, error_message)
        stdscr.refresh()
        stdscr.getch() # Wait for a final key press before exiting

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except curses.error as e:
        print(f"Error: Curses failed to initialize. Please ensure your terminal is large enough.\nDetails: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
