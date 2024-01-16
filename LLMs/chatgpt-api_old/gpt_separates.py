import openai
import time
import os

# Read the API key from the file
with open("chatgpt_api_key.txt", "r") as file:
    openai.api_key = file.read().strip()

# Define the list of prompts
with open("prompts_test.txt") as f:
    prompts = f.read().splitlines()

context = f'You are a knowledgeable assistant. You are an expert on the Sustainable development goals, including how they are discussed in the annual report of the secretary-general titled "progress towards the sustainable development goals", and in speeches and reports from the United Nations. You are familiar with the work of the following organizations: UN DESA (and its divisions EAPD, DPIDG, DISD, DSDG, FSDO), UNDP, UNCTAD, and the five UN regional commissions. You will respond to the following prompt with a long response with as much detail as possible.'

# Define the delay between calls in seconds (adjust as needed)
delay = 2

# Define retry mode ("automatic" or "manual")
retry_mode = "automatic"  # Change to "manual" if needed

# Define SDG range
sdg_start = 1
sdg_end = 18  # This is exclusive, so it goes up to 17

# Check if SDG range is valid
if not (1 <= sdg_start <= 18) or not (1 <= sdg_end <= 18):
    print("Error: SDG range must be between 1 and 17")
    exit(1)

# Start the timer
start_time = time.time()

for sdg in range(sdg_start, sdg_end):
    print(f"Processing SDG {sdg}...")
    # Create a directory for this SDG
    sdg_dir = f"SDG_{sdg}"
    if not os.path.exists(sdg_dir):
        os.makedirs(sdg_dir)

    for i, prompt in enumerate(prompts, start=1):
        print(f"Processing prompt {i} of {len(prompts)}...")
        full_prompt = f"SDG {sdg}: {prompt}"
        # Create the messages list
        messages = [
            {
                "role": "system",
                "content": context,
            },
            {"role": "user", "content": full_prompt},
        ]

        # Add error handling for the API call
        while True:
            try:
                # Get a response from OpenAI's API
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    temperature=1.2,
                    messages=messages,
                )

                reply = response.choices[0].message.content

                # Write the response to an individual file
                response_filename = os.path.join(sdg_dir, f"d_{sdg}_{i}.txt")
                with open(response_filename, "w") as response_file:
                    response_file.write(f"{reply}\n\n\n")
                # If the API call succeeds, break out of the loop
                print(f"d_{i} for SDG {sdg} completed.")
                break

            except Exception as e:
                print(f"Error for prompt: {full_prompt}")
                print(f"Error message: {e}")
                # If an error occurs, decide what to do based on the retry mode
                if retry_mode == "automatic":
                    print(
                        "Automatic retry mode activated. Waiting for 5 minutes before retrying..."
                    )
                    time.sleep(300)  # 5 minutes wait
                    print("Retrying now...")
                else:
                    while True:
                        user_decision = input(
                            "An error occurred. Would you like to 'retry (r)' the prompt or 'stop (s)' the script? "
                        ).lower()
                        if user_decision == "r":
                            print("Retrying and resuming...")
                            break
                        elif user_decision == "s":
                            exit(0)  # This will stop the script
                        else:
                            print("Invalid input. Please type 'r' or 's'.")

            # Wait for a while before the next call
            time.sleep(delay)
    print(f"SDG {sdg} completed.")

# Stop the timer and calculate the elapsed time
end_time = time.time()
elapsed_time = (end_time - start_time) / 60
print(f"Total time elapsed: {elapsed_time} minutes")
print("The script has completed successfully.")
