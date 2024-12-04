import requests
import random
import json


def simulate_voting():
    """
    Simulate voting process with predefined sample data
    """
    # Load sample voting data
    with open('sample.json', 'r') as file:
        voting_data = json.load(file)

    successful_votes = voting_data['successful_votes']
    base_url = 'http://localhost:8000'  # Assuming local FastAPI server

    # Track voting results
    voting_results = {}

    # Simulate voting for each sample voter
    for voter in successful_votes:
        try:
            response = requests.post(
                f'{base_url}/vote',
                json={
                    'voter_id': voter['voter_id'],
                    'party_name': voter['party']
                }
            )

            if response.status_code == 200:
                print(f"✅ Vote successful for {voter['voter_details']['name']} from {voter['voter_details']['state']}")

                # Track party votes
                party = voter['party']
                voting_results[party] = voting_results.get(party, 0) + 1
            else:
                print(f"❌ Vote failed for {voter['voter_details']['name']}")

        except requests.exceptions.RequestException as e:
            print(f"Error submitting vote: {e}")

    # Fetch and display final results
    try:
        results_response = requests.get(f'{base_url}/results')
        if results_response.status_code == 200:
            final_results = results_response.json()
            print("\n🗳️ Final Election Results 🗳️")
            for party, votes in final_results.items():
                print(f"{party}: {votes} votes")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching results: {e}")


if __name__ == '__main__':
    simulate_voting()