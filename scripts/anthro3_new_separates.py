from anthropic import Anthropic
import time
import os
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(
    description="Process SDGs using Anthropic Claude 3 API"
)
parser.add_argument("--sdg", type=int, help="Single SDG number to process")
parser.add_argument("--sdg_start", type=int, help="Start of SDG range")
parser.add_argument("--sdg_end", type=int, help="End of SDG range (exclusive)")
parser.add_argument("--prompts", type=str, help="Path to the prompt file")
parser.add_argument(
    "--model",
    type=str,
    default="claude-3-opus-20240229",
    choices=[
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    help="Anthropic Claude 3 model to use",
)
args = parser.parse_args()

# Validate and set SDG range
if args.sdg:
    if not 1 <= args.sdg <= 17:
        print("Error: SDG must be between 1 and 17")
        parser.print_help()
        exit(1)
    sdg_start = args.sdg
    sdg_end = args.sdg + 1
elif args.sdg_start and args.sdg_end:
    if not 1 <= args.sdg_start <= 17 or not 1 <= args.sdg_end <= 18:
        print("Error: SDG range must be between 1 and 17")
        parser.print_help()
        exit(1)
    sdg_start = args.sdg_start
    sdg_end = args.sdg_end + 1
else:
    print("Error: Please specify either a single SDG or a range of SDGs")
    parser.print_help()
    exit(1)

# Read the API key from the file
with open("anthropic_api_key.txt", "r") as file:
    api_key = file.read().strip()

# Create the Anthropic client object with the API key
client = Anthropic(api_key=api_key)

if not args.prompts:
    print("Error: Please specify a prompt file using the --prompts")
    parser.print_help()
    exit(1)

prompt_file_path = args.prompts

# Define the list of prompts
with open(prompt_file_path) as f:
    prompts = [line.strip() for line in f.readlines() if line.strip()]

# Context for the prompts
context = "You are a highly knowledgeable assistant with expertise in the Sustainable Development Goals (SDGs). Your task is to generate a detailed, comprehensive response to the following prompt. Your response should consist of a flowing narrative in english that avoids section headings or preliminary explanations, focusing instead on delivering substantive, relevant, and insightful content. The response must align with the depth of expertise expected for the topic, incorporating appropriate terminology, technical jargon, and comparative analysis as needed. Use illustrative examples where relevant to enhance clarity and engagement. Tailor the content to the intended audience, ensuring it is innovative, compelling, and contextually nuanced. Avoid unnecessary or irrelevant information, and ensure the narrative is cohesive and thought-provoking."

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
        full_prompt = f"{context} SDG {sdg}: {prompt}"
        print(f"prompt: {full_prompt}")

        while True:
            try:
                # Get a response from Anthropic's API
                response = client.messages.create(
                    model=args.model,
                    max_tokens=4000,
                    temperature=1.0,
                    messages=[{"role": "user", "content": full_prompt}],
                )

                # Extract the text from the response
                reply = response.content[0].text

                # Write the response to an individual file
                response_filename = os.path.join(sdg_dir, f"d_{sdg}_{i}.txt")
                with open(response_filename, "w", encoding="utf-8") as response_file:
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
