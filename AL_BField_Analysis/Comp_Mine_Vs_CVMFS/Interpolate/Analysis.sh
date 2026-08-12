#!/bin/bash
clear
# Function to display countdown
function countdown() {
    local count=3
    while [ $count -gt 0 ]; do
        echo -n "$count "
        sleep 1
        ((count--))
    done
    echo "Exiting the script..."
    sleep 0.5
    clear
}

# Function to handle folder selection
function select_folder() {
    echo "Which of the following do you want to run?"
    echo "------------------------------------------"
    for (( i=0; i<"${#folders[@]}"; i++ )); do
        echo "$((i+1)). ${folders[i]}"
    done

    while true; do
        echo "---------------------------------------------------------------"
        read -p "Enter the option number, 'q' for quick exit, or 'exit' to quit: " input
        if [[ "$input" = "exit" ]]; then
            countdown
            return 1
        elif [[ "$input" = "q" || "$input" = "Q" ]]; then
            clear
            echo "Quick exit. Bye!"
            # clear
            return 1
        elif [[ "$input" =~ ^[0-9]+$ ]]; then
            num_input=$((input))
            if ((num_input >= 1 && num_input <= "${#folders[@]}")); then
                selected_folder="${folders[$((num_input-1))]}"
                echo "You selected: $selected_folder"
                folder_path="$directory/$selected_folder"
                file_path="$folder_path/$selected_folder.sh"
                if [ -f "$file_path" ]; then
                    echo "Sourcing file: $file_path"
                    source "$file_path"
                else
                    echo "File not found: $file_path"
                fi
                return 0
            else
                echo "Invalid option. Please enter a valid number."
            fi
        else
            echo "Invalid input. Please enter a valid number, 'q' for quick exit, or 'exit' to quit."
        fi
    done
}

function sel_fol() {
    directory="$1"
    folders=()

    while IFS= read -r -d '' folder; do
        folder_name=$(basename "$folder")
        folders+=("$folder_name")
    done < <(find "$directory" -mindepth 1 -maxdepth 1 -type d -print0)

    if [ "${#folders[@]}" -eq 0 ]; then
        echo "No folders found in the directory: $directory"
        # exit 1
    fi

    select_folder
}

read -p "What directory are you using? " directory
sel_fol "$directory"