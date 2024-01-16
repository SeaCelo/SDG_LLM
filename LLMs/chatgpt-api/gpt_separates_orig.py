from openai import OpenAI
import time
import os
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description="Process SDGs")
parser.add_argument("--sdg", type=int, help="Single SDG number to process")
parser.add_argument("--sdg_start", type=int, help="Start of SDG range")
parser.add_argument("--sdg_end", type=int, help="End of SDG range (exclusive)")
args = parser.parse_args()

# Validate and set SDG range
if args.sdg:
    if not 1 <= args.sdg <= 17:
        print("Error: SDG must be between 1 and 17")
        exit(1)
    sdg_start = args.sdg
    sdg_end = args.sdg + 1
elif args.sdg_start and args.sdg_end:
    if not 1 <= args.sdg_start <= 17 or not 1 <= args.sdg_end <= 18:
        print("Error: SDG range must be between 1 and 17")
        exit(1)
    sdg_start = args.sdg_start
    sdg_end = args.sdg_end
else:
    print("Error: Please specify either a single SDG or a range of SDGs")
    exit(1)


# Read the API key from the file
with open("chatgpt_api_key.txt", "r") as file:
    api_key = file.read().strip()

# Create the OpenAI client object with the API key
client = OpenAI(api_key=api_key)


# Define the list of prompts
with open("prompts_large.txt") as f:
    prompts = f.read().splitlines()

# context = f'You are a knowledgeable assistant. You are an expert on the Sustainable development goals, including how they are discussed in the annual report of the secretary-general titled "progress towards the sustainable development goals", and in speeches and reports from the United Nations. You are familiar with the work of the following organizations: UN DESA (and its divisions EAPD, DPIDG, DISD, DSDG, FSDO), UNDP, UNCTAD, and the five UN regional commissions. You will respond to the following prompt with a long response with as much detail as possible. Do not include section headings and focus instead on a flowing narrative without unnecessary and irrelevant information.'
# context = f"You are a knowledgeable assistant. You are an expert on the Sustainable development goals. You will respond to the following prompt with a long response with as much detail as possible. Do not include section headings and focus instead on a flowing narrative without unnecessary and irrelevant information. Do not include any preliminary explanation or preamble of the content. The content should be tailored in style and issues."
context = f"You are a knowledgeable assistant. You are an expert on the Sustainable development goals. You will respond to the following prompt with a long response with as much detail as possible. Do not include section headings and focus instead on a flowing narrative without unnecessary and irrelevant information. Do not include any preliminary explanation or preamble of the content, or an explanation of the style that will be used. The content should be tailored in style and issues. It should be innovative and interesting. Based on the prompt, it should match the appropriate depth of expertise, use of terms and jargon, areas of focus, use of comparative analysis, use of examples, and expected audience."


# Define the delay between calls in seconds (adjust as needed)
delay = 2

# Define retry mode ("automatic" or "manual")
retry_mode = "automatic"  # Change to "manual" if needed

# Start the timer
start_time = time.time()

for sdg in range(sdg_start, sdg_end):
    print(f"Processing SDG {sdg}...")
    # Create a directory for this SDG
    sdg_dir = f"results/SDG_{sdg}"
    if not os.path.exists(sdg_dir):
        os.makedirs(sdg_dir)

    for i, prompt in enumerate(prompts, start=1):
        print(f"Processing prompt {i} of {len(prompts)}...")
        full_prompt = f"SDG {sdg}: {prompt}"
        print(f"prompt: {full_prompt}")

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
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo", temperature=1.2, messages=messages
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
