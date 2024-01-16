import os
import time
import anthropic

# Read the API key from the file
with open("anthropic_api_key.txt", "r") as file:
    API_KEY = file.read().strip()

with open("prompts.txt") as f:
    prompts = f.read().splitlines()

context = f'You are a knowledgeable assistant. You are an expert on the Sustainable development goals, including how they are discussed in the annual report of the secretary-general titled "progress towards the sustainable development goals", and in speeches and reports from the United Nations. You are familiar with the work of the following organizations: UN DESA (and its divisions EAPD, DPIDG, DISD, DSDG, FSDO), UNDP, UNCTAD, and the five UN regional commissions. You will respond to the following prompt with a long response with as much detail as possible.'

# Define the delay between calls in seconds (adjust as needed)
delay = 2


def main(max_tokens_to_sample: int = 2000):
    c = anthropic.Client(api_key=API_KEY)

    start_time = time.time()

    for sdg in range(15, 18):
        filename = f"SDG_{sdg}.txt"
        print(f"Processing SDG {sdg}")
        with open(filename, "w") as f:
            for prompt in prompts:
                full_prompt = f"{anthropic.HUMAN_PROMPT} {context} SDG {sdg}: {prompt} {anthropic.AI_PROMPT}"
                try:
                    response = c.completion(
                        prompt=full_prompt,
                        stop_sequences=[anthropic.HUMAN_PROMPT],
                        model="claude-v1",
                        max_tokens_to_sample=max_tokens_to_sample,
                        temperature=1,
                    )
                    f.write(f"\n{response['completion']}\n\n")
                except:
                    print(f"Error for prompt: {full_prompt}")
                    break
                # Wait for a while before the next call
                time.sleep(delay)

    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    print(f"Total time elapsed: {elapsed_time} minutes")


if __name__ == "__main__":
    main()
