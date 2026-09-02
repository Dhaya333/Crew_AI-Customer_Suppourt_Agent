import sys
import os

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from customer_support.crew import CustomerSupportCrew


def run():
    """Kick off the customer support crew with a sample inquiry."""
    inputs = {
        "customer": "DeepLearningAI",
        "person": "Udhaya",
        "inquiry": (
            "I need help with setting up a Crew and kicking it off, "
            "specifically how can I add memory to my crew? "
            "Can you provide guidance?"
        ),
    }

    result = CustomerSupportCrew().crew().kickoff(inputs=inputs)
    print("\n\n========== FINAL RESPONSE ==========\n")
    print(result)


if __name__ == "__main__":
    run()
