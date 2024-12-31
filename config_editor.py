import json
import os

# Function to get the path of the config file (same directory as the script)
def get_config_file_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# Function to load the current configuration from the JSON file
def load_config():
    config_file_path = get_config_file_path()
    
    try:
        with open(config_file_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Config file not found. Creating a new one...")
        config = {
            "Settings": {
                "music_directory": "",
                "weather_api_key": "",
                "ai_model": ""
            }
        }
        save_config(config)  # Save default config if the file doesn't exist
    return config

# Function to save the configuration to the JSON file
def save_config(config):
    config_file_path = get_config_file_path()
    
    with open(config_file_path, 'w') as f:
        json.dump(config, f, indent=4)

# Function to edit the configuration
def edit_config():
    # Load current config
    config = load_config()

    # Prompt user for inputs and update the config dictionary
    print("Edit Configuration")
    model_name = input(f"Current AI model is '{config['Settings']['ai_model']}'. Enter new model name: ")
    if model_name:
        config['Settings']['ai_model'] = model_name

    music_directory = input(f"Current music directory is '{config['Settings']['music_directory']}'. Enter new music directory: ")
    if music_directory:
        config['Settings']['music_directory'] = music_directory

    weather_api_key = input(f"Current weather API key is '{config['Settings']['weather_api_key']}'. Enter new weather API key: ")
    if weather_api_key:
        config['Settings']['weather_api_key'] = weather_api_key

    # Save the updated config to the JSON file
    save_config(config)

    print("\nConfiguration updated successfully!")

# Main function to run the program
def main():
    
        # Ask if the user wants to edit the config
        print("\nWelcome to the Config Editor!")
        edit_choice = input("Do you want to edit the configuration? \n [1] Yes \n [2] No \n >>>  ").strip().lower()

        if edit_choice.lower() == '1' or "yes":
            edit_config()
        elif edit_choice.lower() == '2' or "no" :
            exit(code= "Shutting down the Config Editor.")
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

if __name__ == "__main__":
    main()
